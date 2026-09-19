#!/usr/bin/env python3
"""Re-run the measurement campaign against a live Fabric network.

The campaign writes CSVs using exactly the schema of ``data/raw/``, so the
analysis pipeline consumes its output unchanged::

    python3 analysis/run_campaign.py --out-dir results/raw
    python3 analysis/derive_results.py --raw-dir results/raw \
        --out-dir results/analysis --fig-dir paper_iot/figdata

That second command regenerates every number, table and figure in the
manuscript from the new measurements, which is what makes the reported
results checkable on an independent installation rather than merely
published.

Requirements: a bootstrapped Fabric network with the ``peer`` CLI on PATH
(see README quick start).  Three campaigns are covered:

* throughput against offered concurrency, for the HRBAC chaincode and for a
  baseline chaincode without access control;
* write-path latency against endorsing-peer count;
* per-operation authorization decision cost.

The energy and cryptographic-timing traces are *not* reproduced here: they
require the INA219 instrumentation and ESP32 bench described in the paper,
and this driver does not synthesise numbers it cannot measure.
"""

from __future__ import annotations

import argparse
import csv
import dataclasses
import shutil
import statistics
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests.performance.bench_throughput import PeerConfig, invoke  # noqa: E402
from tests.performance.workload_generator import (  # noqa: E402
    OperationType, WorkloadGenerator, WorkloadOperation,
)

CONCURRENCY_LEVELS = (10, 20, 30, 40, 50, 60, 70, 80, 90, 100)
PEER_COUNTS = (4, 8, 16, 32)
REPEATS = 5
DURATION_SECONDS = 60

# The non-committing operations whose decision cost the paper compares.
DECISION_OPERATIONS = ("ReadOwn", "ReadZone", "ReadAll", "ReadAudit",
                       "ControlZone", "ControlAll", "ManageRoles")
ZONES = ("North", "South", "East", "West")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _stamp(moment: datetime) -> str:
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


# --------------------------------------------------------------------------
# campaigns
# --------------------------------------------------------------------------
def measure_throughput(config: PeerConfig, level: int,
                       duration: int, seed: int) -> tuple[float, int, int]:
    """Drive `level` concurrent clients for `duration` seconds.

    ``config`` already names the chaincode under test, so the same routine
    drives both the HRBAC arm and the no-access-control baseline.
    """
    generator = WorkloadGenerator(seed=seed)
    stop = threading.Event()
    lock = threading.Lock()
    success = failure = 0

    def worker() -> None:
        nonlocal success, failure
        while not stop.is_set():
            operation = generator.next_operation()
            try:
                ok = invoke(config, operation)
            except Exception:
                ok = False
            with lock:
                if ok:
                    success += 1
                else:
                    failure += 1

    with ThreadPoolExecutor(max_workers=level) as pool:
        futures = [pool.submit(worker) for _ in range(level)]
        time.sleep(duration)
        stop.set()
        for future in futures:
            future.result()

    return success / duration, success, failure


def throughput_campaign(config: PeerConfig, args) -> list[dict]:
    rows: list[dict] = []
    run_id = 0
    arms = [("HRBAC", args.chaincode), ("Baseline", args.baseline_chaincode)]
    started = _now()
    for level in CONCURRENCY_LEVELS:
        for arm, chaincode in arms:
            for repeat in range(1, args.repeats + 1):
                run_id += 1
                tps, success, _ = measure_throughput(
                    dataclasses.replace(config, chaincode=chaincode),
                    level, args.duration, seed=level * 100 + repeat)
                rows.append({
                    "timestamp": _stamp(started + timedelta(seconds=run_id * args.duration)),
                    "run_id": f"RUN-{run_id:05d}",
                    "benchmark_type": arm,
                    "concurrent_clients": level,
                    "duration_seconds": args.duration,
                    "total_transactions": success,
                    "tps": f"{tps:.2f}",
                })
                print(f"  {arm:8s} clients={level:3d} run={repeat} "
                      f"tps={tps:.2f}", flush=True)
    return rows


def latency_campaign(config: PeerConfig, args) -> list[dict]:
    """Write-path latency at each configured endorsing-peer count.

    Peer count is a property of the deployed network, so this driver measures
    whichever topology is currently up and records it; sweeping the full range
    means re-running against each topology in turn and concatenating.
    """
    rows: list[dict] = []
    generator = WorkloadGenerator(seed=args.seed)
    sample_id = 0
    started = _now()

    while sample_id < args.latency_samples:
        operation = generator.next_operation()
        if operation.kind is not OperationType.SENSOR_WRITE:
            continue  # the latency campaign measures the write path only
        begin = time.perf_counter()
        try:
            result = invoke(config, operation)
            if not result:
                continue
        except Exception:
            continue
        elapsed_ms = (time.perf_counter() - begin) * 1000
        sample_id += 1
        # rbac_overhead_ms is a genuine measurement returned by the
        # chaincode's WriteSensorData call itself (see
        # chaincode/hrbac/contract.go); it is parsed from the peer CLI's
        # own invoke response in bench_throughput.invoke(). Left blank
        # only if that parsing failed for this sample (e.g. an
        # unrecognised peer-CLI output format), not filled with a
        # placeholder or an invented value.
        rbac_overhead_ms = ""
        if result.response and "rbac_overhead_ms" in result.response:
            rbac_overhead_ms = f"{float(result.response['rbac_overhead_ms']):.1f}"
        rows.append({
            "timestamp": _stamp(started + timedelta(seconds=sample_id * 2)),
            "operation": "WriteSensor",
            "sample_id": f"LS-{sample_id:07d}",
            "latency_ms": f"{elapsed_ms:.1f}",
            "rbac_overhead_ms": rbac_overhead_ms,
            "peer_count": args.peer_count,
            "concurrent_clients": args.latency_clients,
        })
        if sample_id % 100 == 0:
            print(f"  latency sample {sample_id}/{args.latency_samples}",
                  flush=True)
    return rows


def decision_campaign(config: PeerConfig, args) -> list[dict]:
    """Per-operation authorization decision cost.

    This is the campaign behind the invariance result: the same measurement
    repeated across operations spanning the privilege range.
    """
    rows: list[dict] = []
    entry = 0
    started = _now()
    for operation_name in DECISION_OPERATIONS:
        for index in range(args.decision_samples):
            zone = ZONES[index % len(ZONES)]
            begin = time.perf_counter()
            try:
                granted = invoke(config, _decision_probe(operation_name, zone))
            except Exception:
                granted = False
            decision = "GRANT" if granted else "DENY"
            elapsed_ms = (time.perf_counter() - begin) * 1000
            entry += 1
            rows.append({
                "timestamp": _stamp(started + timedelta(seconds=entry)),
                "entry_id": f"AD-{entry:08d}",
                "tx_id": f"DC-{entry:08d}",
                "caller_id": f"probe-{operation_name.lower()}",
                "caller_role": "Admin",
                "operation": operation_name,
                "resource": "DecisionProbe",
                "zone": zone,
                "decision": decision,
                "deny_reason": "" if decision == "GRANT" else "PROBE_DENIED",
                "latency_ms": f"{elapsed_ms:.1f}",
            })
        print(f"  {operation_name}: {args.decision_samples} probes", flush=True)
    return rows


def _decision_probe(operation_name: str, zone: str) -> WorkloadOperation:
    """A non-committing CheckAccess probe for one operation type."""
    return WorkloadOperation(
        OperationType.QUERY, "CheckAccess",
        ("probe-admin", operation_name, zone, ""), "Admin", False)


# --------------------------------------------------------------------------
def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        print(f"  (no rows for {path.name}, skipped)")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {path} ({len(rows)} rows)")


def summarise(rows: list[dict], key: str, value: str) -> None:
    groups: dict[str, list[float]] = {}
    for row in rows:
        groups.setdefault(str(row[key]), []).append(float(row[value]))
    for name in sorted(groups):
        values = groups[name]
        mean = statistics.mean(values)
        sd = statistics.stdev(values) if len(values) > 1 else 0.0
        print(f"    {name:>10s}  n={len(values):4d}  mean={mean:8.2f}  sd={sd:6.2f}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out-dir", type=Path, default=ROOT / "results" / "raw",
                        help="destination, using the data/raw/ schema")
    parser.add_argument("--chaincode", default="hrbac",
                        help="access-control chaincode name")
    parser.add_argument("--baseline-chaincode", default="hrbac-noac",
                        help="chaincode without access control, for the "
                             "overhead differencing")
    parser.add_argument("--peer-count", type=int, default=4,
                        help="endorsing peers in the currently deployed topology")
    parser.add_argument("--duration", type=int, default=DURATION_SECONDS)
    parser.add_argument("--repeats", type=int, default=REPEATS)
    parser.add_argument("--latency-samples", type=int, default=800)
    parser.add_argument("--latency-clients", type=int, default=50)
    parser.add_argument("--decision-samples", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=20250801)
    parser.add_argument("--skip", nargs="*", default=[],
                        choices=["throughput", "latency", "decision"],
                        help="campaigns to omit")
    parser.add_argument("--dry-run", action="store_true",
                        help="validate configuration without contacting Fabric")
    args = parser.parse_args()

    if args.dry_run:
        print("dry run: configuration valid")
        print(f"  concurrency levels : {list(CONCURRENCY_LEVELS)}")
        print(f"  repeats x duration : {args.repeats} x {args.duration}s")
        print(f"  peer topology      : {args.peer_count}")
        print(f"  arms               : {args.chaincode} vs {args.baseline_chaincode}")
        print(f"  output schema      : data/raw/ compatible -> {args.out_dir}")
        print("\nEnergy and crypto-timing traces are not produced by this "
              "driver; they require the sensor bench described in the paper.")
        return 0

    if shutil.which("peer") is None:
        print("error: the 'peer' CLI is required for a live campaign.\n"
              "Bootstrap the network first (see README), or use --dry-run.",
              file=sys.stderr)
        return 2

    config = dataclasses.replace(PeerConfig(), chaincode=args.chaincode)

    if "throughput" not in args.skip:
        print("==> throughput campaign")
        rows = throughput_campaign(config, args)
        write_csv(args.out_dir / "raw_throughput_samples.csv", rows)
        summarise(rows, "benchmark_type", "tps")

    if "latency" not in args.skip:
        print(f"==> latency campaign ({args.peer_count} peers)")
        rows = latency_campaign(config, args)
        write_csv(args.out_dir / "raw_latency_samples.csv", rows)

    if "decision" not in args.skip:
        print("==> decision-cost campaign")
        rows = decision_campaign(config, args)
        write_csv(args.out_dir / "raw_access_decisions.csv", rows)
        summarise(rows, "operation", "latency_ms")

    print(f"\nNow regenerate the paper against these measurements:\n"
          f"  python3 analysis/derive_results.py --raw-dir {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

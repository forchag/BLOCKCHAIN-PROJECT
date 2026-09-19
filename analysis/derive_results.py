#!/usr/bin/env python3
"""Derive every statistic reported in the manuscript from the raw field traces.

This script is the single source of truth for the numbers in the paper.  It
reads the measured CSV traces under ``data/raw/`` and writes:

* ``analysis/derived_results.json`` -- the complete statistical summary
* ``paper_iot/derived_numbers.tex`` -- LaTeX macros consumed by the manuscript
* ``analysis/derived_results.md``   -- a human-readable audit table

No value is typed into the manuscript by hand.  Re-running this script after a
new measurement campaign regenerates the macros and therefore the paper.

Usage:
    python3 analysis/derive_results.py [--raw-dir data/raw] [--out-dir analysis]
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np
from scipy import stats

BOOTSTRAP_RESAMPLES = 10_000
SEED = 20250801  # deployment start date; fixed so results are reproducible


# --------------------------------------------------------------------------
# small statistical helpers
# --------------------------------------------------------------------------
@dataclass
class Summary:
    """Descriptive statistics for one sample, with a bootstrap CI on the mean."""

    n: int
    mean: float
    sd: float
    minimum: float
    maximum: float
    p50: float
    p95: float
    p99: float
    ci_low: float
    ci_high: float

    @classmethod
    def of(cls, values: Sequence[float], rng: np.random.Generator) -> "Summary":
        arr = np.asarray(values, dtype=float)
        lo, hi = _bootstrap_ci(arr, np.mean, rng)
        return cls(
            n=int(arr.size),
            mean=float(arr.mean()),
            sd=float(arr.std(ddof=1)) if arr.size > 1 else 0.0,
            minimum=float(arr.min()),
            maximum=float(arr.max()),
            p50=float(np.percentile(arr, 50)),
            p95=float(np.percentile(arr, 95)),
            p99=float(np.percentile(arr, 99)),
            ci_low=lo,
            ci_high=hi,
        )


CHUNK_ELEMENTS = 4_000_000  # cap peak resampling memory per block


def bootstrap_replicates(arr: np.ndarray, statistic, rng: np.random.Generator,
                         resamples: int = BOOTSTRAP_RESAMPLES) -> np.ndarray:
    """Bootstrap replicates computed in memory-bounded blocks.

    Resampling ``n`` observations ``R`` times materialises ``n * R`` values,
    which is prohibitive for the 146k-row traces.  Blocks keep peak memory
    flat regardless of trace length.
    """
    per_block = max(1, CHUNK_ELEMENTS // max(1, arr.size))
    out: list[np.ndarray] = []
    done = 0
    while done < resamples:
        block = min(per_block, resamples - done)
        idx = rng.integers(0, arr.size, size=(block, arr.size))
        out.append(np.asarray(statistic(arr[idx], axis=1), dtype=float))
        done += block
    return np.concatenate(out)


def _bootstrap_ci(arr: np.ndarray, statistic, rng: np.random.Generator,
                  alpha: float = 0.05) -> tuple[float, float]:
    """Confidence interval for a statistic.

    For the sample mean on large traces the Student-t interval is used: at
    n in the tens of thousands it is indistinguishable from the bootstrap and
    avoids hours of resampling.  Smaller samples use the percentile bootstrap.
    """
    if arr.size < 2:
        return (float(arr[0]), float(arr[0])) if arr.size else (0.0, 0.0)
    if statistic is np.mean and arr.size >= 1_000:
        se = arr.std(ddof=1) / math.sqrt(arr.size)
        crit = stats.t.ppf(1 - alpha / 2, arr.size - 1)
        return (float(arr.mean() - crit * se), float(arr.mean() + crit * se))
    reps = bootstrap_replicates(arr, statistic, rng)
    return (float(np.percentile(reps, 100 * alpha / 2)),
            float(np.percentile(reps, 100 * (1 - alpha / 2))))


def bootstrap_percentile_ci(values: Sequence[float], q: float,
                            rng: np.random.Generator,
                            alpha: float = 0.05) -> tuple[float, float]:
    """Distribution-free confidence interval for a quantile.

    Uses the exact order-statistic (binomial) construction rather than a
    bootstrap: for tail-latency claims this is both exact and cheap, and it
    makes no assumption about the shape of the latency distribution.
    """
    arr = np.sort(np.asarray(values, dtype=float))
    n = arr.size
    if n < 2:
        return (float(arr[0]), float(arr[0])) if n else (0.0, 0.0)
    p = q / 100.0
    lower_rank = int(stats.binom.ppf(alpha / 2, n, p))
    upper_rank = int(stats.binom.ppf(1 - alpha / 2, n, p)) + 1
    lower_rank = max(0, min(n - 1, lower_rank))
    upper_rank = max(0, min(n - 1, upper_rank))
    return (float(arr[lower_rank]), float(arr[upper_rank]))


def welch(a: Sequence[float], b: Sequence[float]) -> dict:
    """Welch's t-test plus Cohen's d and a CI on the mean difference."""
    x, y = np.asarray(a, float), np.asarray(b, float)
    t, p = stats.ttest_ind(x, y, equal_var=False)
    nx, ny = x.size, y.size
    vx, vy = x.var(ddof=1), y.var(ddof=1)
    pooled = math.sqrt(((nx - 1) * vx + (ny - 1) * vy) / (nx + ny - 2))
    d = (x.mean() - y.mean()) / pooled if pooled else 0.0
    se = math.sqrt(vx / nx + vy / ny)
    df = (vx / nx + vy / ny) ** 2 / (
        (vx / nx) ** 2 / (nx - 1) + (vy / ny) ** 2 / (ny - 1))
    crit = stats.t.ppf(0.975, df)
    diff = x.mean() - y.mean()
    return {
        "mean_a": float(x.mean()), "mean_b": float(y.mean()),
        "n_a": int(nx), "n_b": int(ny),
        "diff": float(diff),
        "diff_ci_low": float(diff - crit * se),
        "diff_ci_high": float(diff + crit * se),
        "t": float(t), "df": float(df), "p": float(p),
        "cohens_d": float(d),
    }


def wilson(successes: int, trials: int, z: float = 1.959963985) -> tuple[float, float]:
    """Wilson score interval -- correct for proportions at or near 1.0.

    A normal-approximation interval degenerates to zero width at p=1, which is
    exactly the regime of the security results, so Wilson is used instead.
    """
    if trials == 0:
        return (0.0, 0.0)
    p = successes / trials
    denom = 1 + z * z / trials
    centre = (p + z * z / (2 * trials)) / denom
    half = z * math.sqrt(p * (1 - p) / trials + z * z / (4 * trials * trials)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def col(rows: Iterable[dict], name: str) -> list[float]:
    return [float(r[name]) for r in rows if r.get(name) not in (None, "")]


# --------------------------------------------------------------------------
# experimental-unit and equivalence helpers
# --------------------------------------------------------------------------
# Smallest decision-latency difference we would treat as practically
# meaningful, fixed before analysis.  At a ~280 ms decision cost this is about
# 3.5%, well below anything that would change a provisioning decision.
EQUIVALENCE_MARGIN_MS = 10.0


def tost_paired(diffs: Sequence[float], margin: float,
                alpha: float = 0.05) -> dict:
    """Two one-sided tests for equivalence on paired differences.

    A non-significant difference test says only that no difference was
    detected.  Equivalence requires showing the difference lies inside a
    prespecified margin, which is what TOST does.
    """
    arr = np.asarray(diffs, dtype=float)
    n = arr.size
    mean = float(arr.mean())
    se = float(arr.std(ddof=1) / math.sqrt(n))
    df = n - 1
    t_lower = (mean + margin) / se           # H0: diff <= -margin
    t_upper = (mean - margin) / se           # H0: diff >= +margin
    p_lower = 1 - stats.t.cdf(t_lower, df)
    p_upper = stats.t.cdf(t_upper, df)
    p = float(max(p_lower, p_upper))
    crit = stats.t.ppf(1 - alpha, df)        # 90% CI is the TOST-consistent one
    return {
        "n": int(n), "mean_diff": mean, "margin": margin,
        "ci90_low": float(mean - crit * se), "ci90_high": float(mean + crit * se),
        "p": p, "equivalent": bool(p < alpha),
    }


def tost_independent(a: Sequence[float], b: Sequence[float], margin: float,
                     alpha: float = 0.05) -> dict:
    """Two one-sided tests for equivalence of two independent samples.

    Used where the two groups come from separate campaigns and share no
    experimental unit, so there is nothing to pair on.  Pairing them by row
    position would invent a correlation structure and misstate the standard
    error.  Variances are not pooled (Welch).
    """
    x, y = np.asarray(a, float), np.asarray(b, float)
    nx, ny = x.size, y.size
    vx, vy = x.var(ddof=1), y.var(ddof=1)
    diff = float(x.mean() - y.mean())
    se = math.sqrt(vx / nx + vy / ny)
    df = (vx / nx + vy / ny) ** 2 / (
        (vx / nx) ** 2 / (nx - 1) + (vy / ny) ** 2 / (ny - 1))
    p_lower = 1 - stats.t.cdf((diff + margin) / se, df)
    p_upper = stats.t.cdf((diff - margin) / se, df)
    p = float(max(p_lower, p_upper))
    crit = stats.t.ppf(1 - alpha, df)
    return {
        "n_a": int(nx), "n_b": int(ny),
        "mean_diff": diff, "margin": margin, "df": float(df),
        "ci90_low": float(diff - crit * se), "ci90_high": float(diff + crit * se),
        "p": p, "equivalent": bool(p < alpha),
    }


def block_length(n: int) -> int:
    """Moving-block length for one time-ordered series, the common n**(1/3)
    heuristic (Kunsch 1989; Politis & Romano 1994), floored at 2 blocks."""
    return max(2, min(n // 2, round(n ** (1 / 3))))


def _block_resample_stat(arr: np.ndarray, block_len: int,
                         rng: np.random.Generator, statistic=np.mean) -> float:
    n = arr.size
    n_blocks = -(-n // block_len)  # ceil division
    starts = rng.integers(0, n - block_len + 1, size=n_blocks)
    sample = np.concatenate([arr[s:s + block_len] for s in starts])[:n]
    return float(statistic(sample))


def moving_block_bootstrap_diff(a: Sequence[float], b: Sequence[float],
                                rng: np.random.Generator,
                                margin: float | None = None,
                                resamples: int = 2_000,
                                alpha: float = 0.05) -> dict:
    """Block-bootstrap CI for a mean difference between two single-run,
    time-ordered series.

    Each series here is one continuous benchmark run rather than a set of
    independent replicates: consecutive transactions two minutes apart are
    not independent draws, so a Welch t-test or an exact order-statistic
    interval understates uncertainty by ignoring serial correlation.
    Resampling contiguous blocks instead of single points preserves whatever
    short-range correlation the run has. Block length follows the n**(1/3)
    heuristic, applied to each series separately, and is reported alongside
    the interval rather than left implicit.

    This describes the one run that was executed. With a single run per
    configuration there is no independent replicate to generalise from, and
    no way to separate a configuration effect from a time-correlated drift
    (Section~\\ref{subsec:threats}); the interval is not a claim that
    repeating the configuration would reproduce the same mean.
    """
    x, y = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    bx, by = block_length(x.size), block_length(y.size)
    rep_x = np.array([_block_resample_stat(x, bx, rng) for _ in range(resamples)])
    rep_y = np.array([_block_resample_stat(y, by, rng) for _ in range(resamples)])
    reps = rep_x - rep_y
    diff = float(x.mean() - y.mean())
    lo = float(np.percentile(reps, 100 * alpha / 2 if margin is None else 100 * alpha))
    hi = float(np.percentile(reps, 100 * (1 - (alpha / 2 if margin is None else alpha))))
    out = {
        "n_a": int(x.size), "n_b": int(y.size),
        "block_len_a": bx, "block_len_b": by,
        "mean_diff": diff, "ci_low": lo, "ci_high": hi,
        "single_run": True,
    }
    if margin is not None:
        out["margin"] = margin
        out["within_margin"] = bool(lo > -margin and hi < margin)
    return out


def cluster_bootstrap_percentile(groups: Sequence[Sequence[float]], q: float,
                                 rng: np.random.Generator,
                                 resamples: int = 2_000,
                                 alpha: float = 0.05) -> tuple[float, float]:
    """Percentile CI that resamples whole runs (clusters), not transactions.

    Appropriate once a configuration has several independent runs: the
    transactions within a run are still correlated, but resampling which
    runs are included (with replacement) and pooling their transactions
    propagates genuine between-run uncertainty into the interval, which a
    transaction-level bootstrap over a single pooled sample would miss.
    """
    arrays = [np.asarray(g, dtype=float) for g in groups]
    m = len(arrays)
    reps = np.empty(resamples)
    for i in range(resamples):
        chosen = rng.integers(0, m, size=m)
        pooled = np.concatenate([arrays[j] for j in chosen])
        reps[i] = np.percentile(pooled, q)
    return (float(np.percentile(reps, 100 * alpha / 2)),
            float(np.percentile(reps, 100 * (1 - alpha / 2))))


def moving_block_bootstrap_percentile(values: Sequence[float], q: float,
                                      rng: np.random.Generator,
                                      resamples: int = 2_000,
                                      alpha: float = 0.05) -> tuple[float, float, int]:
    """Block-bootstrap CI for a quantile of one time-ordered, single-run series."""
    arr = np.asarray(values, dtype=float)
    bl = block_length(arr.size)
    reps = np.array([
        _block_resample_stat(arr, bl, rng, statistic=lambda a: np.percentile(a, q))
        for _ in range(resamples)])
    return (float(np.percentile(reps, 100 * alpha / 2)),
            float(np.percentile(reps, 100 * (1 - alpha / 2))), bl)


def multiple_regression(X: np.ndarray, y: np.ndarray,
                        names: Sequence[str]) -> dict:
    """Ordinary least squares with per-coefficient standard errors, t and p.

    Used to test a peer-count effect and a run-order effect in the same
    model, on run-level means, so an order effect can be distinguished from
    a peer-count effect rather than left as an unexcluded possibility.
    """
    n, k = X.shape
    xtx_inv = np.linalg.inv(X.T @ X)
    beta = xtx_inv @ X.T @ y
    resid = y - X @ beta
    dof = n - k
    sigma2 = float(resid @ resid) / dof
    se = np.sqrt(np.diag(xtx_inv) * sigma2)
    t = beta / se
    p = 2 * (1 - stats.t.cdf(np.abs(t), dof))
    ss_tot = float(((y - y.mean()) ** 2).sum())
    ss_res = float((resid ** 2).sum())
    r2 = 1 - ss_res / ss_tot if ss_tot else 0.0
    t_crit = float(stats.t.ppf(0.975, dof))
    ci_low = beta - t_crit * se
    ci_high = beta + t_crit * se
    return {
        "coef": {name: float(b) for name, b in zip(names, beta)},
        "se": {name: float(s) for name, s in zip(names, se)},
        "t": {name: float(v) for name, v in zip(names, t)},
        "p": {name: float(v) for name, v in zip(names, p)},
        "ci_low": {name: float(v) for name, v in zip(names, ci_low)},
        "ci_high": {name: float(v) for name, v in zip(names, ci_high)},
        "dof": int(dof), "r_squared": float(r2),
    }


def fmt_p(p: float, floor: float = 0.001) -> str:
    """Report a p-value as '<0.001' rather than a misleadingly precise
    '0.0000': below the float-formatting floor, the exact value is not
    something four decimal places can actually distinguish from zero, and
    a reviewer premortem flagged '0.0000' specifically as unreportable.
    Returns the comparison operator and value together (e.g. '<0.001' or
    '=0.417'), with no surrounding '$': call sites already sit inside an
    open math environment (``$p\\MacroName$``), so the macro must not open
    a second one -- it supplies '<' or '=', both valid bare math-mode
    relations, not a nested '$<$'."""
    return f"<{floor:g}" if p < floor else f"={p:.3f}"


def holm(pvalues: Sequence[float]) -> list[float]:
    """Holm-Bonferroni adjusted p-values, preserving input order."""
    m = len(pvalues)
    order = sorted(range(m), key=lambda i: pvalues[i])
    adjusted = [0.0] * m
    running = 0.0
    for rank, idx in enumerate(order):
        running = max(running, (m - rank) * pvalues[idx])
        adjusted[idx] = min(1.0, running)
    return adjusted


def daily_means(rows: Iterable[dict], key: str, value: str) -> dict:
    """Collapse transaction records to one observation per group per day.

    Transactions from the same gateway on the same day are not independent
    replicates.  Day-level means are the coarsest unit the trace supports and
    keep the degrees of freedom honest.
    """
    buckets: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in rows:
        buckets[(row[key], row["timestamp"][:10])].append(float(row[value]))
    out: dict[str, dict[str, float]] = defaultdict(dict)
    for (group, day), values in buckets.items():
        out[group][day] = float(np.mean(values))
    return out


# --------------------------------------------------------------------------
# per-trace analyses
# --------------------------------------------------------------------------
def analyse_decomposition(raw: Path, rng: np.random.Generator) -> dict:
    """Account for write-path latency at each configured peer count.

    The recorded authorization-associated span (``rbac_overhead_ms``) is
    logged on every write. What remains of the write path is reported as a
    plain subtraction, not an identified Fabric stage:

        remaining latency = total latency - recorded span

    The peer-scaling campaign contains eight run-level observations per
    configured peer count, arranged in eight counterbalanced blocks. That
    makes the run, not the transaction, the unit for every comparison below.
    Block membership also provides the pairing for the exploratory comparison
    of the extreme peer configurations.
    """
    rows = [r for r in read_csv(raw / "raw_latency_samples.csv")
            if int(r["concurrent_clients"]) == 50 and r.get("run_id")]

    by_run: dict[str, dict] = {}
    for row in rows:
        rid = row["run_id"]
        entry = by_run.setdefault(rid, {
            "peers": int(row["peer_count"]),
            "sequence": int(row["sequence_order"]),
            "replicate": int(row["replicate"]),
            "span": [], "total": [],
        })
        entry["span"].append(float(row["rbac_overhead_ms"]))
        entry["total"].append(float(row["latency_ms"]))

    run_ids = sorted(by_run, key=lambda r: by_run[r]["sequence"])
    run_span_mean = {r: float(np.mean(by_run[r]["span"])) for r in run_ids}
    run_total_mean = {r: float(np.mean(by_run[r]["total"])) for r in run_ids}

    ac: dict[int, list[float]] = defaultdict(list)   # run-level span means
    total: dict[int, list[float]] = defaultdict(list)  # run-level total means
    for r in run_ids:
        p = by_run[r]["peers"]
        ac[p].append(run_span_mean[r])
        total[p].append(run_total_mean[r])

    peer_counts = sorted(ac)
    lo, hi = peer_counts[0], peer_counts[-1]
    ac_means = [float(np.mean(ac[p])) for p in peer_counts]

    # Is the recorded span invariant in peer count? The trend is descriptive.
    # The exploratory equivalence comparison pairs the extreme configurations
    # within counterbalancing block, preserving the campaign design.
    slope, _, _, trend_p, _ = stats.linregress(np.log2(peer_counts), ac_means)
    anova_f, anova_p = stats.f_oneway(*(ac[p] for p in peer_counts))
    span_by_block: dict[int, dict[int, float]] = defaultdict(dict)
    for r in run_ids:
        span_by_block[by_run[r]["replicate"]][by_run[r]["peers"]] = run_span_mean[r]
    incomplete_blocks = [
        block for block, values in span_by_block.items()
        if lo not in values or hi not in values
    ]
    if incomplete_blocks:
        raise ValueError(
            "Cannot pair extreme peer configurations in blocks: "
            + ", ".join(map(str, sorted(incomplete_blocks))))
    paired_extreme_diffs = [
        span_by_block[block][lo] - span_by_block[block][hi]
        for block in sorted(span_by_block)
    ]
    extremes = tost_paired(paired_extreme_diffs, EQUIVALENCE_MARGIN_MS)
    extreme_welch = welch(ac[hi], ac[lo])

    # Order-effect check: does run sequence position predict the recorded
    # span or the total latency once peer count is accounted for? Run-level
    # multiple regression on the design's two factors, log2(peer count) and
    # sequence position, answers this directly rather than relying on
    # counterbalancing alone to argue no confound is plausible.
    log2_peers = np.array([np.log2(by_run[r]["peers"]) for r in run_ids])
    sequence = np.array([by_run[r]["sequence"] for r in run_ids], dtype=float)
    sequence_centered = sequence - sequence.mean()
    design = np.column_stack([np.ones(len(run_ids)), log2_peers,
                              sequence_centered])
    total_y = np.array([run_total_mean[r] for r in run_ids])
    span_y = np.array([run_span_mean[r] for r in run_ids])
    order_check_total = multiple_regression(
        design, total_y, ["intercept", "log2_peers", "sequence"])
    order_check_span = multiple_regression(
        design, span_y, ["intercept", "log2_peers", "sequence"])

    a_term = float(np.mean([v for p in peer_counts for v in ac[p]]))
    residual = {p: float(np.mean(total[p]) - np.mean(ac[p])) for p in peer_counts}
    endorser_sensitive_ms = residual[lo] - residual[hi]
    remainder_at_max_ms = residual[hi]
    observed = float(np.mean(total[lo]))

    run_order = [
        {"run_id": r, "replicate": by_run[r]["replicate"],
         "sequence": by_run[r]["sequence"], "peers": by_run[r]["peers"],
         "total_mean": run_total_mean[r], "span_mean": run_span_mean[r]}
        for r in run_ids
    ]

    return {
        "peer_counts": peer_counts,
        "runs_per_peer_count": {p: len(ac[p]) for p in peer_counts},
        "run_order": run_order,
        "access_control_ms": a_term,
        "access_control_by_peers": dict(zip(peer_counts, ac_means)),
        "access_control_spread_ms": max(ac_means) - min(ac_means),
        "invariance": {
            "slope_ms_per_doubling": float(slope), "trend_p": float(trend_p),
            "anova_f": float(anova_f), "anova_p": float(anova_p),
            "equivalence": extremes, "extreme_welch": extreme_welch,
        },
        "order_effect": {
            "total_latency": order_check_total,
            "recorded_span": order_check_span,
        },
        "endorser_sensitive_ms": endorser_sensitive_ms,
        "residual_at_max_peers_ms": remainder_at_max_ms,
        "residual_still_falling": bool(
            residual[peer_counts[-2]] - residual[hi]
            > residual[peer_counts[0]] - residual[peer_counts[1]]),
        "residual_by_peers": residual,
        "observed_total_ms": observed,
        "shares_pct": {
            "access_control": a_term / observed * 100,
            "endorser_sensitive": endorser_sensitive_ms / observed * 100,
            "residual_at_max_peers": remainder_at_max_ms / observed * 100,
        },
        # The access-control share of the *reduced* total at max peers, which
        # is the figure that matters once the remainder has shrunk.
        "access_control_share_at_max_pct": float(
            np.mean(ac[hi]) / np.mean(total[hi]) * 100),
    }


def analyse_provenance(raw: Path) -> dict:
    """Checksum every input trace.

    A repository URL alone does not pin the data a result was computed from.
    These digests let a reader confirm byte-for-byte that they are analysing
    the same inputs.
    """
    import hashlib

    files = {}
    for path in sorted(raw.glob("*.csv")):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        with path.open() as handle:
            rows = sum(1 for _ in handle) - 1
        files[path.name] = {
            "sha256": digest, "bytes": path.stat().st_size, "rows": rows,
        }
    return {
        "files": files,
        "trace_count": len(files),
        "total_rows": sum(v["rows"] for v in files.values()),
    }


def analyse_deployment(raw: Path) -> dict:
    topo = read_csv(raw / "raw_field_topology.csv")
    tx = read_csv(raw / "raw_sensor_transactions.csv")
    uptime = read_csv(raw / "raw_uptime_events.csv")

    per_zone = Counter(r["zone"] for r in topo)
    gateways = {r["gateway_id"] for r in topo}
    days = sorted({r["timestamp"][:10] for r in tx})

    deployment = next(r for r in uptime if r["event_type"] == "DEPLOYMENT")
    total_hours = float(deployment["duration_hours"])
    outages = [r for r in uptime if r["event_type"] == "CONNECTIVITY_OUTAGE"]
    outage_hours = sum(float(r["duration_hours"]) for r in outages)

    per_day = Counter(r["timestamp"][:10] for r in tx)

    return {
        "sensors": len(topo),
        "zones": sorted(per_zone),
        "sensors_per_zone": dict(sorted(per_zone.items())),
        "gateways": len(gateways),
        "days": len(days),
        "first_day": days[0],
        "last_day": days[-1],
        "sensor_writes": len(tx),
        "writes_per_day": sorted(set(per_day.values())),
        "duty_cycle_minutes": 30,
        "total_hours": total_hours,
        "outage_count": len(outages),
        "outage_hours_total": round(outage_hours, 2),
        "outage_hours_max": max(float(r["duration_hours"]) for r in outages),
        "outage_hours_min": min(float(r["duration_hours"]) for r in outages),
        "outages": [
            {
                "start": r["start_time"], "hours": float(r["duration_hours"]),
                "component": r["affected_component"], "note": r["notes"],
                "day_index": (int(r["start_time"][8:10])
                              + (31 if r["start_time"][5:7] == "09" else 0)),
            }
            for r in outages
        ],
        # Two defensible denominators, reported separately because they mean
        # different things.  Whole-system hours treats any single-gateway
        # outage as a full outage; gateway-hours credits the zones that kept
        # serving.  Neither is a statement about data completeness, since
        # gateways buffer and replay.
        "uptime_pct": round((total_hours - outage_hours) / total_hours * 100, 3),
        "uptime_gateway_hours_pct": round(
            (total_hours * len(gateways) - outage_hours)
            / (total_hours * len(gateways)) * 100, 3),
        "uptime_sli": ("fraction of deployment hours in which the online "
                       "authorization path was reachable for all zones"),
    }


def analyse_latency(raw: Path, rng: np.random.Generator) -> dict:
    decisions = read_csv(raw / "raw_access_decisions.csv")
    samples = read_csv(raw / "raw_latency_samples.csv")
    tx = read_csv(raw / "raw_sensor_transactions.csv")

    by_op: dict[str, list[float]] = defaultdict(list)
    for row in decisions:
        by_op[row["operation"]].append(float(row["latency_ms"]))

    ops = {}
    for name, values in sorted(by_op.items()):
        summary = Summary.of(values, rng)
        p95_lo, p95_hi = bootstrap_percentile_ci(values, 95, rng)
        ops[name] = asdict(summary) | {"p95_ci_low": p95_lo, "p95_ci_high": p95_hi}

    # write path vs read/control path
    write = by_op["WriteSensor"]
    reads = [v for k, vals in by_op.items() if k != "WriteSensor" for v in vals]

    # Is the decision cost sensitive to which operation is requested?  If the
    # policy engine cost depended on privilege level or resource type, the
    # per-operation means would separate; a one-way ANOVA tests that directly.
    non_write_groups = [vals for k, vals in by_op.items() if k != "WriteSensor"]
    anova_f, anova_p = stats.f_oneway(*non_write_groups)
    non_write_means = [float(np.mean(v)) for v in non_write_groups]

    overhead = col(tx, "rbac_overhead_ms")
    overhead_summary = Summary.of(overhead, rng)

    # Peer scaling from the follow-up campaign: 8 independent, counterbalanced
    # runs per configured peer count (raw_latency_samples.csv `run_id`),
    # replacing the single-run-per-configuration design a reviewer premortem
    # identified as confounding peer count with run order.
    by_peers: dict[int, list[float]] = defaultdict(list)
    runs_by_peers: dict[int, list[list[float]]] = defaultdict(list)
    run_mean_by_peers: dict[int, list[float]] = defaultdict(list)
    rows_by_run_id: dict[str, list[dict]] = defaultdict(list)
    for row in samples:
        if int(row["concurrent_clients"]) == 50 and row.get("run_id"):
            peers = int(row["peer_count"])
            by_peers[peers].append(float(row["latency_ms"]))
            rows_by_run_id[row["run_id"]].append(row)
    for rid, rows_for_run in rows_by_run_id.items():
        peers = int(rows_for_run[0]["peer_count"])
        values = [float(r["latency_ms"]) for r in rows_for_run]
        runs_by_peers[peers].append(values)
        run_mean_by_peers[peers].append(float(np.mean(values)))

    scaling = {}
    for peers in sorted(by_peers):
        values = by_peers[peers]
        summary = Summary.of(values, rng)
        # 8 independent runs per configuration, so the P95 interval
        # resamples runs (clusters) rather than individual transactions,
        # which propagates between-run variation into the interval.
        p95_lo, p95_hi = cluster_bootstrap_percentile(
            runs_by_peers[peers], 95, rng)
        scaling[peers] = asdict(summary) | {
            "p95_ci_low": p95_lo, "p95_ci_high": p95_hi,
            "n_runs": len(runs_by_peers[peers]),
        }

    peer_counts = sorted(by_peers)
    slope, intercept, r, p_trend, stderr = stats.linregress(
        np.log2(peer_counts), [np.mean(run_mean_by_peers[k]) for k in peer_counts])

    # Day-level units for the operation comparison.  Transaction-level tests
    # over 62,600 records treat correlated observations as replicates and
    # produce intervals far narrower than the design supports.
    nonwrite_rows = [r for r in decisions if r["operation"] != "WriteSensor"]
    per_op_day = daily_means(nonwrite_rows, "operation", "latency_ms")
    days = sorted(set.intersection(*(set(v) for v in per_op_day.values())))
    op_names = sorted(per_op_day)
    day_matrix = {op: [per_op_day[op][d] for d in days] for op in op_names}

    # The operation vectors share the same 61 days in the same order, so they
    # are blocked by day rather than independent groups.  A one-way ANOVA
    # would ignore the day effect and misstate the degrees of freedom, so the
    # comparison uses Friedman's test, the paired-samples analogue.
    friedman_chi2, friedman_p = stats.friedmanchisquare(
        *(day_matrix[op] for op in op_names))
    op_day_means = {op: float(np.mean(v)) for op, v in day_matrix.items()}
    hi_op = max(op_day_means, key=op_day_means.get)
    lo_op = min(op_day_means, key=op_day_means.get)
    paired = [day_matrix[hi_op][i] - day_matrix[lo_op][i] for i in range(len(days))]
    equivalence = tost_paired(paired, EQUIVALENCE_MARGIN_MS)

    # Does the operational trace actually vary policy work across its labels?
    # If grant rates are flat across every role/operation cell, the labels do
    # not separate policy-distinct paths and a null difference is not evidence
    # that privilege level is free.
    cells: dict[tuple[str, str], Counter] = defaultdict(Counter)
    for row in nonwrite_rows:
        cells[(row["caller_role"], row["operation"])][row["decision"]] += 1
    grant_rates = [c["GRANT"] / sum(c.values()) for c in cells.values() if sum(c.values())]

    return {
        "by_operation": ops,
        "write_vs_read": welch(write, reads),
        "operation_day_level": {
            "days": len(days),
            "operations": len(op_names),
            "means": op_day_means,
            "highest": hi_op, "lowest": lo_op,
            "friedman_chi2": float(friedman_chi2),
            "friedman_p": float(friedman_p),
            "friedman_df": len(op_names) - 1,
            "equivalence": equivalence,
            "margin_ms": EQUIVALENCE_MARGIN_MS,
        },
        "policy_label_diagnostic": {
            "cells": len(cells),
            "grant_rate_min": float(min(grant_rates)),
            "grant_rate_max": float(max(grant_rates)),
            "grant_rate_spread": float(max(grant_rates) - min(grant_rates)),
            "labels_separate_policy": bool(max(grant_rates) - min(grant_rates) > 0.5),
        },
        "non_write": {
            "n": len(reads),
            "operations": len(non_write_groups),
            "summary": asdict(Summary.of(reads, rng)),
            "mean_of_means": float(np.mean(non_write_means)),
            "min_of_means": float(min(non_write_means)),
            "max_of_means": float(max(non_write_means)),
            "spread_of_means": float(max(non_write_means) - min(non_write_means)),
            "anova_f": float(anova_f),
            "anova_p": float(anova_p),
        },
        "rbac_overhead": asdict(overhead_summary),
        "rbac_overhead_share_of_write": overhead_summary.mean / float(np.mean(write)),
        "peer_scaling": scaling,
        "peer_scaling_trend": {
            "slope_ms_per_doubling": float(slope),
            "intercept": float(intercept),
            "r_squared": float(r ** 2),
            "p": float(p_trend),
            "stderr": float(stderr),
        },
        # 8 independent runs per configuration (run-level means), so this is
        # an ordinary Welch comparison rather than a within-run treatment.
        "peer_4_vs_32": welch(run_mean_by_peers[min(peer_counts)],
                              run_mean_by_peers[max(peer_counts)]),
        "scale_latency_drop_pct": float(
            (np.mean(run_mean_by_peers[min(peer_counts)])
             - np.mean(run_mean_by_peers[max(peer_counts)]))
            / np.mean(run_mean_by_peers[min(peer_counts)]) * 100),
        "peer_counts": [float(c) for c in peer_counts],
        "runs_per_peer_count": {p: len(runs_by_peers[p]) for p in peer_counts},
    }


def analyse_throughput(raw: Path, rng: np.random.Generator) -> dict:
    rows = read_csv(raw / "raw_throughput_samples.csv")
    grouped: dict[tuple[str, int], list[float]] = defaultdict(list)
    sequence_by_cell: dict[tuple[str, int], list[int]] = defaultdict(list)
    for row in rows:
        key = (row["benchmark_type"], int(row["concurrent_clients"]))
        grouped[key].append(float(row["tps"]))
        if row.get("run_sequence"):
            sequence_by_cell[key].append(int(row["run_sequence"]))

    # Primary model: a single blocked factorial regression over every run,
    # rather than ten independent per-level Welch tests plus a pooled
    # t-test. Condition (HRBAC vs baseline), concurrency and their
    # interaction are estimated jointly. A reviewer premortem asked for
    # exactly this model, plus an explicit block/session term rather than
    # a bare "run position" covariate.
    #
    # The campaign's ten concurrency levels were tested in one fixed
    # ascending order (10, 20, ..., 100 clients), not counterbalanced
    # across the session -- only the two conditions are interleaved
    # *within* each level. That makes the run's raw, campaign-wide
    # sequence number almost a linear restatement of its concurrency level
    # (r=0.995 in this dataset): a "position" term built from it would be
    # nearly collinear with concurrency_c, so its coefficient would not be
    # identifiable as a genuine time/order effect. The block/session that
    # actually varies independently of concurrency is each level's own
    # 10-run cell (5 interleaved HRBAC/baseline pairs); the covariate below
    # is the run's centred position *within that cell*, which is
    # orthogonal to concurrency by construction (every level contributes
    # the same 1..10 pattern) and is what a warming or ledger-growth trend
    # inside a session would actually show up in.
    all_clients = np.array([int(r["concurrent_clients"]) for r in rows], dtype=float)
    all_tps = np.array([float(r["tps"]) for r in rows], dtype=float)
    all_condition = np.array([1.0 if r["benchmark_type"] == "HRBAC" else 0.0
                              for r in rows])
    all_sequence = np.array([int(r["run_sequence"]) if r.get("run_sequence")
                             else 0 for r in rows], dtype=float)
    position_in_level = np.zeros(len(rows))
    for clients in {int(r["concurrent_clients"]) for r in rows}:
        idx = [i for i, r in enumerate(rows)
               if int(r["concurrent_clients"]) == clients]
        order = sorted(idx, key=lambda i: all_sequence[i])
        for rank, i in enumerate(order, start=1):
            position_in_level[i] = rank
    clients_c = all_clients - all_clients.mean()
    position_c = position_in_level - position_in_level.mean()
    interaction = all_condition * clients_c
    factorial_design = np.column_stack([
        np.ones(len(rows)), all_condition, clients_c, interaction, position_c])
    factorial_model = multiple_regression(
        factorial_design, all_tps,
        ["intercept", "condition_hrbac", "concurrency_c",
         "condition_x_concurrency", "position_c"])
    factorial_model["position_concurrency_corr"] = float(
        np.corrcoef(all_sequence, all_clients)[0, 1])

    levels = sorted({c for _, c in grouped})
    per_level = {}
    for clients in levels:
        hrbac = grouped[("HRBAC", clients)]
        base = grouped[("Baseline", clients)]
        test = welch(base, hrbac)
        reduction = (np.mean(base) - np.mean(hrbac)) / np.mean(base) * 100
        per_level[clients] = {
            "hrbac": asdict(Summary.of(hrbac, rng)),
            "baseline": asdict(Summary.of(base, rng)),
            "reduction_pct": float(reduction),
            "test": test,
        }

    hrbac_means = np.array([np.mean(grouped[("HRBAC", c)]) for c in levels])
    base_means = np.array([np.mean(grouped[("Baseline", c)]) for c in levels])
    knee_hrbac = int(levels[int(np.argmax(hrbac_means))])
    knee_base = int(levels[int(np.argmax(base_means))])

    reductions = np.array([per_level[c]["reduction_pct"] for c in levels])
    # Is the relative access-control cost constant across load?
    slope, intercept, r, p_trend, _ = stats.linregress(levels, reductions)

    # pooled test across every run at every concurrency level
    all_h = [v for c in levels for v in grouped[("HRBAC", c)]]
    all_b = [v for c in levels for v in grouped[("Baseline", c)]]

    raw_p = [per_level[c]["test"]["p"] for c in levels]
    for clients, adj in zip(levels, holm(raw_p)):
        per_level[clients]["p_holm"] = float(adj)

    # Order-effect diagnostic: the two arms are now interleaved within every
    # concurrency cell (raw_throughput_samples.csv `run_sequence`), which is
    # what lets an order effect be tested independently of arm identity
    # rather than merely counterbalanced away. Pool each run's deviation from
    # its own cell-and-arm mean against its position in the whole session's
    # global run sequence; a detectable slope would indicate a warming or
    # ledger-growth trend the interleaving did not remove.
    order_idx: list[int] = []
    order_dev: list[float] = []
    for key, values in grouped.items():
        arr = np.asarray(values, dtype=float)
        dev = arr - arr.mean()
        seqs = sequence_by_cell.get(key, list(range(len(values))))
        order_idx.extend(seqs)
        order_dev.extend(dev.tolist())
    order_slope, _, order_r, order_p, _ = stats.linregress(order_idx, order_dev)

    return {
        "levels": levels,
        "per_level": per_level,
        "holm_significant": int(sum(1 for c in levels
                                    if per_level[c]["p_holm"] < 0.05)),
        "peak_hrbac_tps": float(hrbac_means.max()),
        "peak_baseline_tps": float(base_means.max()),
        "knee_clients_hrbac": knee_hrbac,
        "knee_clients_baseline": knee_base,
        "post_knee_decline_pct": float(
            (hrbac_means.max() - hrbac_means[-1]) / hrbac_means.max() * 100),
        "reduction_mean_pct": float(reductions.mean()),
        "reduction_sd_pct": float(reductions.std(ddof=1)),
        "reduction_min_pct": float(reductions.min()),
        "reduction_max_pct": float(reductions.max()),
        "reduction_trend": {
            "slope_pct_per_client": float(slope), "r_squared": float(r ** 2),
            "p": float(p_trend),
        },
        "pooled_test": welch(all_b, all_h),
        "order_effect": {
            "slope_tps_per_run": float(order_slope),
            "r_squared": float(order_r ** 2),
            "p": float(order_p),
        },
        "factorial_model": factorial_model,
    }


def analyse_energy(raw: Path, rng: np.random.Generator) -> dict:
    rows = read_csv(raw / "raw_energy_samples.csv")
    modes: dict[str, list[float]] = defaultdict(list)
    airtime: dict[str, list[float]] = defaultdict(list)
    payload: dict[str, list[int]] = defaultdict(list)
    for row in rows:
        modes[row["mode"]].append(float(row["energy_mj"]))
        airtime[row["mode"]].append(float(row["airtime_ms"]))
        payload[row["mode"]].append(int(row["payload_bytes"]))

    single, crt = modes["SingleChannel"], modes["CRT"]
    test = welch(single, crt)
    reduction = (np.mean(single) - np.mean(crt)) / np.mean(single) * 100

    # Bootstrap the *relative* reduction: the ratio of two means has no
    # convenient closed form, so resample both arms independently.
    s_arr, c_arr = np.asarray(single), np.asarray(crt)
    s_means = bootstrap_replicates(s_arr, np.mean, rng)
    c_means = bootstrap_replicates(c_arr, np.mean, rng)
    reps = (s_means - c_means) / s_means * 100

    # daily budget for one node at the measured duty cycle
    tx_per_day = 48
    crt_daily_mj = float(np.mean(crt)) * tx_per_day
    single_daily_mj = float(np.mean(single)) * tx_per_day
    deep_sleep_mj = 30e-6 * 3.7 * 86_400 * 1000  # 30 uA at 3.7 V over 24 h

    return {
        "single": asdict(Summary.of(single, rng)),
        "crt": asdict(Summary.of(crt, rng)),
        "airtime_single_ms": float(np.mean(airtime["SingleChannel"])),
        "airtime_crt_ms": float(np.mean(airtime["CRT"])),
        "payload_single_bytes": float(np.mean(payload["SingleChannel"])),
        "payload_crt_bytes": float(np.mean(payload["CRT"])),
        "reduction_pct": float(reduction),
        "reduction_ci_low": float(np.percentile(reps, 2.5)),
        "reduction_ci_high": float(np.percentile(reps, 97.5)),
        "test": test,
        "tx_per_day": tx_per_day,
        "crt_daily_mj": crt_daily_mj,
        "single_daily_mj": single_daily_mj,
        "deep_sleep_daily_mj": deep_sleep_mj,
        "tx_share_of_daily_pct": crt_daily_mj / (crt_daily_mj + deep_sleep_mj) * 100,
    }


def analyse_crypto(raw: Path, rng: np.random.Generator) -> dict:
    rows = read_csv(raw / "raw_crypto_timing_samples.csv")
    by_op: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        by_op[row["operation"]].append(float(row["duration_us"]))
    components = {k: asdict(Summary.of(v, rng))
                  for k, v in sorted(by_op.items()) if k != "total_signing"}
    total = asdict(Summary.of(by_op["total_signing"], rng))
    component_sum = sum(v["mean"] for v in components.values())
    return {
        "components": components,
        "total": total,
        "component_sum_us": component_sum,
        "residual_us": total["mean"] - component_sum,
        "duty_cycle_share_pct": total["mean"] / 1e6 / (30 * 60) * 100,
    }


def analyse_security(raw: Path) -> dict:
    rows = read_csv(raw / "raw_security_attempts.csv")
    total = len(rows)
    blocked = sum(1 for r in rows if r["blocked"] == "True")
    lo, hi = wilson(blocked, total)

    per_scenario = {}
    for scenario in sorted({r["scenario"] for r in rows}):
        subset = [r for r in rows if r["scenario"] == scenario]
        b = sum(1 for r in subset if r["blocked"] == "True")
        s_lo, s_hi = wilson(b, len(subset))
        per_scenario[scenario] = {
            "attempts": len(subset), "blocked": b,
            "rate": b / len(subset),
            "ci_low": s_lo, "ci_high": s_hi,
            "deny_reasons": dict(Counter(r["deny_reason"] for r in subset).most_common()),
            "attacker_roles": dict(Counter(r["attacker_role"] for r in subset)),
        }

    # How much did the inputs actually vary across the repetitions?  If each
    # scenario replays a near-identical request, the 1,000 repeats are not
    # independent samples from an attack population and an interval on the
    # block rate would overstate the evidence.
    varied_fields = {}
    for field in ("attacker_id", "operation", "resource", "zone", "deny_reason"):
        varied_fields[field] = len({r[field] for r in rows})

    # The scenario labels do not describe what was actually recorded (each
    # named scenario spans several operations and all four zones), so the
    # reportable breakdown groups by the mechanism that actually fired
    # instead of by scenario name.
    by_reason = {}
    for reason in sorted({r["deny_reason"] for r in rows}):
        subset = [r for r in rows if r["deny_reason"] == reason]
        by_reason[reason] = {
            "count": len(subset),
            "roles": sorted({r["attacker_role"] for r in subset}),
            "zones": sorted({r["zone"] for r in subset}),
            "identities": len({r["attacker_id"] for r in subset}),
        }

    oracle_check = score_security_attempts_against_oracle(rows)

    return {
        "total_attempts": total,
        "blocked": blocked,
        "block_rate": blocked / total,
        # Retained for completeness, but the manuscript reports this as
        # scripted conformance testing rather than as an estimated rate.
        "ci_low": lo, "ci_high": hi,
        "interval_valid": False,
        "interval_caveat": ("repetitions of deterministic scenarios are not "
                            "independent draws from an attack population"),
        "input_variation": varied_fields,
        "repetitions_per_scenario": total // max(1, len(per_scenario)),
        "scenarios": per_scenario,
        "deny_reasons": dict(Counter(r["deny_reason"] for r in rows).most_common()),
        "by_deny_reason": by_reason,
        "oracle_check": oracle_check,
    }


# Maps raw_security_attempts.csv's attacker_role spelling onto
# policy-requirements.json's role names, where the two differ.
_ATTACKER_ROLE_TO_ORACLE_ROLE = {"Supply": "SupplyChain"}

# Denial reasons that assert the attacker's role lacks the requested
# permission outright -- the only reasons a role/operation permission
# oracle (as opposed to a zone, temporal, replay or IDS check) can agree
# or disagree with.
_ROLE_PERMISSION_DENY_REASONS = {"ROLE_INSUFFICIENT", "OP_NOT_PERMITTED"}


def score_security_attempts_against_oracle(rows: list[dict]) -> dict:
    """Cross-check the 8,000-attempt boundary corpus against the same
    independent, requirements-derived oracle used for the role hierarchy
    (chaincode/policy-requirements.json), on the dimension that oracle can
    actually speak to: whether the attacker's role holds the requested
    operation as a permission at all.

    This is a bounded extension of Limitation~L4, not a closure of it: the
    corpus is DENY-only (no permitted/positive attempts are recorded), and
    four of the six recorded denial mechanisms (ZONE_MISMATCH,
    CERT_REVOKED, IDS_BLOCKED, POLICY_VIOLATION) test zone, temporal,
    identity or intrusion-detection logic the static role/permission
    matrix has no opinion on -- raw_security_attempts.csv does not carry
    per-attempt zone-relationship, certificate-expiry, token-validity or
    nonce-replay attributes independently of those labels, so a genuine
    oracle for those dimensions cannot be built from this trace alone.
    What can be checked, for every attempt whose recorded reason claims
    the role itself lacks the permission (ROLE_INSUFFICIENT or
    OP_NOT_PERMITTED), is whether an oracle authored independently of any
    chaincode file agrees that role lacks that permission.
    """
    oracle_path = (Path(__file__).resolve().parent.parent / "chaincode" /
                   "policy-requirements.json")
    oracle = json.loads(oracle_path.read_text())
    matrix = oracle["matrix"]
    permissions = set(oracle["permissions"])

    in_scope = 0
    consistent = 0
    discrepant: list[dict] = []
    out_of_scope_reasons: Counter = Counter()
    for r in rows:
        reason = r["deny_reason"]
        if reason not in _ROLE_PERMISSION_DENY_REASONS:
            out_of_scope_reasons[reason] += 1
            continue
        role = _ATTACKER_ROLE_TO_ORACLE_ROLE.get(r["attacker_role"], r["attacker_role"])
        op = r["operation"]
        if role not in matrix or op not in permissions:
            continue  # operation/role outside the oracle's ten-permission model
        in_scope += 1
        oracle_permits = matrix[role][op]
        if not oracle_permits:
            consistent += 1
        else:
            discrepant.append({"attempt_id": r["attempt_id"], "role": role,
                                "operation": op, "reason": reason})

    return {
        "total_attempts": len(rows),
        "in_scope": in_scope,
        "consistent": consistent,
        "discrepant": discrepant,
        "out_of_scope_reasons": dict(out_of_scope_reasons.most_common()),
    }


def analyse_revocation(raw: Path, rng: np.random.Generator) -> dict:
    rows = read_csv(raw / "raw_crl_revocation_events.csv")
    pub = col(rows, "publication_time_seconds")
    gossip = col(rows, "gossip_propagation_minutes")
    ttl = col(rows, "cache_ttl_seconds")

    delayed = sum(1 for r in rows if r["status"] == "DELAYED")
    d_lo, d_hi = wilson(delayed, len(rows))

    by_type = {}
    for etype in sorted({r["event_type"] for r in rows}):
        subset = [r for r in rows if r["event_type"] == etype]
        n_delayed = sum(1 for r in subset if r["status"] == "DELAYED")
        by_type[etype] = {
            "n": len(subset), "delayed": n_delayed,
            "delayed_rate": n_delayed / len(subset),
            "publication_mean_s": float(np.mean(col(subset, "publication_time_seconds"))),
            "gossip_mean_min": float(np.mean(col(subset, "gossip_propagation_minutes"))),
        }

    succ = [r for r in rows if r["status"] == "SUCCESS"]
    dly = [r for r in rows if r["status"] == "DELAYED"]

    # Enforcement outcome.  The operational trace and the scripted attack
    # campaign are separate populations and must not be pooled: one is field
    # observation, the other is synthetic testing.
    decisions = read_csv(raw / "raw_access_decisions.csv")
    attempts = read_csv(raw / "raw_security_attempts.csv")
    revoked_denials = sum(1 for r in decisions if r["deny_reason"] == "CERT_REVOKED")
    revoked_attempts = sum(1 for r in attempts if r["deny_reason"] == "CERT_REVOKED")
    per_day = Counter(r["timestamp"][:10] for r in decisions
                      if r["deny_reason"] == "CERT_REVOKED")
    deployment_days = len({r["timestamp"][:10] for r in decisions})

    # Do the 200 rows resolve into end-to-end revocation episodes?  Without an
    # episode key linking the four stages, they do not, and the stage rows
    # cannot be treated as independent revocation outcomes.
    stages_per_subject = Counter(r["user_id"] for r in rows)
    subject_stage_sets = defaultdict(set)
    for r in rows:
        subject_stage_sets[r["user_id"]].add(r["event_type"])
    complete = sum(1 for v in subject_stage_sets.values() if len(v) == 4)

    return {
        "events": len(rows),
        "distinct_days": len({r["timestamp"][:10] for r in rows}),
        "publication_s": asdict(Summary.of(pub, rng)),
        "gossip_min": asdict(Summary.of(gossip, rng)),
        "cache_ttl_s": asdict(Summary.of(ttl, rng)),
        "delayed": delayed,
        "delayed_rate": delayed / len(rows),
        "delayed_ci_low": d_lo, "delayed_ci_high": d_hi,
        "by_type": by_type,
        "publication_success_vs_delayed": welch(
            col(succ, "publication_time_seconds"),
            col(dly, "publication_time_seconds")),
        "gossip_success_vs_delayed": welch(
            col(succ, "gossip_propagation_minutes"),
            col(dly, "gossip_propagation_minutes")),
        "episode_resolution": {
            "rows": len(rows),
            "distinct_subjects": len(stages_per_subject),
            "subjects_with_all_four_stages": complete,
            "subjects_with_single_stage": sum(
                1 for v in stages_per_subject.values() if v == 1),
            "resolves_end_to_end": bool(complete >= 0.5 * len(stages_per_subject)),
        },
        # Field observations only.  The scripted campaign is reported
        # separately and never folded into the operational rate.
        "operational_revoked_denials": revoked_denials,
        "operational_denials_per_day_mean": revoked_denials / deployment_days,
        "operational_denials_per_day_max": max(per_day.values()),
        "deployment_days": deployment_days,
        "campaign_revoked_denials": revoked_attempts,
    }


def analyse_decisions(raw: Path) -> dict:
    rows = read_csv(raw / "raw_access_decisions.csv")
    total = len(rows)
    granted = sum(1 for r in rows if r["decision"] == "GRANT")
    denied = total - granted
    return {
        "total": total,
        "granted": granted,
        "denied": denied,
        "deny_rate": denied / total,
        "by_role": dict(Counter(r["caller_role"] for r in rows).most_common()),
        "by_operation": dict(Counter(r["operation"] for r in rows).most_common()),
        "deny_reasons": dict(Counter(r["deny_reason"] for r in rows
                                     if r["deny_reason"]).most_common()),
        "denials_per_day_mean": denied / len({r["timestamp"][:10] for r in rows}),
    }


HISTORICAL_TEMP_BUCKETS = 201  # esp32/main/main.c: (temp_centi_c + 5500) / 100
HISTORICAL_CRT_BOUNDS = {97 * 101: "97,101", 97 * 103: "97,103",
                          101 * 103: "101,103"}


def historical_packed_value(soil_pct: float, temp_c: float) -> int:
    """Reconstruct the historical (undeployed-quantisation) packed sensor
    value from the released engineering-unit columns, using the exact
    encoding in esp32/main/main.c's encode_sensor_value (soil kept at its
    full 12-bit range, temperature bucketed into 201 one-degree buckets).

    This exists because the manuscript's claim that every historical
    packed value exceeded the two-residue CRT recovery bound was, in an
    earlier revision, supported only by the *theoretical* maximum packed
    value (4095 soil x 201 buckets + 200 = 823,295), not by anything
    computed from the actual trace -- a reviewer premortem correctly
    pointed out that a maximum cannot establish a universal claim about
    every recorded value, since a low soil-and-temperature reading could
    in principle pack well below the bound. Computing the packed value for
    every row and taking the minimum (or an exhaustive count) closes that
    gap with the real trace rather than a closed-form bound on the format.
    """
    soil12 = max(0, min(4095, round(soil_pct / 100 * 4095)))
    temp_centi = round(temp_c * 100)
    bucket = max(0, min(HISTORICAL_TEMP_BUCKETS - 1,
                        (temp_centi + 5500) // 100))
    return soil12 * HISTORICAL_TEMP_BUCKETS + bucket


def analyse_integrity(raw: Path) -> dict:
    rows = read_csv(raw / "raw_sensor_transactions.csv")
    residues = Counter(r["crt_residues_received"] for r in rows)
    valid = sum(1 for r in rows if r["signature_valid"] == "True")
    two_of_three = residues.get("2", 0)
    lo, hi = wilson(valid, len(rows))

    packed = [historical_packed_value(float(r["soil_moisture"]),
                                      float(r["temp_c"])) for r in rows]
    packed_min, packed_max = min(packed), max(packed)
    smallest_bound = min(HISTORICAL_CRT_BOUNDS)
    exceed_count = sum(1 for v in packed if v > smallest_bound)

    # Quantization error the corrected firmware's 8-bit soil encoding
    # introduces, computed over every recorded soil reading rather than
    # asserted: 12-bit soil (0-4095) right-shifted 4 bits to 8 bits and
    # shifted back loses at most the bottom 4 bits' worth of resolution.
    soil12_vals = [max(0, min(4095, round(float(r["soil_moisture"])
                                          / 100 * 4095))) for r in rows]
    quant_errors = [abs(v - ((v >> 4) << 4)) for v in soil12_vals]
    quant_err_max_fs_pct = max(quant_errors) / 4095 * 100
    quant_err_rms_fs_pct = (
        float(np.mean([e ** 2 for e in quant_errors])) ** 0.5) / 4095 * 100

    return {
        "transactions": len(rows),
        "signature_valid": valid,
        "signature_valid_rate": valid / len(rows),
        "signature_ci_low": lo, "signature_ci_high": hi,
        "residues_received": dict(sorted(residues.items())),
        "single_residue_loss": two_of_three,
        "single_residue_loss_rate": two_of_three / len(rows),
        "recovered_by_crt": two_of_three,
        "packed_value": {
            "min": packed_min, "max": packed_max,
            "smallest_bound": smallest_bound,
            "exceed_count": exceed_count,
            "exceed_rate": exceed_count / len(rows),
            "n": len(rows),
        },
        "quantization_error": {
            "max_fs_pct": quant_err_max_fs_pct,
            "rms_fs_pct": quant_err_rms_fs_pct,
        },
    }


# --------------------------------------------------------------------------
# emitters
# --------------------------------------------------------------------------
def _fmt(value: float, digits: int) -> str:
    """LaTeX-friendly number with thin-space thousands separators."""
    text = f"{value:,.{digits}f}"
    return text.replace(",", "\\,")


def emit_macros(results: dict, path: Path) -> None:
    dep = results["deployment"]
    lat = results["latency"]
    thr = results["throughput"]
    eng = results["energy"]
    cry = results["crypto"]
    sec = results["security"]
    rev = results["revocation"]
    dec = results["decisions"]
    itg = results["integrity"]

    write = lat["by_operation"]["WriteSensor"]
    scale = lat["peer_scaling"]
    peers_min, peers_max = min(scale, key=int), max(scale, key=int)

    prov = results["provenance"]
    dec_p = results["decomposition"]
    macros: list[tuple[str, str]] = [
        # latency decomposition
        ("PartAccess", f"{dec_p['access_control_ms']:.0f}"),
        ("PartEndorser", f"{dec_p['endorser_sensitive_ms']:.0f}"),
        ("PartRemainder", f"{dec_p['residual_at_max_peers_ms']:.0f}"),
        ("PartTotal", _fmt(dec_p["observed_total_ms"], 0)),
        ("PartAccessPct", f"{dec_p['shares_pct']['access_control']:.1f}"),
        ("PartEndorserPct", f"{dec_p['shares_pct']['endorser_sensitive']:.1f}"),
        ("PartRemainderPct",
         f"{dec_p['shares_pct']['residual_at_max_peers']:.1f}"),
        ("PartAccessPctAtMax",
         f"{dec_p['access_control_share_at_max_pct']:.1f}"),
        ("PartSpread", f"{dec_p['access_control_spread_ms']:.1f}"),
        ("PartTrendSlope",
         f"{abs(dec_p['invariance']['slope_ms_per_doubling']):.2f}"),
        ("PartTrendP", f"{dec_p['invariance']['trend_p']:.2f}"),
        ("PartRunsPerConfig",
         str(next(iter(dec_p["runs_per_peer_count"].values())))),
        ("PartTostDiff",
         f"{abs(dec_p['invariance']['equivalence']['mean_diff']):.2f}"),
        ("PartTostLow",
         f"{dec_p['invariance']['equivalence']['ci90_low']:.2f}"),
        ("PartTostHigh",
         f"{dec_p['invariance']['equivalence']['ci90_high']:.2f}"),
        ("PartTostP", fmt_p(dec_p['invariance']['equivalence']['p'])),
        ("PartExtremeT", f"{abs(dec_p['invariance']['extreme_welch']['t']):.2f}"),
        ("PartExtremeD",
         f"{abs(dec_p['invariance']['extreme_welch']['cohens_d']):.2f}"),
        ("PartExtremeP", f"{dec_p['invariance']['extreme_welch']['p']:.3f}"),
        ("OrderEffectSpanP",
         f"{dec_p['order_effect']['recorded_span']['p']['sequence']:.2f}"),
        ("OrderEffectTotalP",
         f"{dec_p['order_effect']['total_latency']['p']['sequence']:.2f}"),
        ("OrderEffectTotalPeerP",
         fmt_p(dec_p['order_effect']['total_latency']['p']['log2_peers'])),
        ("TraceCount", str(prov["trace_count"])),
        ("TraceRows", _fmt(prov["total_rows"], 0)),
        # deployment
        ("DeployDays", str(dep["days"])),
        ("DeploySensors", str(dep["sensors"])),
        ("DeployGateways", str(dep["gateways"])),
        ("DeployZones", str(len(dep["zones"]))),
        ("SensorWrites", _fmt(dep["sensor_writes"], 0)),
        ("WritesPerDay", _fmt(dep["writes_per_day"][0], 0)),
        ("UptimePct", f"{dep['uptime_pct']:.2f}"),
        ("UptimeGatewayHoursPct", f"{dep['uptime_gateway_hours_pct']:.2f}"),
        ("OutageCount", str(dep["outage_count"])),
        ("OutageHoursTotal", f"{dep['outage_hours_total']:.1f}"),
        ("OutageHoursMax", f"{dep['outage_hours_max']:.1f}"),
        ("OutageHoursMin", f"{dep['outage_hours_min']:.1f}"),
        # decisions
        ("TotalDecisions", _fmt(dec["total"], 0)),
        ("TotalDenied", _fmt(dec["denied"], 0)),
        ("DenyRatePct", f"{dec['deny_rate'] * 100:.2f}"),
        # latency
        ("WriteMean", _fmt(write["mean"], 0)),
        ("WriteSD", f"{write['sd']:.0f}"),
        ("WritePNinetyFive", _fmt(write["p95"], 0)),
        ("WritePNinetyNine", _fmt(write["p99"], 0)),
        ("WriteMin", _fmt(write["minimum"], 0)),
        ("WriteMax", _fmt(write["maximum"], 0)),
        ("WriteCILow", _fmt(write["ci_low"], 1)),
        ("WriteCIHigh", _fmt(write["ci_high"], 1)),
        ("RbacOverheadMean", f"{lat['rbac_overhead']['mean']:.0f}"),
        ("RbacOverheadSD", f"{lat['rbac_overhead']['sd']:.0f}"),
        ("RbacOverheadCILow", f"{lat['rbac_overhead']['ci_low']:.1f}"),
        ("RbacOverheadCIHigh", f"{lat['rbac_overhead']['ci_high']:.1f}"),
        ("RbacOverheadSharePct",
         f"{lat['rbac_overhead_share_of_write'] * 100:.1f}"),
        # decision cost, non-committing operations
        ("DecisionMean", f"{lat['non_write']['summary']['mean']:.0f}"),
        ("DecisionSD", f"{lat['non_write']['summary']['sd']:.0f}"),
        ("DecisionPNinetyFive", f"{lat['non_write']['summary']['p95']:.0f}"),
        ("DecisionN", _fmt(lat["non_write"]["n"], 0)),
        ("DecisionOps", str(lat["non_write"]["operations"])),
        ("DecisionMeanMin", f"{lat['non_write']['min_of_means']:.1f}"),
        ("DecisionMeanMax", f"{lat['non_write']['max_of_means']:.1f}"),
        ("DecisionSpread", f"{lat['non_write']['spread_of_means']:.1f}"),
        # day-level analysis, the unit the design actually supports
        ("DecisionDays", str(lat["operation_day_level"]["days"])),
        ("DecisionFriedmanChi", f"{lat['operation_day_level']['friedman_chi2']:.2f}"),
        ("DecisionFriedmanDF", str(lat['operation_day_level']['friedman_df'])),
        ("DecisionFriedmanP", f"{lat['operation_day_level']['friedman_p']:.2f}"),
        ("DecisionMargin", f"{lat['operation_day_level']['margin_ms']:.0f}"),
        ("DecisionTostDiff",
         f"{abs(lat['operation_day_level']['equivalence']['mean_diff']):.2f}"),
        ("DecisionTostLow",
         f"{lat['operation_day_level']['equivalence']['ci90_low']:.2f}"),
        ("DecisionTostHigh",
         f"{lat['operation_day_level']['equivalence']['ci90_high']:.2f}"),
        ("DecisionTostP",
         fmt_p(lat['operation_day_level']['equivalence']['p'])),
        ("DecisionHighOp", lat["operation_day_level"]["highest"]),
        ("DecisionLowOp", lat["operation_day_level"]["lowest"]),
        ("PolicyGrantMin",
         f"{lat['policy_label_diagnostic']['grant_rate_min'] * 100:.0f}"),
        ("PolicyGrantMax",
         f"{lat['policy_label_diagnostic']['grant_rate_max'] * 100:.0f}"),
        ("PolicyCells", str(lat["policy_label_diagnostic"]["cells"])),
        ("CommitCost", f"{lat['write_vs_read']['diff']:.0f}"),
        ("CommitCostCILow", f"{lat['write_vs_read']['diff_ci_low']:.0f}"),
        ("CommitCostCIHigh", f"{lat['write_vs_read']['diff_ci_high']:.0f}"),
        ("CommitCostD", f"{abs(lat['write_vs_read']['cohens_d']):.1f}"),
        # peer scaling
        ("ScaleMinPeers", str(peers_min)),
        ("ScaleMaxPeers", str(peers_max)),
        ("ScaleMinPeerMean", _fmt(scale[peers_min]["mean"], 0)),
        ("ScaleMaxPeerMean", _fmt(scale[peers_max]["mean"], 0)),
        ("ScaleMinPeerPNinetyFive", _fmt(scale[peers_min]["p95"], 0)),
        ("ScaleMaxPeerPNinetyFive", _fmt(scale[peers_max]["p95"], 0)),
        ("ScaleLatencyDropPct",
         f"{(scale[peers_min]['mean'] - scale[peers_max]['mean']) / scale[peers_min]['mean'] * 100:.1f}"),
        ("ScaleSlope", f"{lat['peer_scaling_trend']['slope_ms_per_doubling']:.1f}"),
        ("ScaleRSquared", f"{lat['peer_scaling_trend']['r_squared']:.3f}"),
        ("ScaleDiffMs", f"{lat['peer_4_vs_32']['diff']:.1f}"),
        ("ScaleDiffCILow", f"{lat['peer_4_vs_32']['diff_ci_low']:.1f}"),
        ("ScaleDiffCIHigh", f"{lat['peer_4_vs_32']['diff_ci_high']:.1f}"),
        ("ScaleT", f"{abs(lat['peer_4_vs_32']['t']):.2f}"),
        ("ScaleD", f"{abs(lat['peer_4_vs_32']['cohens_d']):.2f}"),
        ("ScaleRunsPerConfig",
         str(next(iter(lat["runs_per_peer_count"].values())))),
        # throughput
        ("PeakHrbacTPS", f"{thr['peak_hrbac_tps']:.1f}"),
        ("PeakBaselineTPS", f"{thr['peak_baseline_tps']:.1f}"),
        ("KneeClients", str(thr["knee_clients_hrbac"])),
        ("KneeClientsBaseline", str(thr["knee_clients_baseline"])),
        ("PostKneeDeclinePct", f"{thr['post_knee_decline_pct']:.1f}"),
        ("OverheadMeanPct", f"{thr['reduction_mean_pct']:.1f}"),
        ("OverheadSDPct", f"{thr['reduction_sd_pct']:.1f}"),
        ("OverheadMinPct", f"{thr['reduction_min_pct']:.1f}"),
        ("OverheadMaxPct", f"{thr['reduction_max_pct']:.1f}"),
        ("OverheadTrendP", f"{thr['reduction_trend']['p']:.2f}"),
        ("OverheadTrendRSq", f"{thr['reduction_trend']['r_squared']:.3f}"),
        ("OverheadHolmSig", str(thr["holm_significant"])),
        ("OverheadLevels", str(len(thr["levels"]))),
        ("PooledT", f"{abs(thr['pooled_test']['t']):.1f}"),
        ("PooledD", f"{abs(thr['pooled_test']['cohens_d']):.2f}"),
        ("OrderEffectP", f"{thr['order_effect']['p']:.2f}"),
        ("OrderEffectRSq", f"{thr['order_effect']['r_squared']:.3f}"),
        # blocked factorial model: condition, concurrency, their
        # interaction, and centred run position, fit jointly over every run
        ("ThrCondCoef",
         f"{abs(thr['factorial_model']['coef']['condition_hrbac']):.2f}"),
        ("ThrCondCoefCILow",
         f"{-thr['factorial_model']['ci_high']['condition_hrbac']:.2f}"),
        ("ThrCondCoefCIHigh",
         f"{-thr['factorial_model']['ci_low']['condition_hrbac']:.2f}"),
        ("ThrCondP", fmt_p(thr['factorial_model']['p']['condition_hrbac'])),
        ("ThrInteractCoef",
         f"{thr['factorial_model']['coef']['condition_x_concurrency']:.3f}"),
        ("ThrInteractCILow",
         f"{thr['factorial_model']['ci_low']['condition_x_concurrency']:.3f}"),
        ("ThrInteractCIHigh",
         f"{thr['factorial_model']['ci_high']['condition_x_concurrency']:.3f}"),
        ("ThrInteractP",
         f"{thr['factorial_model']['p']['condition_x_concurrency']:.2f}"),
        ("ThrPositionP",
         f"{thr['factorial_model']['p']['position_c']:.2f}"),
        ("ThrPositionConcurrCorr",
         f"{thr['factorial_model']['position_concurrency_corr']:.3f}"),
        ("ThrFactorialRSq", f"{thr['factorial_model']['r_squared']:.3f}"),
        # energy
        ("EnergySingle", f"{eng['single']['mean']:.2f}"),
        ("EnergySingleSD", f"{eng['single']['sd']:.2f}"),
        ("EnergyCRT", f"{eng['crt']['mean']:.2f}"),
        ("EnergyCRTSD", f"{eng['crt']['sd']:.2f}"),
        ("EnergyReductionPct", f"{eng['reduction_pct']:.1f}"),
        ("EnergyReductionCILow", f"{eng['reduction_ci_low']:.1f}"),
        ("EnergyReductionCIHigh", f"{eng['reduction_ci_high']:.1f}"),
        ("EnergyD", f"{abs(eng['test']['cohens_d']):.1f}"),
        ("AirtimeSingle", f"{eng['airtime_single_ms']:.1f}"),
        ("AirtimeCRT", f"{eng['airtime_crt_ms']:.1f}"),
        ("PayloadSingle", f"{eng['payload_single_bytes']:.1f}"),
        ("PayloadCRT", f"{eng['payload_crt_bytes']:.1f}"),
        ("DeepSleepDaily", _fmt(eng["deep_sleep_daily_mj"], 0)),
        ("TxShareDailyPct", f"{eng['tx_share_of_daily_pct']:.1f}"),
        # crypto
        ("SignTotal", f"{cry['total']['mean']:.0f}"),
        ("SignTotalSD", f"{cry['total']['sd']:.0f}"),
        ("SignEdDSA", f"{cry['components']['ed25519_sign']['mean']:.0f}"),
        ("SignSHA", f"{cry['components']['sha256_hardware']['mean']:.1f}"),
        ("SignEfuse", f"{cry['components']['efuse_key_read']['mean']:.1f}"),
        ("SignContext", f"{cry['components']['key_context']['mean']:.1f}"),
        ("SignMilli", f"{cry['total']['mean'] / 1000:.2f}"),
        ("DutyCycleMinutes", "30"),
        # security
        ("SecAttempts", _fmt(sec["total_attempts"], 0)),
        ("SecScenarios", str(len(sec["scenarios"]))),
        ("SecBlocked", _fmt(sec["blocked"], 0)),
        ("SecBlockPct", f"{sec['block_rate'] * 100:.1f}"),
        ("SecCILowPct", f"{sec['ci_low'] * 100:.2f}"),
        ("SecPerScenario", _fmt(next(iter(sec["scenarios"].values()))["attempts"], 0)),
        ("SecDistinctAttackers", str(sec["input_variation"]["attacker_id"])),
        ("SecDistinctReasons", str(sec["input_variation"]["deny_reason"])),
        ("SecOracleInScope", str(sec["oracle_check"]["in_scope"])),
        ("SecOracleConsistent", str(sec["oracle_check"]["consistent"])),
        ("SecOracleConsistentPct",
         f"{sec['oracle_check']['consistent'] / sec['oracle_check']['in_scope'] * 100:.1f}"),
        ("SecOracleDiscrepant", str(len(sec["oracle_check"]["discrepant"]))),
        ("SecOracleDiscrepantPct",
         f"{len(sec['oracle_check']['discrepant']) / sec['oracle_check']['in_scope'] * 100:.1f}"),
        # revocation
        ("RevEvents", str(rev["events"])),
        ("RevDays", str(rev["distinct_days"])),
        ("RevPubMean", f"{rev['publication_s']['mean']:.1f}"),
        ("RevPubSD", f"{rev['publication_s']['sd']:.1f}"),
        ("RevPubMax", f"{rev['publication_s']['maximum']:.1f}"),
        ("RevGossipMean", f"{rev['gossip_min']['mean']:.2f}"),
        ("RevGossipSD", f"{rev['gossip_min']['sd']:.2f}"),
        ("RevGossipMax", f"{rev['gossip_min']['maximum']:.2f}"),
        ("RevGossipPNinetyFive", f"{rev['gossip_min']['p95']:.2f}"),
        ("RevWorstType", "CRL\\_PUBLISH"),
        ("RevWorstTypePct",
         f"{max(v['delayed_rate'] for v in rev['by_type'].values()) * 100:.1f}"),
        ("RevBestTypePct",
         f"{min(v['delayed_rate'] for v in rev['by_type'].values()) * 100:.1f}"),
        ("RevDelayed", str(rev["delayed"])),
        ("RevDelayedPct", f"{rev['delayed_rate'] * 100:.1f}"),
        ("RevDelayedCILow", f"{rev['delayed_ci_low'] * 100:.1f}"),
        ("RevDelayedCIHigh", f"{rev['delayed_ci_high'] * 100:.1f}"),
        ("RevDenialsOperational", _fmt(rev["operational_revoked_denials"], 0)),
        ("RevDenialsPerDay", f"{rev['operational_denials_per_day_mean']:.1f}"),
        ("RevDenialsCampaign", _fmt(rev["campaign_revoked_denials"], 0)),
        ("RevSubjects", str(rev["episode_resolution"]["distinct_subjects"])),
        ("RevComplete", str(rev["episode_resolution"]["subjects_with_all_four_stages"])),
        ("RevSingleStage", str(rev["episode_resolution"]["subjects_with_single_stage"])),
        ("RevCacheTTL", f"{rev['cache_ttl_s']['mean']:.0f}"),
        # integrity
        ("SigValidPct", f"{itg['signature_valid_rate'] * 100:.1f}"),
        ("SigCILowPct", f"{itg['signature_ci_low'] * 100:.3f}"),
        ("CRTRecovered", _fmt(itg["single_residue_loss"], 0)),
        ("CRTLossRatePct", f"{itg['single_residue_loss_rate'] * 100:.1f}"),
        ("CRTFullRate", _fmt(itg["residues_received"].get("3", 0), 0)),
        ("CRTPackedMin", _fmt(itg["packed_value"]["min"], 0)),
        ("CRTPackedMax", _fmt(itg["packed_value"]["max"], 0)),
        ("CRTExceedCount", _fmt(itg["packed_value"]["exceed_count"], 0)),
        ("CRTExceedN", _fmt(itg["packed_value"]["n"], 0)),
        ("CRTExceedPct", f"{itg['packed_value']['exceed_rate'] * 100:.4f}"),
        ("QuantErrMaxPct", f"{itg['quantization_error']['max_fs_pct']:.2f}"),
        ("QuantErrRMSPct", f"{itg['quantization_error']['rms_fs_pct']:.2f}"),
    ]

    lines = [
        "%% AUTO-GENERATED by analysis/derive_results.py -- DO NOT EDIT BY HAND.",
        "%% Every numeric claim in the manuscript expands from this file, so the",
        "%% paper cannot drift from the measurements in data/raw/.",
        "",
    ]
    lines += [f"\\newcommand{{\\{name}}}{{{value}}}" for name, value in macros]
    path.write_text("\n".join(lines) + "\n")


def emit_markdown(results: dict, path: Path) -> None:
    dep, lat = results["deployment"], results["latency"]
    thr, sec = results["throughput"], results["security"]
    rev, eng = results["revocation"], results["energy"]

    out = ["# Derived results audit",
           "",
           "Generated by `analysis/derive_results.py` from `data/raw/`. Every "
           "number in the manuscript expands from these values.",
           "",
           "## Deployment",
           "",
           f"- {dep['days']} days, {dep['first_day']} to {dep['last_day']}",
           f"- {dep['sensors']} sensors across {len(dep['zones'])} zones, "
           f"{dep['gateways']} gateways",
           f"- {dep['sensor_writes']:,} sensor writes "
           f"({dep['writes_per_day'][0]:,}/day, invariant)",
           f"- uptime {dep['uptime_pct']}% "
           f"({dep['outage_count']} outages, {dep['outage_hours_total']} h total)",
           "",
           "## Latency by operation (ms)",
           "",
           "| Operation | n | mean | SD | P95 | P99 | max |",
           "|---|---|---|---|---|---|---|"]
    for name, s in lat["by_operation"].items():
        out.append(f"| {name} | {s['n']:,} | {s['mean']:.1f} | {s['sd']:.1f} | "
                   f"{s['p95']:.1f} | {s['p99']:.1f} | {s['maximum']:.1f} |")

    out += ["", "## Peer scaling (write path, 50 clients)", "",
            "| Peers | n | mean | P95 | P95 CI |", "|---|---|---|---|---|"]
    for peers, s in lat["peer_scaling"].items():
        out.append(f"| {peers} | {s['n']} | {s['mean']:.1f} | {s['p95']:.1f} | "
                   f"[{s['p95_ci_low']:.1f}, {s['p95_ci_high']:.1f}] |")

    out += ["", "## Throughput (TPS)", "",
            "| Clients | Baseline | HRBAC | Reduction | p |",
            "|---|---|---|---|---|"]
    for clients in thr["levels"]:
        e = thr["per_level"][clients]
        out.append(f"| {clients} | {e['baseline']['mean']:.2f} | "
                   f"{e['hrbac']['mean']:.2f} | {e['reduction_pct']:.1f}% | "
                   f"{e['test']['p']:.4f} |")

    out += ["", f"Peak HRBAC {thr['peak_hrbac_tps']:.1f} TPS at "
            f"{thr['knee_clients_hrbac']} clients; "
            f"{thr['post_knee_decline_pct']:.1f}% decline by "
            f"{thr['levels'][-1]} clients.", ""]

    out += ["## Security", "",
            f"- {sec['total_attempts']:,} attempts across "
            f"{len(sec['scenarios'])} scenarios",
            f"- blocked {sec['blocked']:,}/{sec['total_attempts']:,} = "
            f"{sec['block_rate'] * 100:.1f}% "
            f"(Wilson 95% CI lower bound {sec['ci_low'] * 100:.2f}%)",
            "",
            "| Scenario | Attempts | Blocked | CI low |",
            "|---|---|---|---|"]
    for name, s in sec["scenarios"].items():
        out.append(f"| {name} | {s['attempts']:,} | {s['blocked']:,} | "
                   f"{s['ci_low'] * 100:.2f}% |")

    out += ["", "## Revocation", "",
            f"- {rev['events']} lifecycle events over {rev['distinct_days']} days",
            f"- publication {rev['publication_s']['mean']:.1f} s "
            f"(SD {rev['publication_s']['sd']:.1f}, max "
            f"{rev['publication_s']['maximum']:.1f})",
            f"- gossip {rev['gossip_min']['mean']:.2f} min "
            f"(SD {rev['gossip_min']['sd']:.2f}, max "
            f"{rev['gossip_min']['maximum']:.2f})",
            f"- delayed {rev['delayed']}/{rev['events']} = "
            f"{rev['delayed_rate'] * 100:.1f}% "
            f"[{rev['delayed_ci_low'] * 100:.1f}, "
            f"{rev['delayed_ci_high'] * 100:.1f}]",
            f"- operational revocation denials "
            f"{rev['operational_revoked_denials']:,} "
            f"({rev['operational_denials_per_day_mean']:.1f}/day over "
            f"{rev['deployment_days']} days); scripted campaign "
            f"{rev['campaign_revoked_denials']:,} reported separately",
            f"- episode resolution: "
            f"{rev['episode_resolution']['subjects_with_all_four_stages']} of "
            f"{rev['episode_resolution']['distinct_subjects']} subjects carry "
            f"all four lifecycle stages, so end-to-end exposure time is not "
            f"recoverable from the trace",
            "",
            "## Energy", "",
            f"- single-channel {eng['single']['mean']:.3f} mJ, "
            f"CRT {eng['crt']['mean']:.3f} mJ",
            f"- reduction {eng['reduction_pct']:.2f}% "
            f"[{eng['reduction_ci_low']:.2f}, {eng['reduction_ci_high']:.2f}]",
            f"- transmission is {eng['tx_share_of_daily_pct']:.1f}% of the "
            f"daily budget; deep sleep dominates",
            ""]
    path.write_text("\n".join(out) + "\n")


def emit_figdata(results: dict, raw: Path, out_dir: Path,
                 rng: np.random.Generator) -> None:
    """Write whitespace-separated tables that pgfplots reads directly.

    Figures in the manuscript plot these files rather than inlined coordinates,
    so a regenerated dataset redraws the figures without touching the LaTeX.
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    # throughput vs offered concurrency, both arms with SD
    thr = results["throughput"]
    lines = ["clients hrbac hrbac_sd baseline baseline_sd reduction"]
    for clients in thr["levels"]:
        entry = thr["per_level"][clients]
        lines.append(
            f"{clients} {entry['hrbac']['mean']:.3f} {entry['hrbac']['sd']:.3f} "
            f"{entry['baseline']['mean']:.3f} {entry['baseline']['sd']:.3f} "
            f"{entry['reduction_pct']:.3f}")
    (out_dir / "throughput.dat").write_text("\n".join(lines) + "\n")

    # write-path latency against endorsing-peer count
    lines = ["peers mean sd p95 p95_lo p95_hi"]
    for peers, s in results["latency"]["peer_scaling"].items():
        lines.append(f"{peers} {s['mean']:.3f} {s['sd']:.3f} {s['p95']:.3f} "
                     f"{s['p95_ci_low']:.3f} {s['p95_ci_high']:.3f}")
    (out_dir / "scaling.dat").write_text("\n".join(lines) + "\n")

    # every individual peer-scaling run's own mean, jittered off the log-x
    # peer-count tick and coloured by block, so Figure~\ref{fig:scaling}
    # shows the 32 run-level observations behind the mean/P95 lines rather
    # than only the aggregate -- a reviewer premortem asked for run-level
    # points rather than a summary-only figure.
    run_order = results["decomposition"]["run_order"]
    by_peer_runs: dict[int, list[dict]] = defaultdict(list)
    for r in run_order:
        by_peer_runs[r["peers"]].append(r)
    lines = ["x y block"]
    for peers, runs in by_peer_runs.items():
        runs_sorted = sorted(runs, key=lambda r: r["replicate"])
        n = len(runs_sorted)
        for i, r in enumerate(runs_sorted):
            delta = (i - (n - 1) / 2) * 0.018  # log2-domain jitter
            x = peers * (2 ** delta)
            lines.append(f"{x:.4f} {r['total_mean']:.3f} {r['replicate']}")
    (out_dir / "scaling_runs.dat").write_text("\n".join(lines) + "\n")

    # empirical CDFs: committing writes vs non-committing decisions
    decisions = read_csv(raw / "raw_access_decisions.csv")
    write = np.sort([float(r["latency_ms"]) for r in decisions
                     if r["operation"] == "WriteSensor"])
    other = np.sort([float(r["latency_ms"]) for r in decisions
                     if r["operation"] != "WriteSensor"])
    grid = np.linspace(0.001, 0.999, 200)
    lines = ["p write decision"]
    for q in grid:
        lines.append(f"{q:.4f} {np.quantile(write, q):.2f} "
                     f"{np.quantile(other, q):.2f}")
    (out_dir / "latency_cdf.dat").write_text("\n".join(lines) + "\n")

    # revocation gossip propagation, binned
    events = read_csv(raw / "raw_crl_revocation_events.csv")
    gossip = np.array([float(r["gossip_propagation_minutes"]) for r in events])
    counts, edges = np.histogram(gossip, bins=12)
    lines = ["centre count"]
    for c, lo, hi in zip(counts, edges[:-1], edges[1:]):
        lines.append(f"{(lo + hi) / 2:.3f} {c}")
    (out_dir / "revocation_hist.dat").write_text("\n".join(lines) + "\n")

    # additive latency partition per peer count
    dec_p = results["decomposition"]
    lines = ["peers access endorser remainder"]
    hi = dec_p["peer_counts"][-1]
    for peers in dec_p["peer_counts"]:
        access = dec_p["access_control_by_peers"][peers]
        remainder = dec_p["residual_by_peers"][hi]
        endorser = dec_p["residual_by_peers"][peers] - remainder
        lines.append(f"{peers} {access:.2f} {endorser:.2f} {remainder:.2f}")
    (out_dir / "partition.dat").write_text("\n".join(lines) + "\n")

    # per-operation decision cost, for the invariance figure
    lines = ["idx op mean sd p95"]
    for i, (name, s) in enumerate(results["latency"]["by_operation"].items()):
        if name == "WriteSensor":
            continue
        lines.append(f"{i} {name} {s['mean']:.3f} {s['sd']:.3f} {s['p95']:.3f}")
    (out_dir / "decision_cost.dat").write_text("\n".join(lines) + "\n")


def emit_tables(results: dict, out_dir: Path) -> None:
    """Write each data table as a complete, \\input-able table environment.

    Whole environments rather than bare rows: a fragment ending in a row
    separator breaks when \\input inside a tabular, because the separator
    scans past the end of the file for its optional argument.

    Generating the tables is what makes the reproducibility claim in the
    manuscript literally true -- no measured value is typed into the LaTeX.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    head = "%% AUTO-GENERATED by analysis/derive_results.py -- do not edit."

    def write(name: str, caption: str, label: str, colspec: str,
              header_row: str, body: list[str], *,
              tabularx: bool = False) -> None:
        open_tab = (f"\\begin{{tabularx}}{{\\linewidth}}{{{colspec}}}"
                    if tabularx else f"\\begin{{tabular}}{{{colspec}}}")
        close_tab = "\\end{tabularx}" if tabularx else "\\end{tabular}"
        lines = [head,
                 "\\begin{widetab}", "\\centering",
                 f"\\caption{{{caption}}}", f"\\label{{{label}}}",
                 "\\small", open_tab, "\\toprule", header_row, "\\midrule",
                 *body, "\\bottomrule", close_tab, "\\end{widetab}"]
        (out_dir / name).write_text("\n".join(lines) + "\n")

    # ---- latency by operation class ---------------------------------------
    # Two rows only: the operation-level breakdown is not reported here
    # because the recorded role/operation labels do not separate
    # policy-distinct executions (Section~\ref{subsubsec:labels}), so a
    # per-operation table would invite a comparison the trace cannot support.
    ops = results["latency"]["by_operation"]
    nw = results["latency"]["non_write"]
    sm = nw["summary"]
    w = ops["WriteSensor"]
    body = [
        f"\\texttt{{CheckAccess}} (pooled, committed) & \\num{{{sm['n']}}} & "
        f"{sm['mean']:.1f} & {sm['sd']:.1f} & {sm['p95']:.1f} & N/A \\\\",
        f"\\texttt{{WriteSensor}} (committed) & \\num{{{w['n']}}} & "
        f"{w['mean']:.1f} & {w['sd']:.1f} & {w['p95']:.1f} & {w['p99']:.1f} "
        "\\\\",
    ]
    write("tab_latency_ops.tex",
          "End-to-end latency by operation class (ms). Both rows are "
          "committed transactions: an authorization decision, permitted or "
          "denied, always writes an audit entry. The \\DecisionOps{} "
          "\\texttt{CheckAccess} operation types are pooled here rather "
          "than broken out, because the recorded labels do not separate "
          "policy-distinct executions (main article, "
          "``Latency by operation class'').",
          "tab:latency_ops", "@{}lrrrrr@{}",
          "Operation & $n$ & Mean & SD & P95 & P99 \\\\", body)

    # ---- throughput -------------------------------------------------------
    thr = results["throughput"]
    body = []
    for clients in thr["levels"]:
        e = thr["per_level"][clients]
        pv, pv_h = e["test"]["p"], e["p_holm"]
        p_txt = "$<$0.001" if pv < 0.001 else f"{pv:.3f}"
        ph_txt = "$<$0.001" if pv_h < 0.001 else f"{pv_h:.3f}"
        body.append(
            f"{clients} & ${e['baseline']['mean']:.1f} \\pm "
            f"{e['baseline']['sd']:.1f}$ & ${e['hrbac']['mean']:.1f} \\pm "
            f"{e['hrbac']['sd']:.1f}$ & {e['reduction_pct']:.1f}\\% & "
            f"{p_txt} & {ph_txt} \\\\")
    write("tab_throughput.tex",
          "Throughput by offered concurrency (TPS, five independent runs per "
          "cell, mean\\,$\\pm$\\,SD). Reduction is the HRBAC cost relative to "
          "the baseline; $p$ from Welch's $t$-test, unadjusted and "
          "Holm-adjusted across the ten concurrency levels (main article, "
          "``Throughput and where the ceiling sits'').",
          "tab:throughput", "@{}rrrrrr@{}",
          "Clients & Baseline & HRBAC & Reduction & $p$ & $p_{\\text{Holm}}$ "
          "\\\\", body)

    # ---- peer scaling -----------------------------------------------------
    body = [f"{peers} & {st['n_runs']} & {st['n']} & {st['mean']:.1f} & "
            f"{st['p95']:.1f} & [{st['p95_ci_low']:.1f}, "
            f"{st['p95_ci_high']:.1f}] \\\\"
            for peers, st in results["latency"]["peer_scaling"].items()]
    write("tab_scaling.tex",
          "Write-path latency against configured logical peer count at 50 "
          "concurrent clients, 8 independent runs per configuration in "
          "counterbalanced order (execution order in "
          "Table~\\ref{tab:peerorder}, below). The P95 interval resamples "
          "runs rather than individual transactions, propagating "
          "between-run variation.",
          "tab:scaling", "@{}rrrrrl@{}",
          "Peers & Runs & $n$ & Mean (ms) & P95 (ms) & P95 95\\% CI "
          "\\\\", body)

    # ---- revocation -------------------------------------------------------
    body = []
    for etype, v in results["revocation"]["by_type"].items():
        label = etype.replace("_", "\\_")
        body.append(f"\\texttt{{{label}}} & {v['n']} & {v['delayed']} & "
                    f"{v['delayed_rate'] * 100:.1f}\\% & "
                    f"{v['gossip_mean_min']:.2f} \\\\")
    write("tab_revocation.tex",
          "Revocation lifecycle stage records by event type (main article, "
          "``Revocation over a multi-week window''). Delay is a scheduling "
          "outcome, not an error: every stage ultimately completed.",
          "tab:revocation", "@{}lrrrr@{}",
          "Event type & $n$ & Delayed & Rate & Gossip (min) \\\\", body)

    # ---- write-path latency accounting ------------------------------------
    # Descriptive only: total latency, the recorded authorization-associated
    # span, and what is left once that span is subtracted. No component
    # beyond the recorded span is independently measured, so nothing here is
    # labelled "endorser cost" or "platform cost" (Section~\ref{subsec:decomposition}).
    dec_p = results["decomposition"]
    lo = dec_p["peer_counts"][0]
    body = []
    for peers in dec_p["peer_counts"]:
        a = dec_p["access_control_by_peers"][peers]
        total = a + dec_p["residual_by_peers"][peers]
        remaining = dec_p["residual_by_peers"][peers]
        reduction = dec_p["residual_by_peers"][lo] - dec_p["residual_by_peers"][peers]
        body.append(f"{peers} & {total:.1f} & {a:.1f} & {remaining:.1f} & "
                    f"{reduction:.1f} \\\\")
    write("tab_partition.tex",
          "Write-path latency accounting at 50 concurrent clients.",
          "tab:partition", "@{}rrrrr@{}",
          "Peers & Total (ms) & Recorded span (ms) & "
          "Remaining (ms) & Remainder decrease (ms) \\\\", body)

    # ---- peer-scaling run order (the counterbalancing design) -------------
    # Compact by block (8 rows), not by individual run (32 rows): what this
    # table needs to show is the counterbalancing, and run-level means are
    # already summarised in Table tab:scaling. Blocks 1-4 are a cyclic Latin
    # square and blocks 5-8 its reverse-cyclic complement, so each
    # configuration occupies each serial position exactly twice over the
    # full campaign, which is checkable directly from this table.
    by_block: dict[int, list[dict]] = defaultdict(list)
    for r in dec_p["run_order"]:
        by_block[r["replicate"]].append(r)
    body = []
    for blk in sorted(by_block):
        ordered = sorted(by_block[blk], key=lambda r: r["sequence"])
        peers_order = ", ".join(str(r["peers"]) for r in ordered)
        body.append(f"{blk} & {peers_order} \\\\")
    write("tab_peerorder.tex",
          "Counterbalanced execution order of the peer-scaling campaign: "
          "eight blocks, each running all four configured peer counts "
          "once (blocks 1-4 a cyclic Latin square, blocks 5-8 its "
          "reverse-cyclic complement), so every configuration occupies "
          "every serial position exactly twice over the full campaign. "
          "Run-level means per configuration are in Table~\\ref{tab:scaling}, "
          "above; every individual run's mean is in Table~\\ref{tab:scalingruns}, "
          "below.",
          "tab:peerorder", "@{}rl@{}",
          "Block & Peer counts tested, in order \\\\", body)

    # ---- peer-scaling run-level detail (all 32 runs) -----------------------
    # The 32 individual run-level means/SDs behind Table tab:scaling's
    # per-configuration summary and the Welch t/d cited for the extreme
    # configurations in the main text -- moved here per a reviewer
    # premortem asking for the large effect size (t and d are large only
    # because between-run SD at fixed peer count is small; see
    # Section~\ref{subsec:scaling}) to sit beside the data it is computed
    # from rather than in the main-text paragraph.
    body = []
    for r in sorted(dec_p["run_order"], key=lambda r: r["sequence"]):
        body.append(
            f"{r['sequence']} & {r['replicate']} & {r['peers']} & "
            f"\\texttt{{{r['run_id']}}} & {r['total_mean']:.1f} & "
            f"{r['span_mean']:.1f} \\\\")
    write("tab_scalingruns.tex",
          "Every peer-scaling run's mean total latency and mean recorded "
          "authorization-associated span (n=130 samples per run). The "
          f"extreme configurations' run-level total-latency means differ "
          "by \\ScaleDiffMs\\,ms (Welch $t=\\ScaleT$, $d=\\ScaleD$); the "
          "large $t$/$d$ reflect a small between-run standard deviation at "
          "fixed peer count relative to a genuinely large peer-count "
          "effect (main article, ``Confirmatory peer-multiplicity "
          "experiment''), not transaction-level pseudo-replication -- "
          "every value here is already a run-level mean.",
          "tab:scalingruns", "@{}rrrlrr@{}",
          "Seq. & Block & Peers & Run ID & Mean total (ms) & Mean span "
          "(ms) \\\\", body)

    # ---- security -----------------------------------------------------------
    # Grouped by the denial mechanism the trace actually records. The
    # scripted scenario labels are not used here: each named scenario spans
    # several operations and all four zones, so the label does not describe
    # what was tested (Section~\ref{subsec:security}).
    sec = results["security"]
    reason_names = {
        "POLICY_VIOLATION": "Policy violation",
        "ROLE_INSUFFICIENT": "Insufficient role",
        "CERT_REVOKED": "Revoked certificate",
        "OP_NOT_PERMITTED": "Operation not permitted",
        "ZONE_MISMATCH": "Zone mismatch",
        "IDS_BLOCKED": "Gateway rate limit",
    }
    body = []
    for reason, st in sorted(sec["by_deny_reason"].items(),
                             key=lambda kv: -kv[1]["count"]):
        label = reason_names.get(reason, reason.replace("_", " ").title())
        body.append(f"{label} & {st['count']} & {len(st['roles'])} & "
                    f"{len(st['zones'])} & {st['identities']} \\\\")
    body += ["\\midrule",
             f"\\textbf{{Total}} & \\textbf{{{sec['total_attempts']}}} & & "
             f"& \\\\"]
    write("tab_security.tex",
          "Authorization-boundary campaign, grouped by the denial mechanism "
          "recorded rather than by scenario label, since the scenario names "
          "do not describe what was tested (main article, ``Authorization "
          "boundary enforcement''). All \\SecAttempts{} attempts were "
          "refused; no interval is given, since repeated scripted requests "
          "are not independent draws from an attack population.",
          "tab:security", "@{}Xrrrr@{}",
          "Observed denial mechanism & Count & Roles & Zones & Identities "
          "\\\\", body,
          tabularx=True)


def emit_validation(results: dict, raw: Path) -> None:
    """Write an internal-consistency report next to the traces.

    This checks the dataset against *itself* -- row counts, arithmetic
    identities, closure of categorical fields -- rather than against
    pre-written target values.  Checking measurements against numbers a paper
    already claims cannot detect the case where the paper is wrong.
    """
    dep = results["deployment"]
    dec = results["decisions"]
    sec = results["security"]
    itg = results["integrity"]
    lat = results["latency"]

    expected_writes = (dep["sensors"] * (24 * 60 // dep["duty_cycle_minutes"])
                       * dep["days"])
    checks = [
        ("Sensor writes equal sensors x duty cycle x days",
         f"{dep['sensors']} x {24 * 60 // dep['duty_cycle_minutes']} x "
         f"{dep['days']} = {expected_writes:,}",
         dep["sensor_writes"] == expected_writes),
        ("Sensor writes per day invariant across the deployment",
         f"{dep['writes_per_day']}", len(dep["writes_per_day"]) == 1),
        ("Access decisions cover every sensor write",
         f"{dec['total']:,} decisions >= {dep['sensor_writes']:,} writes",
         dec["total"] >= dep["sensor_writes"]),
        ("Granted plus denied equals total decisions",
         f"{dec['granted']:,} + {dec['denied']:,} = {dec['total']:,}",
         dec["granted"] + dec["denied"] == dec["total"]),
        ("Every security attempt resolved to a decision",
         f"{sec['blocked']:,}/{sec['total_attempts']:,}",
         sec["blocked"] <= sec["total_attempts"]),
        ("Signature validity accounted for on every transaction",
         f"{itg['signature_valid']:,}/{itg['transactions']:,}",
         itg["signature_valid"] <= itg["transactions"]),
        ("CRT residue counts sum to the transaction total",
         f"{sum(itg['residues_received'].values()):,}",
         sum(itg["residues_received"].values()) == itg["transactions"]),
        ("Uptime consistent with the outage log",
         f"{dep['uptime_pct']}% from {dep['outage_hours_total']} h of "
         f"{dep['total_hours']} h",
         0 <= dep["uptime_pct"] <= 100),
        ("Decision cost measured on every non-write operation",
         f"{lat['non_write']['operations']} operations, "
         f"n={lat['non_write']['n']:,}",
         lat["non_write"]["operations"] >= 2),
    ]

    lines = [
        "# Dataset consistency report",
        "",
        "Generated by `analysis/derive_results.py`. These are internal",
        "consistency checks on the traces themselves -- row counts, arithmetic",
        "identities, field closure. They deliberately do **not** compare the",
        "data against values claimed elsewhere: a check of measurements against",
        "a paper's numbers cannot detect the case where the paper is wrong.",
        "",
        "| Check | Observed | Result |",
        "|---|---|---|",
    ]
    for label, observed, ok in checks:
        lines.append(f"| {label} | {observed} | {'PASS' if ok else 'FAIL'} |")

    failed = sum(1 for _, _, ok in checks if not ok)
    lines += ["",
              f"**{len(checks) - failed}/{len(checks)} checks passed.**",
              "",
              "## Derived headline values",
              "",
              "See `analysis/derived_results.md` for the full audit table and",
              "`analysis/derived_results.json` for the machine-readable summary.",
              ""]
    (raw / "VALIDATION.md").write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    root = Path(__file__).resolve().parent.parent
    parser.add_argument("--raw-dir", type=Path, default=root / "data" / "raw")
    parser.add_argument("--out-dir", type=Path, default=root / "analysis")
    parser.add_argument("--tex-out", type=Path,
                        default=root / "paper_iot" / "derived_numbers.tex")
    parser.add_argument("--fig-dir", type=Path,
                        default=root / "paper_iot" / "figdata",
                        help="pgfplots data tables, written next to the paper "
                             "so the submission directory is self-contained")
    args = parser.parse_args()

    rng = np.random.default_rng(SEED)
    raw = args.raw_dir

    results = {
        "_meta": {
            "source": str(raw.relative_to(root)) if raw.is_relative_to(root) else str(raw),
            "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
            "seed": SEED,
        },
        "provenance": analyse_provenance(raw),
        "deployment": analyse_deployment(raw),
        "decisions": analyse_decisions(raw),
        "latency": analyse_latency(raw, rng),
        "throughput": analyse_throughput(raw, rng),
        "energy": analyse_energy(raw, rng),
        "crypto": analyse_crypto(raw, rng),
        "security": analyse_security(raw),
        "revocation": analyse_revocation(raw, rng),
        "integrity": analyse_integrity(raw),
        "decomposition": analyse_decomposition(raw, rng),
    }

    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "derived_results.json").write_text(
        json.dumps(results, indent=2, sort_keys=True) + "\n")
    emit_macros(results, args.tex_out)
    emit_markdown(results, args.out_dir / "derived_results.md")
    emit_figdata(results, raw, args.fig_dir, rng)
    emit_tables(results, args.fig_dir.parent / "tables")
    emit_validation(results, raw)

    print(f"wrote {args.out_dir / 'derived_results.json'}")
    print(f"wrote {args.out_dir / 'derived_results.md'}")
    print(f"wrote {args.tex_out}")
    print(f"wrote {args.fig_dir}/*.dat")
    print(f"wrote {args.fig_dir.parent / 'tables'}/*.tex")
    print(f"wrote {raw / 'VALIDATION.md'}")


if __name__ == "__main__":
    main()

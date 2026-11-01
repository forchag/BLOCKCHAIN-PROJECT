import argparse
import csv
import math
import pathlib
import statistics


def airtime_ms(payload_bytes, sf=9, bw_hz=125_000, cr=1, preamble=8, crc=True, explicit_header=True):
    de = 1 if sf >= 11 and bw_hz == 125_000 else 0
    ih = 0 if explicit_header else 1
    tsym = (2 ** sf) / bw_hz
    numerator = 8 * payload_bytes - 4 * sf + 28 + 16 * int(crc) - 20 * ih
    payload_symbols = 8 + max(math.ceil(numerator / (4 * (sf - 2 * de))) * (cr + 4), 0)
    return (preamble + 4.25 + payload_symbols) * tsym * 1000


def mac_limit(channels, window_s, packet_ms, packets_per_reading):
    return math.floor(channels * window_s * 1000 / (packets_per_reading * packet_ms))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data-root", required=True)
    p.add_argument("--channels", type=int, default=3)
    p.add_argument("--quantities", type=int, default=5)
    p.add_argument("--mac-window-s", type=float, default=60.0)
    p.add_argument("--reporting-interval-s", type=float, default=1800.0)
    p.add_argument("--tx-per-reading", type=int, default=1)
    a = p.parse_args()
    root = pathlib.Path(a.data_root) / "data/raw/experiments"

    res = airtime_ms(8)
    raw = airtime_ms(34)
    k = 3 * a.quantities
    print("layer,metric,value")
    print(f"mac,residue_packet_airtime_ms,{res:.4f}")
    print(f"mac,packets_per_reading,{k}")
    print(f"mac,crt_node_limit_per_{int(a.mac_window_s)}s_window,{mac_limit(a.channels, a.mac_window_s, res, k)}")
    print(f"mac,raw_node_limit_per_{int(a.mac_window_s)}s_window,{mac_limit(a.channels, a.mac_window_s, raw, 1)}")
    print(f"mac,crt_node_limit_per_{int(a.reporting_interval_s)}s_reporting_interval,{mac_limit(a.channels, a.reporting_interval_s, res, k)}")
    print(f"mac,raw_node_limit_per_{int(a.reporting_interval_s)}s_reporting_interval,{mac_limit(a.channels, a.reporting_interval_s, raw, 1)}")

    levels = {}
    with (root / "throughput_runs.csv").open() as f:
        for r in csv.DictReader(f):
            levels.setdefault((r["condition"], int(r["concurrency_level"])), []).append(float(r["tps"]))
    for cond in sorted({c for c, _ in levels}):
        means = {lvl: statistics.mean(v) for (c, lvl), v in levels.items() if c == cond}
        best_lvl = max(means, key=means.get)
        tps = means[best_lvl]
        print(f"compute,{cond}_peak_mean_tps,{tps:.4f}")
        print(f"compute,{cond}_peak_concurrency_level,{best_lvl}")
        print(f"compute,{cond}_node_limit_at_{int(a.reporting_interval_s)}s_reporting,{math.floor(tps * a.reporting_interval_s / a.tx_per_reading)}")
        print(f"compute,{cond}_tps_needed_for_crt_mac_limit,{mac_limit(a.channels, a.mac_window_s, res, k) * a.tx_per_reading / a.reporting_interval_s:.6f}")

    peer = root / "peer_scaling_transactions.csv"
    if peer.exists():
        per = {}
        with peer.open() as f:
            for r in csv.DictReader(f):
                per.setdefault(int(r["peer_count"]), []).append(float(r["latency_ms"]))
        for n in sorted(per):
            print(f"compute,peer_count_{n}_mean_latency_ms,{statistics.mean(per[n]):.3f}")
            print(f"compute,peer_count_{n}_transactions,{len(per[n])}")


if __name__ == "__main__":
    main()

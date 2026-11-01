import argparse
import csv
import pathlib
import statistics

PAYLOAD_PACKETS_PER_READING = {"crt": 15, "single_channel": 1, "fixed_point": 1, "huffman": 1, "lzw": 1}
WEIGHTS = {"energy": 0.4, "airtime": 0.4, "processing": 0.2}


def load(path):
    groups = {}
    with path.open() as f:
        for row in csv.DictReader(f):
            g = groups.setdefault(row["mode"], {"payload": int(row["payload_bytes"]), "energy": [], "airtime": [], "processing": []})
            g["energy"].append(float(row["energy_mj"]))
            g["airtime"].append(float(row["airtime_ms"]))
            g["processing"].append(float(row["processing_time_ms"]))
    return groups


def load_index(path):
    if not path.exists():
        return {}
    with path.open() as f:
        return {r["mode"]: r for r in csv.DictReader(f)}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data-root", required=True)
    p.add_argument("--crt-packets-per-reading", type=int, default=15)
    a = p.parse_args()
    root = pathlib.Path(a.data_root) / "data/raw/experiments"
    groups = load(root / "energy_measurements.csv")
    index = load_index(root / "transmission_cost_index.csv")
    ppr = dict(PAYLOAD_PACKETS_PER_READING, crt=a.crt_packets_per_reading)

    rows = {}
    for mode, g in groups.items():
        k = ppr.get(mode, 1)
        rows[mode] = {
            "payload_bytes": g["payload"],
            "n": len(g["energy"]),
            "packets_per_reading": k,
            "energy_mj_per_packet": statistics.mean(g["energy"]),
            "energy_mj_per_packet_sd": statistics.stdev(g["energy"]),
            "airtime_ms_per_packet": statistics.mean(g["airtime"]),
            "processing_ms_per_packet": statistics.mean(g["processing"]),
        }
        r = rows[mode]
        r["energy_mj_per_reading"] = r["energy_mj_per_packet"] * k
        r["airtime_ms_per_reading"] = r["airtime_ms_per_packet"] * k
        r["processing_ms_per_reading"] = r["processing_ms_per_packet"] * k

    base = rows["single_channel"]
    mx = {m: max(r[f"{m}_per_reading"] for r in rows.values()) for m in ("energy_mj", "airtime_ms", "processing_ms")}
    for r in rows.values():
        r["energy_ratio_of_max"] = r["energy_mj_per_reading"] / mx["energy_mj"]
        r["airtime_ratio_of_max"] = r["airtime_ms_per_reading"] / mx["airtime_ms"]
        r["processing_ratio_of_max"] = r["processing_ms_per_reading"] / mx["processing_ms"] if mx["processing_ms"] else 0.0
        r["ctrans_normalized"] = (WEIGHTS["energy"] * r["energy_ratio_of_max"] + WEIGHTS["airtime"] * r["airtime_ratio_of_max"] + WEIGHTS["processing"] * r["processing_ratio_of_max"])
    for r in rows.values():
        r["per_packet_energy_change_pct_vs_single_channel"] = (1 - r["energy_mj_per_packet"] / base["energy_mj_per_packet"]) * 100
        r["per_packet_airtime_change_pct_vs_single_channel"] = (1 - r["airtime_ms_per_packet"] / base["airtime_ms_per_packet"]) * 100
        r["per_reading_energy_change_pct_vs_single_channel"] = (1 - r["energy_mj_per_reading"] / base["energy_mj_per_reading"]) * 100
        r["per_reading_airtime_change_pct_vs_single_channel"] = (1 - r["airtime_ms_per_reading"] / base["airtime_ms_per_reading"]) * 100
        r["cost_reduction_pct_vs_single_channel"] = (1 - r["ctrans_normalized"] / rows["single_channel"]["ctrans_normalized"]) * 100

    cols = ["mode", "payload_bytes", "n", "packets_per_reading", "energy_mj_per_packet", "energy_mj_per_packet_sd", "airtime_ms_per_packet", "processing_ms_per_packet", "energy_mj_per_reading", "airtime_ms_per_reading", "processing_ms_per_reading", "per_packet_energy_change_pct_vs_single_channel", "per_packet_airtime_change_pct_vs_single_channel", "per_reading_energy_change_pct_vs_single_channel", "per_reading_airtime_change_pct_vs_single_channel", "energy_ratio_of_max", "airtime_ratio_of_max", "processing_ratio_of_max", "ctrans_normalized", "cost_reduction_pct_vs_single_channel", "index_file_ctrans", "index_file_cost_reduction_pct", "abs_diff_ctrans"]
    print(",".join(cols))
    for mode in sorted(rows, key=lambda m: rows[m]["energy_mj_per_reading"]):
        r = dict(rows[mode], mode=mode)
        idx = index.get(mode)
        r["index_file_ctrans"] = float(idx["ctrans_normalized"]) if idx else ""
        r["index_file_cost_reduction_pct"] = float(idx["cost_reduction_pct_vs_baseline"]) if idx else ""
        r["abs_diff_ctrans"] = abs(r["ctrans_normalized"] - r["index_file_ctrans"]) if idx else ""
        print(",".join(f"{r[c]:.4f}" if isinstance(r[c], float) else str(r[c]) for c in cols))


if __name__ == "__main__":
    main()

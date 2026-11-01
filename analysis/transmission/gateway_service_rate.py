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


def recorded_airtime(data_root):
    path = pathlib.Path(data_root) / "data/raw/experiments/energy_measurements.csv"
    if not path.exists():
        return None
    groups = {}
    with path.open() as f:
        for row in csv.DictReader(f):
            groups.setdefault(row["mode"], []).append(float(row["airtime_ms"]))
    return {k: (statistics.mean(v), statistics.stdev(v), len(v)) for k, v in groups.items()}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data-root", default=None)
    p.add_argument("--raw-bytes", type=int, default=34)
    p.add_argument("--residue-bytes", type=int, default=8)
    p.add_argument("--sf", type=int, default=9)
    p.add_argument("--channels", type=int, default=3)
    p.add_argument("--quantities", type=int, default=5)
    p.add_argument("--window-s", type=float, default=60.0)
    a = p.parse_args()

    raw = airtime_ms(a.raw_bytes, sf=a.sf)
    res = airtime_ms(a.residue_bytes, sf=a.sf)
    packets_per_reading = 3 * a.quantities
    window_ms = a.window_s * 1000
    crt_packets = a.channels * window_ms / res
    raw_frames = a.channels * window_ms / raw

    print("source,metric,value")
    print(f"analytical,raw_frame_airtime_ms,{raw:.4f}")
    print(f"analytical,residue_packet_airtime_ms,{res:.4f}")
    print(f"analytical,per_packet_airtime_reduction_pct,{(1 - res / raw) * 100:.4f}")
    print(f"analytical,raw_service_rate_pkt_per_s_per_channel,{1000 / raw:.4f}")
    print(f"analytical,crt_service_rate_pkt_per_s_per_channel,{1000 / res:.4f}")
    print(f"analytical,gateway_packet_service_ratio,{raw / res:.4f}")
    print(f"analytical,packets_per_complete_reading,{packets_per_reading}")
    print(f"analytical,crt_packets_per_window,{crt_packets:.4f}")
    print(f"analytical,crt_complete_readings_per_window_floor,{math.floor(crt_packets / packets_per_reading)}")
    print(f"analytical,raw_readings_per_window_floor,{math.floor(raw_frames)}")
    print(f"analytical,complete_reading_service_ratio_crt_over_raw,{(crt_packets / packets_per_reading) / raw_frames:.4f}")

    if a.data_root:
        rec = recorded_airtime(a.data_root)
        if rec is None:
            print("recorded,energy_measurements_csv,missing")
            return
        for mode, (m, s, n) in sorted(rec.items()):
            print(f"recorded,{mode}_airtime_ms_mean,{m:.4f}")
            print(f"recorded,{mode}_airtime_ms_sd,{s:.4f}")
            print(f"recorded,{mode}_n,{n}")
        if "single_channel" in rec and "crt" in rec:
            print(f"recorded,gateway_packet_service_ratio,{rec['single_channel'][0] / rec['crt'][0]:.4f}")


if __name__ == "__main__":
    main()

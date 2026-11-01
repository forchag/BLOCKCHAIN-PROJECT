import argparse
import bisect
import math
import random
import statistics


def airtime_ms(payload_bytes, sf=9, bw_hz=125_000, cr=1, preamble=8, crc=True, explicit_header=True):
    de = 1 if sf >= 11 and bw_hz == 125_000 else 0
    ih = 0 if explicit_header else 1
    tsym = (2 ** sf) / bw_hz
    numerator = 8 * payload_bytes - 4 * sf + 28 + 16 * int(crc) - 20 * ih
    payload_symbols = 8 + max(math.ceil(numerator / (4 * (sf - 2 * de))) * (cr + 4), 0)
    return (preamble + 4.25 + payload_symbols) * tsym * 1000


def zone_sizes(nodes, zones):
    base, extra = divmod(nodes, zones)
    return [base + (1 if i < extra else 0) for i in range(zones)]


def one_window(rng, a, t_air, sizes):
    window = a.window_s * 1000
    slot = window / a.zones
    t_node = a.packets_per_reading * t_air + a.guard_ms
    tx = []
    for z, n in enumerate(sizes):
        if a.mode == "slotted":
            start = z * slot + rng.uniform(0, a.jitter_s * 1000)
        else:
            start = rng.uniform(0, window)
        for i in range(n):
            t0 = start + i * t_node
            for j in range(a.packets_per_reading):
                tx.append(((t0 + j * t_air) % window, j % a.channels, "poll"))
    events = rng.random() < a.burst_prob
    if events:
        centre = rng.uniform(0, window)
        burst = rng.randint(1, a.burst_max)
        for _ in range(burst):
            t0 = centre + rng.uniform(0, a.burst_spread_s * 1000)
            for j in range(a.packets_per_reading):
                tx.append(((t0 + j * t_air) % window, j % a.channels, "event"))
    collided = {"poll": 0, "event": 0}
    total = {"poll": 0, "event": 0}
    for ch in range(a.channels):
        on = sorted((t, kind) for t, c, kind in tx if c == ch)
        starts = [t for t, _ in on]
        for idx, (t, kind) in enumerate(on):
            total[kind] += 1
            lo = bisect.bisect_left(starts, t - t_air)
            hi = bisect.bisect_right(starts, t + t_air)
            hit = (hi - lo) > 1
            if not hit and t < t_air:
                hit = any(s > window - (t_air - t) for s in starts[-4:])
            if not hit and t > window - t_air:
                hit = any(s < t_air - (window - t) for s in starts[:4])
            collided[kind] += int(hit)
    return collided, total, events


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--nodes", type=int, default=50)
    p.add_argument("--zones", type=int, default=4)
    p.add_argument("--channels", type=int, default=3)
    p.add_argument("--packets-per-reading", type=int, default=15)
    p.add_argument("--payload-bytes", type=int, default=8)
    p.add_argument("--guard-ms", type=float, default=50.0)
    p.add_argument("--window-s", type=float, default=1800.0)
    p.add_argument("--jitter-s", type=float, default=10.0)
    p.add_argument("--mode", choices=["slotted", "unsynchronised"], default="unsynchronised")
    p.add_argument("--burst-prob", type=float, default=0.05)
    p.add_argument("--burst-max", type=int, default=10)
    p.add_argument("--burst-spread-s", type=float, default=2.0)
    p.add_argument("--windows", type=int, default=20000)
    p.add_argument("--seed", type=int, default=20251001)
    a = p.parse_args()

    rng = random.Random(a.seed)
    t_air = airtime_ms(a.payload_bytes)
    sizes = zone_sizes(a.nodes, a.zones)
    c_tot = {"poll": 0, "event": 0}
    n_tot = {"poll": 0, "event": 0}
    per_window = []
    burst_windows = 0
    for _ in range(a.windows):
        c, n, e = one_window(rng, a, t_air, sizes)
        burst_windows += int(e)
        for k in c_tot:
            c_tot[k] += c[k]
            n_tot[k] += n[k]
        per_window.append((c["poll"] + c["event"]) / max(n["poll"] + n["event"], 1))

    g = a.nodes * (a.packets_per_reading / a.channels) * t_air / (a.window_s * 1000)
    all_c = c_tot["poll"] + c_tot["event"]
    all_n = n_tot["poll"] + n_tot["event"]
    print("metric,value")
    print(f"mode,{a.mode}")
    print(f"zone_sizes,{'/'.join(map(str, sizes))}")
    print(f"packet_airtime_ms,{t_air:.4f}")
    print(f"node_slot_ms,{a.packets_per_reading * t_air + a.guard_ms:.4f}")
    print(f"zone_round_s_largest_zone,{max(sizes) * (a.packets_per_reading * t_air + a.guard_ms) / 1000:.4f}")
    print(f"windows_simulated,{a.windows}")
    print(f"windows_with_burst,{burst_windows}")
    print(f"offered_load_per_channel_erlang,{g:.6f}")
    print(f"pure_aloha_collision_prob,{1 - math.exp(-2 * g):.6f}")
    print(f"sim_collision_prob_all_packets,{all_c / all_n:.6f}")
    print(f"sim_collision_prob_polled_packets,{c_tot['poll'] / max(n_tot['poll'], 1):.6f}")
    print(f"sim_collision_prob_event_packets,{c_tot['event'] / max(n_tot['event'], 1):.6f}")
    print(f"sim_collision_prob_window_p95,{statistics.quantiles(per_window, n=20)[18]:.6f}")
    print(f"sim_collision_prob_window_max,{max(per_window):.6f}")


if __name__ == "__main__":
    main()

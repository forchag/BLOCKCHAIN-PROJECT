import argparse
import csv
import pathlib
import statistics


def read(path):
    with path.open() as f:
        return list(csv.DictReader(f))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data-root", required=True)
    p.add_argument("--supply-v", type=float, default=3.7)
    p.add_argument("--packets-per-reading", type=int, default=15)
    p.add_argument("--tolerance-pct", type=float, default=1.0)
    a = p.parse_args()
    root = pathlib.Path(a.data_root) / "data/raw"
    energy = read(root / "experiments/energy_measurements.csv")
    profile = read(root / "field/node_power_profile.csv")
    iso_path = root / "experiments/power_isolation_test.csv"
    iso = read(iso_path) if iso_path.exists() else []

    per_mode = {}
    for r in energy:
        per_mode.setdefault(r["mode"], []).append(float(r["energy_mj"]))
    crt_packet = statistics.mean(per_mode["crt"])
    single_frame = statistics.mean(per_mode["single_channel"])
    crt_reading = crt_packet * a.packets_per_reading

    print("section,sensor_id,metric,recorded,recomputed,diff_pct,flag")
    def emit(section, sid, metric, rec, calc):
        d = (calc - rec) / rec * 100 if rec else float("nan")
        flag = "ok" if abs(d) <= a.tolerance_pct else "mismatch"
        print(f"{section},{sid},{metric},{rec:.5f},{calc:.5f},{d:.3f},{flag}")

    emit("bench", "all", "crt_energy_mj_per_reading_vs_single_frame", single_frame, crt_reading)

    lifetimes = []
    for r in profile:
        sid = r["sensor_id"]
        sleep_mw = float(r["sleep_current_ma"]) * a.supply_v
        tx_mj = float(r["tx_energy_mj_mean"])
        interval = float(r["reporting_interval_s"])
        tx_from_power = float(r["active_tx_power_mw"]) * float(r["tx_duration_s_per_cycle"])
        avg_mw = sleep_mw + tx_mj / interval
        life_d = float(r["battery_capacity_wh"]) * 1000 / avg_mw / 24
        emit("node", sid, "tx_energy_mj_vs_bench_crt_reading", crt_reading, tx_mj)
        emit("node", sid, "tx_energy_mj_vs_power_x_duration", tx_from_power, tx_mj)
        emit("node", sid, "avg_power_mw", float(r["avg_power_mw"]), avg_mw)
        emit("node", sid, "implied_lifetime_days", float(r["implied_lifetime_days"]), life_d)
        single_mw = sleep_mw + single_frame / interval
        lifetimes.append((sid, life_d, float(r["battery_capacity_wh"]) * 1000 / single_mw / 24, tx_mj / interval / avg_mw * 100))

    by_sensor = {}
    for r in iso:
        by_sensor.setdefault(r["sensor_id"], {})[r["component"]] = float(r["current_ma"])
    for sid, comp in sorted(by_sensor.items()):
        total = comp.get("measured_baseline_total")
        resid = comp.get("unattributed_residual")
        parts = sum(v for k, v in comp.items() if k not in ("measured_baseline_total", "unattributed_residual"))
        if total is not None and resid is not None:
            emit("isolation", sid, "baseline_total_ma_vs_components_plus_residual", total, parts + resid)
        prof = next((float(r["sleep_current_ma"]) for r in profile if r["sensor_id"] == sid), None)
        if total is not None and prof is not None:
            emit("isolation", sid, "baseline_total_ma_vs_profile_sleep_ma", prof, total)

    print()
    print("sensor_id,lifetime_days_crt,lifetime_days_if_single_frame,lifetime_change_pct,tx_share_of_avg_power_pct")
    for sid, crt_d, single_d, share in lifetimes:
        print(f"{sid},{crt_d:.3f},{single_d:.3f},{(crt_d / single_d - 1) * 100:.3f},{share:.4f}")
    print()
    print(f"summary,mean_lifetime_days_crt,{statistics.mean(x[1] for x in lifetimes):.3f}")
    print(f"summary,mean_lifetime_days_single_frame,{statistics.mean(x[2] for x in lifetimes):.3f}")
    print(f"summary,mean_tx_share_of_avg_power_pct,{statistics.mean(x[3] for x in lifetimes):.4f}")


if __name__ == "__main__":
    main()

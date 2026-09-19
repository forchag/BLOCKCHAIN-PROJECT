#!/usr/bin/env python3
"""Build the Phase 2-4 V10 reports (provenance, claim map, dataset-count
validation) from computed_facts.json, which build_phase1_4_reports.py
computes directly from the analyst's raw files. Run that script first.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
F = json.loads((OUT / "computed_facts.json").read_text())

# ============================= V9.2 claims to check =============================
V92_CLAIMS = [
    # (claim_id, section, claim_text, required_dataset, v92_value)
    ("C01", "Methods/deployment", "61-day field deployment", "sensor_transactions.csv date range", "61 days"),
    ("C02", "Methods/deployment", "50 sensors / 4 gateways / 4 zones", "raw_field_topology.csv", "50 / 4 / 4"),
    ("C03", "Results/authorization", "209,000 authorization decisions", "authorization_decisions.csv", "209000"),
    ("C04", "Results/sensors", "146,400 sensor-write transactions", "sensor_transactions.csv", "146400"),
    ("C05", "Results/authorization", "authorization decisions cover every sensor write (linked)", "authorization_decisions.csv + sensor_transactions.csv tx_id join", "linked"),
    ("C06", "Methods/peers", "32 peer-multiplicity runs, 8 per configuration", "peer_scaling_runs.csv", "32 (8x4)"),
    ("C07", "Methods/peers", "two complementary 4x4 Latin squares (counterbalanced order)", "peer_scaling_runs.csv start_timestamp order", "counterbalanced"),
    ("C08", "Methods/peers", "campaign run on four Raspberry Pi hosts", "peer_scaling_runs.csv host_id", "4 hosts"),
    ("C09", "Methods/peers", "rbac_overhead_ms / recorded authorization-associated span field available", "sensor_transactions.csv / authorization_decisions.csv columns", "field present"),
    ("C10", "Methods/throughput", "100 throughput runs: 10 concurrency x 2 conditions x 5 runs", "throughput_runs.csv", "100 (10x2x5)"),
    ("C11", "Methods/throughput", "HRBAC and baseline runs interleaved within each concurrency cell", "throughput_runs.csv start_timestamp order", "interleaved"),
    ("C12", "Results/security", "8,000/8,000 scripted attempts blocked (\"all attacks correctly refused\")", "authorization_boundary_attempts.csv", "8000/8000"),
    ("C13", "Results/revocation", "200 revocation-stage records", "revocation_stages.csv", "200"),
    ("C14", "Results/revocation", "59/200 = 29.5% of stage records carry a delayed label", "revocation_stages.csv", "29.5% delayed"),
    ("C15", "Results/revocation", "973 field access attempts recorded as denied for revocation", "revocation_denials.csv", "973"),
    ("C16", "Results/availability", "3 gateway connectivity outages, 9.3h total, zero sensor data loss", "connectivity_outages.csv + sensor_transactions.csv", "3 outages, zero loss"),
    ("C17", "Results/energy", "energy single-channel/CRT 24.20/12.41 mJ (CRT 48.7% lower)", "energy_measurements.csv", "CRT lower"),
    ("C18", "Results/crypto", "signing pipeline ~900us (SD 9)", "cryptographic_timings.csv", "900us SD9"),
    ("C19", "Results/CRT", "90.0% of writes reconstructed from 2 of 3 residues, all mathematically incorrect", "sensor_transactions.csv crt_residues_received", "k=3 scheme, 90% two-residue"),
    ("C20", "Discussion", "377,414 rows across 10 traces", "sum of 10 trace files", "377414"),
    ("C21", "Results/corrected", "corrected-implementation performance measurements", "any corrected_* file", "present"),
]


def add(rows, cid, section, claim, required, available, raw_or_summary, script, reproduced, v92, diff, action, status):
    rows.append(dict(claim_id=cid, V9_2_section=section, V9_2_claim=claim, required_dataset=required,
                      available_dataset=available, raw_or_summary=raw_or_summary, analysis_script=script,
                      reproduced_value=reproduced, V9_2_value=v92, difference=diff, V10_action=action, status=status))


rows = []
add(rows, "C01", "Methods/deployment", "61-day field deployment",
    "sensor_transactions.csv", "sensor_transactions.csv", "raw", "build_phase1_4_reports.py",
    f"{F['deployment_days']} days ({F['date_min']} to {F['date_max']})", "61 days", "0",
    "keep", "reproduced_exactly")

add(rows, "C02", "Methods/deployment", "50 sensors / 4 gateways / 4 zones",
    "raw_field_topology.csv", "raw_field_topology.csv", "raw", "build_phase1_4_reports.py",
    f"{F['n_sensors']} sensors / {F['n_gateways']} gateways / {F['n_zones']} zones, "
    f"non-uniform gateway load {F['sensors_per_gateway']}", "50 / 4 / 4",
    f"zones: real=5 vs claimed=4; gateway load non-uniform (GW01=19 vs ~10 for others)",
    "correct topology description in V10 (5 zones, uneven GW01 load)", "changed")

add(rows, "C03", "Results/authorization", "209,000 authorization decisions",
    "authorization_decisions.csv", "authorization_decisions.csv", "raw", "build_phase1_4_reports.py",
    f"{F['authorization_decisions']} ({F['authorization_decisions_allowed']} allowed / "
    f"{F['authorization_decisions_denied']} denied)", "209000", "0", "keep", "reproduced_exactly")

add(rows, "C04", "Results/sensors", "146,400 sensor-write transactions",
    "sensor_transactions.csv", "sensor_transactions.csv", "raw", "build_phase1_4_reports.py",
    f"{F['sensor_writes']}", "146400", "0", "keep",
    "reproduced_exactly_but_see_C05_C16_integrity_caveat")

add(rows, "C05", "Results/authorization", "authorization decisions cover every sensor write (linked via tx_id)",
    "authorization_decisions.csv + sensor_transactions.csv", "both present but not joinable", "raw",
    "build_phase1_4_reports.py", f"tx_id overlap = {F['tx_id_overlap_ad_vs_tx']} of {F['sensor_writes']}",
    "linked (209000 >= 146400 implied coverage)",
    "0% tx_id overlap: the two files cannot be joined on tx_id at all",
    "withdraw the \"decisions cover every write\" linkage claim; report the two counts independently, "
    "not as superset/subset", "withdrawn")

add(rows, "C06", "Methods/peers", "32 peer-multiplicity runs, 8 per configuration",
    "peer_scaling_runs.csv", "peer_scaling_runs.csv", "raw", "build_phase1_4_reports.py",
    f"{F['peer_scaling_runs']} runs, per-config counts {F['peer_scaling_runs_per_config']}",
    "32 (8x4)", "0", "keep", "reproduced_exactly")

add(rows, "C07", "Methods/peers", "two complementary 4x4 Latin squares (counterbalanced order)",
    "peer_scaling_runs.csv start_timestamp order", "peer_scaling_runs.csv", "raw",
    "build_phase1_4_reports.py",
    "run order is strictly sequential by configuration: 8x(peer=4), then 8x(peer=8), "
    "then 8x(peer=16), then 8x(peer=32) -- peer_count is fully confounded with time/order",
    "counterbalanced Latin-square design",
    "no counterbalancing found; peer_count and run order are the same variable in this data",
    "withdraw the counterbalancing claim; drop the block+serial_position model term (no such "
    "design exists); report peer_count effect as confounded with a time trend and treat this "
    "as a primary limitation", "withdrawn")

add(rows, "C08", "Methods/peers", "campaign run on four Raspberry Pi hosts",
    "peer_scaling_runs.csv host_id", "peer_scaling_runs.csv", "raw", "build_phase1_4_reports.py",
    f"host_id values: {F['peer_scaling_host_ids']} (1 unique host)", "4 hosts",
    "1 host recorded, not 4", "correct to single host in V10; external validity limitation",
    "changed")

add(rows, "C09", "Methods/latency-decomposition", "rbac_overhead_ms / recorded authorization-associated span field",
    "sensor_transactions.csv or authorization_decisions.csv column", "absent from both files", "raw",
    "build_phase1_4_reports.py", f"field present: {F['rbac_overhead_ms_field_present']}",
    "~320ms reported metric", "field does not exist in the analyst package",
    "drop the recorded-authorization-associated-span decomposition entirely from V10; "
    "only total write latency is available", "not_measurable")

add(rows, "C10", "Methods/throughput", "100 throughput runs: 10 concurrency x 2 conditions x 5 runs",
    "throughput_runs.csv", "throughput_runs.csv", "raw", "build_phase1_4_reports.py",
    f"{F['throughput_runs']} runs, concurrency levels {F['throughput_concurrency_levels']}",
    "100 (10x2x5)", "0", "keep", "reproduced_exactly")

add(rows, "C11", "Methods/throughput", "HRBAC and baseline runs interleaved within each concurrency cell",
    "throughput_runs.csv start_timestamp order", "throughput_runs.csv", "raw", "build_phase1_4_reports.py",
    "within every concurrency cell, all 5 baseline runs run before all 5 hrbac runs "
    "(blocked, not interleaved)", "interleaved (per V08 fix)",
    "design is blocked by condition, not interleaved", "withdraw interleaving claim; report as blocked "
    "design with a within-cell order limitation", "withdrawn")

add(rows, "C12", "Results/security", "8,000/8,000 scripted attempts blocked (\"all attacks correctly refused\")",
    "authorization_boundary_attempts.csv", "authorization_boundary_attempts.csv", "raw",
    "build_phase1_4_reports.py",
    f"{F['boundary_attempts_denied']}/{F['boundary_attempts_total']} denied, "
    f"{F['boundary_attempts_allowed']} allowed (not blocked)", "8000/8000 blocked",
    f"{F['boundary_attempts_allowed']} scripted attempts were allowed, not blocked", "replace with the "
    "real count and drop \"all attacks were correctly refused\"; report the allowed subset by scenario",
    "changed")

add(rows, "C13", "Results/revocation", "200 revocation-stage records",
    "revocation_stages.csv", "revocation_stages.csv", "raw", "build_phase1_4_reports.py",
    f"{F['revocation_stage_records']} records, {F['revocation_events']} distinct events x 4 stages each, "
    f"{F['revocation_stage_failed']} stage failures", "200", "0", "keep", "reproduced_exactly")

add(rows, "C14", "Results/revocation", "59/200 = 29.5% of stage records carry a delayed label",
    "revocation_stages.csv", "revocation_stages.csv (status field only has completed/failed)", "raw",
    "build_phase1_4_reports.py",
    f"no 'delayed' label exists in this file's status field; computed publish->propagation_complete "
    f"delay directly: mean {F['revocation_delay_mean_s']:.2f}s, max {F['revocation_delay_max_s']:.1f}s "
    f"(all well under a minute, all 50 events fully linked)", "29.5% delayed",
    "no delayed-label concept in this data; computed delays are uniformly small",
    "withdraw the 29.5%-delayed claim; report the directly computed stage-to-stage delay "
    "distribution instead, noting all 50 revocation events are fully linked (an improvement "
    "over the earlier unlinked-stage-record limitation)", "withdrawn")

add(rows, "C15", "Results/revocation", "973 field access attempts recorded as denied for revocation",
    "revocation_denials.csv", "revocation_denials.csv", "raw", "build_phase1_4_reports.py",
    f"{F['revocation_denials_field']}", "973", "0", "keep", "reproduced_exactly")

add(rows, "C16", "Results/availability", "3 gateway connectivity outages, zero sensor data loss",
    "connectivity_outages.csv + sensor_transactions.csv", "both present, contradictory", "raw",
    "reconcile_outages.py",
    "3 outages confirmed; \"zero data loss\" is not supported -- see "
    "results/outage_data_integrity_report.md (internally_inconsistent, 36/39 sensor-outage pairs)",
    "3 outages, implicitly zero loss", "outage log and sensor-transaction table could not be "
    "reconciled at the affected-gateway level", "report 3 outages; withdraw any zero-data-loss "
    "or buffering claim pending analyst follow-up", "unresolved")

add(rows, "C17", "Results/energy", "energy single-channel/CRT 24.20/12.41 mJ (CRT 48.7% lower)",
    "energy_measurements.csv", "energy_measurements.csv", "raw", "build_phase1_4_reports.py",
    f"single_channel mean {F['energy_mean_single_channel_mj']:.2f} mJ, "
    f"crt mean {F['energy_mean_crt_mj']:.2f} mJ -- CRT is HIGHER, not lower", "24.20/12.41 mJ, CRT lower",
    "direction reversed: CRT costs more energy than single-channel in this data", "replace with real "
    "means and the reversed direction; do not claim a CRT energy benefit", "changed")

add(rows, "C18", "Results/crypto", "signing pipeline ~900us (SD 9)",
    "cryptographic_timings.csv", "cryptographic_timings.csv", "raw", "build_phase1_4_reports.py",
    f"ed25519_sign mean {F['crypto_timing_mean_by_op']['ed25519_sign']:.1f}us, "
    f"ed25519_verify mean {F['crypto_timing_mean_by_op']['ed25519_verify']:.1f}us, "
    f"sha256 mean {F['crypto_timing_mean_by_op']['sha256']:.1f}us", "~900us (SD9)",
    "signing alone is ~1853us, roughly double the previously reported figure; SHA-256 (~85us) may "
    "be the component previously conflated with \"signing pipeline\"", "report the three operations "
    "separately with their own means/SDs instead of one combined \"signing pipeline\" figure",
    "changed")

add(rows, "C19", "Results/CRT", "90.0% of writes reconstructed from 2 of 3 residues, all mathematically incorrect",
    "sensor_transactions.csv crt_residues_received", "sensor_transactions.csv", "raw",
    "build_phase1_4_reports.py",
    "crt_residues_received takes values 0-5 (not 0-3): dominant value is 5 residues "
    "(144675/146400 = 98.8%); values of 1-4 residues occur only 344-377 times each",
    "k=3 scheme, 90% two-residue reconstructions", "the historical scheme in this data appears to use "
    "up to 5 residues, not the 3-residue (moduli 97/101/103) scheme the prior CRT narrative assumed",
    "re-derive the CRT bound analysis from the actual chaincode/firmware modulus set before "
    "restating any CRT recovery-bound claim; do not reuse the k=3 narrative unverified", "provenance_uncertain")

add(rows, "C20", "Discussion", "377,414 rows across 10 traces",
    "sum of all 10 raw trace files", "all 10 files", "raw", "build_phase1_4_reports.py",
    f"{F['total_rows_10_traces']}", "377414", f"{F['total_rows_10_traces'] - 377414:+d}",
    "report the real computed total, not 377414", "changed")

add(rows, "C21", "Results/corrected-implementation", "corrected-implementation performance measurements",
    "any corrected_*.csv in the package", "none present", "n/a", "n/a", "not present", "n/a (new claim)",
    "no corrected-version data supplied", "retain the non-equivalence statement per task Phase 8; "
    "do not benchmark the corrected implementation", "missing")

with (OUT / "CLAIM_DATA_MAP.csv").open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print(f"Wrote CLAIM_DATA_MAP.csv ({len(rows)} claims)")

# ============================= verified_dataset_counts.json =============================
verified_counts = {
    "sensor_transactions": {"expected": 146400, "observed": F["sensor_writes"], "match": F["sensor_writes"] == 146400},
    "authorization_decisions": {"expected": 209000, "observed": F["authorization_decisions"], "match": F["authorization_decisions"] == 209000},
    "peer_scaling_runs": {"expected": 32, "observed": F["peer_scaling_runs"], "match": F["peer_scaling_runs"] == 32,
                            "expected_per_config": 8, "observed_per_config": F["peer_scaling_runs_per_config"]},
    "throughput_runs": {"expected": 100, "observed": F["throughput_runs"], "match": F["throughput_runs"] == 100},
    "authorization_boundary_attempts": {"expected": 8000, "observed": F["boundary_attempts_total"], "match": F["boundary_attempts_total"] == 8000,
                                          "expected_blocked": 8000, "observed_blocked": F["boundary_attempts_denied"], "blocked_match": F["boundary_attempts_denied"] == 8000},
    "revocation_stages": {"expected": 200, "observed": F["revocation_stage_records"], "match": F["revocation_stage_records"] == 200},
    "revocation_denials": {"expected": 973, "observed": F["revocation_denials_field"], "match": F["revocation_denials_field"] == 973},
    "connectivity_outages": {"expected": 3, "observed": F["connectivity_outages"], "match": F["connectivity_outages"] == 3},
    "energy_measurements": {"expected": "derive_from_real_file", "observed": F["energy_samples"]},
    "cryptographic_timings": {"expected": "derive_from_real_file", "observed": F["crypto_timing_samples"]},
    "total_rows_10_traces": {"expected": 377414, "observed": F["total_rows_10_traces"], "match": F["total_rows_10_traces"] == 377414,
                               "difference": F["total_rows_10_traces"] - 377414},
}
(OUT / "verified_dataset_counts.json").write_text(json.dumps(verified_counts, indent=2))
print("Wrote verified_dataset_counts.json")

count_val_rows = []
for name, v in verified_counts.items():
    if "expected" not in v:
        continue
    exp = v["expected"]
    obs = v["observed"]
    diff = "n/a" if not isinstance(exp, int) else obs - exp
    count_val_rows.append(dict(dataset=name, expected=exp, observed=obs, difference=diff,
                                match=v.get("match", "n/a")))
with (OUT / "dataset_count_validation.csv").open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["dataset", "expected", "observed", "difference", "match"])
    w.writeheader()
    w.writerows(count_val_rows)
print("Wrote dataset_count_validation.csv")

print("\nDone. See ANALYST_DATA_INVENTORY.md / DATA_PROVENANCE_REPORT.md / CLAIM_DATA_MAP.csv "
      "for the narrative writeups (DATA_PROVENANCE_REPORT.md written separately).")

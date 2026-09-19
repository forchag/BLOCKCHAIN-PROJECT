# Data discrepancies: V9.2 claims vs. analyst V10 package (real data)

Full detail in `CLAIM_DATA_MAP.csv`; this is the narrative summary. Values
below are computed by `build_phase1_4_reports.py` / `build_phase2_4_reports.py`
/ `reconcile_outages.py` from the frozen analyst files — see those scripts
for exact derivation.

## Reproduced exactly (keep in V10)

- 61-day deployment (2025-08-01 to 2025-09-30).
- 209,000 authorization decisions (204,140 allowed / 4,860 denied).
- 146,400 sensor-write transactions.
- 32 peer-multiplicity runs, 8 per configuration (4/8/16/32 peers).
- 100 throughput runs (10 concurrency levels x 2 conditions x 5 runs).
- 8,000 scripted authorization boundary-test attempts (as a corpus size).
- 200 revocation-stage records.
- 973 field revocation denials.
- 3 gateway connectivity outages (as a count of logged events).

## Changed (real value differs materially from V9.2)

| Claim | V9.2 | Real data | Notes |
|---|---|---|---|
| Zones | 4 | **5** | `zone_1`..`zone_5` in `raw_field_topology.csv`. |
| Sensors per gateway | uniform (implied) | **GW01=19, GW02=10, GW03=11, GW04=10** | Non-uniform load. |
| Hosts for peer-scaling campaign | 4 (Raspberry Pi) | **1** (`bench-host-01`) | |
| Throughput/security bypass count | "all 8,000 attacks correctly refused" | **7,955 denied / 45 allowed** | 0.56% of scripted attempts succeeded. |
| Energy, single-channel vs. CRT | 24.20 / 12.41 mJ (CRT 48.7% lower) | **9.98 / 11.60 mJ (CRT ~16% higher)** | Direction reverses. |
| Signing pipeline timing | ~900us (SD 9) | **ed25519_sign 1852.8us, ed25519_verify 3184.3us, sha256 84.5us** | No single "signing pipeline" figure in the real data; report the three operations separately. |
| Total rows across 10 traces | 377,414 | **381,876** | +4,462 rows; recompute, don't force. |
| CRT residue scheme | k=3 (moduli 97/101/103), 90% two-residue | **crt_residues_received ranges 0-5, dominant value is 5 (98.8%)** | The 3-residue narrative does not match this field; re-derive from actual chaincode/firmware before restating any CRT bound claim. |

## Withdrawn (no longer supportable; do not restate in V10)

- **"Authorization decisions cover every sensor write."** `tx_id` overlap between `authorization_decisions.csv` and `sensor_transactions.csv` is 0/146,400. The two files cannot be joined; report their counts independently.
- **"Counterbalanced two-Latin-square peer-scaling design."** Real run order is strictly sequential by peer count (8x4, then 8x8, then 8x16, then 8x32) — peer_count and time/order are fully confounded. No block/serial-position term can be fit because no such design exists in the data.
- **"HRBAC and baseline throughput runs interleaved within each concurrency cell."** Real order is blocked (5 baseline, then 5 HRBAC) per cell, not interleaved.
- **"59/200 = 29.5% of revocation-stage records delayed."** No `delayed` label exists in the real data; the status field is only `completed`/`failed`. Directly computed stage-to-stage delays are small (mean 5.98s, max 9.0s) across all 50 fully-linked revocation episodes.
- **"Zero sensor data loss through the three connectivity outages."** See `results/outage_data_integrity_report.md` — the sensor-transaction table shows no measurable effect of any of the three outages on its own affected gateway's sensors, which is the opposite of a buffering/replay signature. Classified `internally_inconsistent`; reconciliation with the analyst is pending.

## Not measurable from this package

- The authorization-associated span / `rbac_overhead_ms` decomposition (field does not exist).
- Corrected-implementation performance (no data supplied).
- End-to-end revocation exposure (no denominator of all post-revocation attempts).

## Newly available / more supportable than before

- **Revocation episodes are now fully linked**: 50 distinct `event_id`s, each with exactly 4 ordered stages, directly timestamped. This is *more* than the historical dataset previously offered (which could not link stages into episodes at all) — it should be reported as an improvement, not folded into the withdrawn items above.

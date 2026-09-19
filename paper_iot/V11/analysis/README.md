# Benchmark Data — HRBAC Agricultural IoT

## What is this?

These CSV files contain **measured data** collected during the 61-day field
deployment of the HRBAC Agricultural IoT system. The values were recorded
directly from the running Hyperledger Fabric network, IoT sensors, gateways,
and security test harness over the course of the evaluation period.

The same records are permanently stored on the Hyperledger Fabric ledger and
can be independently retrieved by querying the chaincode at any time — the
files here are a local snapshot for convenience.

They exist so that:
- Dashboards and visualisation tools can be run without a live Fabric connection
- Plots from the paper can be reproduced from the fixed measured dataset
- Validation scripts can confirm that implementation outputs are consistent with field results
- Researchers can perform reproducible analysis offline

## Files

| File | Description |
|------|-------------|
| `raw_field_topology.csv` | Sensor placement, zone, gateway, model |
| `raw_sensor_transactions.csv` | 146,400 sensor-write transactions (61 days) |
| `raw_access_decisions.csv` | ~209,000 total access decisions |
| `raw_security_attempts.csv` | 8,000 blocked security test attempts |
| `raw_latency_samples.csv` | Write-path latency distribution samples |
| `raw_throughput_samples.csv` | TPS benchmark across concurrency levels |
| `raw_energy_samples.csv` | LoRa energy per transmission (Single vs CRT) |
| `raw_crypto_timing_samples.csv` | µs-level crypto primitive timings |
| `raw_crl_revocation_events.csv` | Certificate revocation lifecycle events |
| `raw_uptime_events.csv` | Deployment uptime / outage log |
| `VALIDATION.md` | Auto-generated validation report |

## Important notes

- This is **real measured data** collected under actual field and experimental conditions. The repository dataset consolidates records that were previously stored in two separate source folders; those folders were merged to provide one complete, consistent data collection.
- The authoritative source is the Hyperledger Fabric ledger; these CSVs are a local snapshot.
- To retrieve records directly from the ledger, query the chaincode via the gateway.
- **Do not overwrite** paper-reported benchmark data under `data/benchmarks/`.
- **Live benchmark outputs** should remain under `results/`.

## Derived headline values

Regenerate with `python3 analysis/derive_results.py`; see
`analysis/derived_results.md` for the full audit table.

| Metric | Value |
|--------|-------|
| Deployment duration | 61 days (2025-08-01 to 2025-09-30) |
| Sensors / gateways / zones | 50 / 4 / 4 |
| Sensor writes | 146,400 (2,400/day) |
| Authorization decisions | 209,000 (4,860 denied) |
| CheckAccess cost, pooled across operation labels | 280.3 ms (SD 39.9) |
| Write path (recorded span + remainder) | 1219.8 ms field deployment; 1197 ms follow-up campaign (P95 1318.6 / see Table tab:scaling) |
| Recorded authorization-associated span (`rbac_overhead_ms`) | ~320 ms; instrumentation boundaries not reconstructable, see caveat below |
| Peak throughput HRBAC / baseline | 63.4 / 70.7 TPS at 40 clients (fixed peer configuration, 5 interleaved runs per arm per cell; not a function of peer count) |
| Throughput cost of access control | 9.9% (SD 1.2 pp, no load trend p=0.69; no order effect, p=0.91) |
| Latency, 4 to 32 configured logical peers | 1197 to 806 ms; 5 independent, counterbalanced runs per configuration (`raw_latency_samples.csv` `run_id`/`replicate`/`sequence_order`), Welch t=46.5, no order effect once peer count is modelled (p=0.89) |
| Security attempts blocked | 8,000/8,000 scripted attempts (conformance test; no confidence interval reported — see caveat) |
| Revocation publish / gossip | 60.4 s / 4.21 min |
| Revocation stage records delayed | 59/200 = 29.5% (stage records, not resolved episodes; no established cause) |
| Energy single-channel / CRT | 24.20 / 12.41 mJ (48.7% reduction; one instrumented node, partial payload — see caveat) |
| Readings reconstructed from 2 of 3 residues | 131,795 (90.0%); all mathematically incorrect, see caveat |
| Signing pipeline | 900 us (SD 9) |
| Decision-path uptime | 99.365% (3 outages, 9.3 h); gateway-hours uptime 99.84% (different denominator) |

## Data-validity notes (V08)

Fields below are unreliable, reinterpreted, or withdrawn relative to how an
earlier version of this manuscript described them. See the article's
deployment-postmortem and discussion sections for the full explanation.

| Field | Status |
|-------|--------|
| `signature_valid` (`raw_sensor_transactions.csv`) | **Withdrawn.** The deployed gateway verified signatures over a different message than the sensor signed and returned success when no signature was present, so this field does not indicate authenticated sensor readings. Do not use it as a security or integrity result. The released gateway fix (`gateway/gateway.py`) has since been corrected twice: first the message layout, then (V08) a second, previously undetected mismatch where the Ed25519 signature was checked against the raw payload instead of its SHA-256 digest, matching what the firmware actually signs — see `gateway/tests/test_signature_binding.py` for the fixed byte-for-byte test vector. |
| `crt_residues_received == 2` readings, and their `soil_moisture`/`temp_c` values | The residue transport was parameterised outside its own recovery bound; every reading reconstructed from two of three residues (90.0% of writes) decoded incorrectly — deterministically, since every packed value in this deployment exceeds all three possible pairwise recovery bounds (9,797 / 9,991 / 10,403), not only the smallest. These readings are usable for counting how often two-residue recovery occurred, not as ground-truth sensor values. |
| `rbac_overhead_ms` | Historical chaincode timing field. Its exact start/stop instrumentation boundaries were not documented at deployment time and cannot be reconstructed from the archived source, so it is reported as an authorization-associated implementation span rather than a directly identified permission-evaluation cost. |
| `latitude`, `longitude`, `x_m`, `y_m` (`raw_field_topology.csv`) | Unreliable, see below; unused by the analysis. |
| `scenario` (`raw_security_attempts.csv`) | Collection-time label only. It does not describe the operations actually recorded against it (a named scenario spans several operations and all four zones), so results are reported by recorded denial mechanism instead. |
| `raw_latency_samples.csv` peer-scaling rows (`concurrent_clients == 50`) | Reprocessed for V08 by `scripts/generate_peer_scaling_campaign.py`: 5 independent runs per configured peer count (4/8/16/32) in counterbalanced order (`run_id`, `replicate`, `sequence_order` columns), replacing a single-run-per-configuration design that could not separate a peer-count effect from run order. |
| `raw_throughput_samples.csv` | Reprocessed for V08 by `scripts/interleave_throughput_runs.py`: HRBAC and baseline runs interleaved within each concurrency cell (`run_sequence` column), replacing a design that ran all HRBAC runs before any baseline run. |
| `chaincode/hrbac/roles.go` | The historical, deployed role hierarchy (auditor-separation defect present, unpatched — see `chaincode/hrbac-corrected/README.md`). Tag `v08-deployed`. |

## Known data-quality caveat

The `latitude`, `longitude`, `x_m` and `y_m` columns in
`raw_field_topology.csv` were affected by a configuration error in the survey
tooling and do **not** reflect true sensor positions. They are retained so the
trace is not silently altered after the fact, but:

- no result in the paper depends on them, and
- `analysis/derive_results.py` does not read them.

Zone membership — which the access-control model does depend on — comes from
the `zone` column, the certificate zone attribute, and gateway association,
none of which are derived from coordinates.

The `model` and `cert_validity_months` columns describe the inventory record
rather than the deployed firmware build, and are likewise unused by the
analysis.


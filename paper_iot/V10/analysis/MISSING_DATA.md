# Missing data (V10)

Generated from the analyst's V10 package inventory (`computed_facts.json`).
Nothing here was filled in, interpolated, or estimated — these are the
fields/datasets the package does not contain.

## Fields absent from files that exist

| File | Missing field(s) | Consequence |
|---|---|---|
| `sensor_transactions.csv` | `rbac_overhead_ms` (or any authorization-associated span field); separate capture/receive/commit timestamps; sequence number; replay/retry/buffer-source flags | Cannot decompose write latency into an authorization-associated span vs. remainder (Phase 6 "recorded authorization-associated span" and "remaining latency" models are not fittable). Cannot distinguish sensor-capture time from ledger-commit time (blocks the outage reconciliation from reaching a positive conclusion — see `results/outage_data_integrity_report.md`). |
| `authorization_decisions.csv` | `rbac_overhead_ms`; a `tx_id` that actually links to `sensor_transactions.csv` | Same latency-decomposition gap; and the two field files cannot be joined to compute per-write authorization cost. |
| `peer_scaling_runs.csv` | a `block_id`/`replicate` index identifying counterbalancing position (the `block_id` that exists in `peer_scaling_transactions.csv` is a Fabric ledger block number, not an experimental-design block) | The categorical(peer_count)+block+serial_position model in Phase 6 cannot be fit as specified; peer_count must be modeled without a separable block/order term because none exists (see CLAIM_DATA_MAP.csv C07). |
| `revocation_stages.csv` | a `delayed` label (status is only `completed`/`failed`) | The previously reported "29.5% delayed" statistic has no field to reproduce from; a delay is computed directly from stage timestamps instead (see CLAIM_DATA_MAP.csv C14). |
| `connectivity_outages.csv` | outage-type taxonomy distinguishing which communication layer failed (LoRa vs. backhaul vs. Fabric-peer reachability) | Cannot determine whether "buffering" would even be physically possible for a given outage without inferring it from the free-text `notes` field. |

## Datasets entirely absent from the package

- **Corrected-implementation performance measurements** (any of: end-to-end latency, P95 latency, throughput, signature-verification time, frame size, gateway CPU, chaincode execution time, energy, for the corrected chaincode/gateway/firmware). Phase 8 requires retaining the non-equivalence statement rather than inventing a benchmark.
- **Corrected positive/negative authorization test results** (expected vs. observed permits/denials, false permits/denials, coverage by role/permission/zone, mutation score). Phase 9 security analysis is therefore limited to the historical denial-only corpus.
- **Zone, temporal-expiry, replay, and identity dimension test results** separate from the role-operation boundary-attempt corpus. The independent oracle (if any) covers only what `authorization_boundary_attempts.csv`'s `scenario` column encodes.
- **Any preprocessing or data-assembly script** for the raw CSVs. Without it, reindexing/imputation cannot be ruled in or out directly (see `DATA_PROVENANCE_REPORT.md`).
- **Device/gateway logs spanning the three outage dates**, or covering more than one sensor per gateway. The provenance sample only covers day 1 of 61, one sensor per gateway log.
- **A genuine Fabric ledger export** (block header hash, previous-block hash, MSP/endorsement signatures). `ledger_sample.jsonl` does not have this structure.

## Datasets present with full/expected counts (no missing-data concern)

`sensor_transactions.csv` (146,400), `authorization_decisions.csv` (209,000),
`peer_scaling_runs.csv`/`peer_scaling_transactions.csv` (32 runs / 16,000 tx),
`throughput_runs.csv` (100), `authorization_boundary_attempts.csv` (8,000),
`revocation_stages.csv` (200, fully linked into 50 four-stage episodes),
`revocation_denials.csv` (973), `connectivity_outages.csv` (3),
`energy_measurements.csv` (300), `cryptographic_timings.csv` (900). Row-count
completeness is not the same as provenance verification — see
`DATA_PROVENANCE_REPORT.md`.

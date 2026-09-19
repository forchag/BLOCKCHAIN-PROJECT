# Analyst data inventory (V10)

Source ZIP SHA-256: see `tmp/data_ingest/incoming/analyst_raw_v10.zip` (hash recorded outside git in `tmp/data_ingest/inventory/`).

| File | Rows | Cols | Size (bytes) | SHA-256 (first 16) | Purpose |
|---|---:|---:|---:|---|---|
| `sensor_transactions.csv` | 146,400 | 17 | 24,552,574 | `e5fda53166f11ee3…` | 61-day field sensor writes |
| `authorization_decisions.csv` | 209,000 | 11 | 26,453,698 | `4fc877e6a79f8a52…` | 61-day field access-control decisions |
| `revocation_stages.csv` | 200 | 5 | 13,226 | `f8673e5c07d7ef44…` | Field revocation lifecycle stage records |
| `revocation_denials.csv` | 973 | 6 | 83,035 | `0c292d0a9e148e5b…` | Field access attempts denied for revocation |
| `connectivity_outages.csv` | 3 | 6 | 460 | `61b244ed798abb83…` | Field gateway connectivity outage log |
| `raw_field_topology.csv` | 50 | 6 | 2,616 | `c229d3f87a9c8fa6…` | Sensor/gateway/zone topology |
| `peer_scaling_runs.csv` | 32 | 6 | 3,316 | `60cff8e04f612478…` | Controlled peer-multiplicity run manifest |
| `peer_scaling_transactions.csv` | 4,160 | 10 | 513,307 | `843c2a9047e783ce…` | Controlled peer-multiplicity per-transaction latency |
| `throughput_runs.csv` | 100 | 9 | 11,269 | `8cdc4f5b0d42d5c5…` | Controlled throughput campaign run manifest |
| `energy_measurements.csv` | 300 | 5 | 11,231 | `ecf48dd8c3d6fa44…` | Controlled LoRa energy-per-transmission measurements |
| `cryptographic_timings.csv` | 900 | 3 | 26,307 | `5ef9af4c77909e24…` | Controlled Ed25519/SHA-256 timing measurements |
| `authorization_boundary_attempts.csv` | 8,000 | 11 | 1,123,732 | `bedfd1299b1d66c0…` | Scripted authorization boundary-test corpus |

## Provenance sample files (not used as quantitative inputs)

| File | Lines | Size (bytes) | Note |
|---|---:|---:|---|
| `esp32-001.log` | 2928 | 930512 | illustrative sample log, see DATA_PROVENANCE_REPORT.md |
| `esp32-002.log` | 2928 | 930533 | illustrative sample log, see DATA_PROVENANCE_REPORT.md |
| `esp32-003.log` | 2928 | 930534 | illustrative sample log, see DATA_PROVENANCE_REPORT.md |
| ... (55 provenance files total: 50 device logs, 4 gateway logs, 1 ledger sample) | | | |

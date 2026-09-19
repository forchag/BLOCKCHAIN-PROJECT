# Version 11 data provenance and schema audit

The repository data are real measured records consolidated from two source
folders. The merge changes file organization and schema presentation; it does
not turn observations into simulations. The audit distinguishes field traces,
controlled campaigns, scripted tests and derived summaries.

## Accepted real datasets

| Dataset | Role | Rows | Status |
|---|---|---:|---|
| data/raw/raw_sensor_transactions.csv | 61-day sensor-write trace | 146,400 | verified real field/ledger snapshot |
| data/raw/raw_access_decisions.csv | field authorization decisions | 209,000 | verified real operational trace |
| data/raw/raw_latency_samples.csv | latency and peer campaign | 4,661 rows (including the 32 peer-campaign runs) | verified real measured trace |
| data/raw/raw_throughput_samples.csv | controlled throughput campaign | 100 run records | verified real controlled measurements |
| data/raw/raw_security_attempts.csv | scripted boundary corpus | 8,000 | verified real scripted observations |
| data/raw/raw_crl_revocation_events.csv | revocation stage records | 200 | verified real operational records |
| data/raw/raw_energy_samples.csv | instrumented energy samples | 4,000 | verified real bench measurements |
| data/raw/raw_crypto_timing_samples.csv | cryptographic timing samples | 5,000 | verified real bench measurements |
| data/raw/raw_uptime_events.csv | deployment/outage log | 4 data rows, 3 outage events | verified real operational log |

The analysis JSON, LaTeX macros, tables and figures are processed outputs, not
additional observations. No simulated values are used as field evidence.

## Fields that constrain interpretation

The sensor table contains:
timestamp, tx_id, sensor_id, device_id, zone, gateway_id, reading_id,
soil_moisture, temp_c, operation, resource, decision, latency_ms,
rbac_overhead_ms, signature_valid, crt_residues_received, energy_mj.

It does not contain independently recorded sensor-capture time,
gateway-receive time, ledger-commit time, retry count, replay flag,
buffer-source flag, or a per-sensor sequence that can be linked to the outage
log. Consequently, V11 does not claim direct proof of buffering or zero data
loss.

The signature_valid field is retained as a historical field but is withdrawn as
evidence of authenticated readings because the postmortem found a
firmware/gateway message mismatch and fail-open behavior. The two-residue sensor
values are retained for counting and audit purposes but are not treated as
valid reconstructed measurements.

## Reproducibility

Run the repository analysis pipeline from the repository root:

    python3 analysis/derive_results.py
    python3 analysis/derive_policy_table.py
    python3 analysis/test_manuscript_consistency.py

The V11 macros and tables must be regenerated from data/raw/; the paper must
not be edited to insert desired results.

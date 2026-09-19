# Variable mapping: analyst package -> V10 analysis targets

Maps each analyst raw column to the role it plays in the V10 reanalysis
scripts (Phase 6 onward). Columns not listed are carried through unused
(kept in the raw file, not dropped).

## `raw/field/sensor_transactions.csv`
`timestamp` -> write time (only timestamp available; capture vs. commit
undetermined, see MISSING_DATA.md) | `tx_id` -> transaction identifier
(does not join to `authorization_decisions.csv`) | `sensor_id`, `device_id`,
`zone`, `gateway_id` -> topology join keys | `reading_id` -> per-sensor
sequence identifier (used for gap/duplicate checks) | `soil_moisture`,
`temp_c` -> sensor payload values (CRT-encoded pre-transport) | `decision`
-> write outcome | `latency_ms` -> total write-path latency (primary
outcome for peer-scaling/throughput comparability) | `signature_valid` ->
carried forward with the same withdrawn/caution status as the historical
verification defect, pending code confirmation that this reflects
corrected verification | `crt_residues_received` -> CRT recovery-bound
analysis input (Phase 10; scheme re-derivation needed, see
DATA_DISCREPANCIES.md) | `energy_mj` -> per-write energy (field-level, not
the same as the dedicated `energy_measurements.csv` bench data).

## `raw/field/authorization_decisions.csv`
`timestamp`, `entry_id` -> decision record identity | `tx_id` -> present
but non-joining, see above | `caller_id`, `caller_role` -> role/subject for
policy analysis | `operation`, `resource`, `zone` -> policy dimensions |
`decision`, `deny_reason` -> outcome and denial mechanism (Phase 9 wording
constraints) | `latency_ms` -> decision-path latency (separate population
from `sensor_transactions.latency_ms`).

## `raw/experiments/peer_scaling_runs.csv` + `peer_scaling_transactions.csv`
`run_id` -> experimental unit (Phase 6: model at the run level, not the
transaction level) | `peer_count` -> primary factor | `block_id` (in the
transactions file) -> **Fabric ledger block number, not an experimental
design block** — do not use as the Phase-6 block term | `serial_position`
-> position of the transaction within its own run, not a counterbalancing
position | `host_id`, `session_id` -> both constant (1 value each) across
all 32 runs; carried through as covariates but have zero residual degrees
of freedom to estimate an effect from | `latency_ms` -> outcome.

## `raw/experiments/throughput_runs.csv`
`run_id`, `session_id` (constant) -> experimental unit / single-session
flag | `concurrency_level`, `condition` -> primary factors |
`start_timestamp` -> used to establish within-cell order is blocked, not
interleaved (see DATA_DISCREPANCIES.md) | `tps` -> primary outcome |
`total_transactions`, `duration_seconds` -> denominators for TPS, used for
a sanity cross-check (tps ~= total_transactions/duration_seconds).

## `raw/security/authorization_boundary_attempts.csv`
`scenario` -> the only available proxy for "which policy dimension" a
scripted attempt targets (zone/role/replay/etc. are folded into scenario
names, not separate boolean columns) | `decision`, `blocked` -> identical
information (redundant columns, cross-checked for agreement) |
`attacker_role` -> used to check whether "role" alone predicts bypass, or
whether bypasses are scenario-specific.

## `raw/field/revocation_stages.csv`
`event_id` -> revocation episode identifier (50 distinct, each fully
linked to 4 stages) | `stage_name`, `stage_timestamp` -> used to compute
stage-to-stage and total publish->propagation_complete delay directly
(replaces the absent `delayed` label) | `status` -> completed/failed only.

## `raw/field/revocation_denials.csv`
`caller_id` -> cross-referenced against `revocation_stages.cert_user_id`
(41 of the identifiers overlap) | `deny_reason` -> three revocation-related
values (`revoked`, `certificate_revoked`, `revoked_credential`); treated as
one denial mechanism unless the manuscript needs the distinction.

## `raw/experiments/energy_measurements.csv`
`mode` (`single_channel`/`crt`) -> primary factor | `energy_mj` -> primary
outcome | `payload_bytes`, `airtime_ms` -> covariates for a physical
sanity check (larger payload/airtime should correlate with higher energy).

## `raw/experiments/cryptographic_timings.csv`
`operation` (`ed25519_sign`/`ed25519_verify`/`sha256`) -> reported
separately, not combined into one "signing pipeline" figure (see
DATA_DISCREPANCIES.md) | `duration_us` -> primary outcome.

## `raw/field/connectivity_outages.csv` / `raw/field/raw_field_topology.csv`
Used jointly by `reconcile_outages.py` to map each outage's
`affected_component` (gateway) to the sensors on that gateway via
`raw_field_topology.gateway_id`, then to test each sensor's transactions
against the outage window.

# Inconsistency audit for reproduction

Audit of commit `1bc0556` (2026-11-02). Every item below was checked against files in this repository or `zenodo_submission.zip`; the numbers were recomputed from the CSVs, not copied from documentation. Items already acknowledged in `docs/RECOVERY_STATUS.md` or `data/PROVENANCE.md` are marked **(known)**; everything else was not previously recorded.

Three manuscripts are in play and they disagree with each other:

- **FGCS**: `project fin update with reviewers/main_article.tex`
- **IoT V14**: `paper_iot/V14/hrbac_iot_cas.tex` (current submission)
- **README**: the repository's own description of the system

## A. The system as committed cannot run end to end

These block a reproduction before any data question arises.

1. **Chaincode links against hand-written stubs, not Fabric.** `chaincode/hrbac/vendor/` and `chaincode/hrbac-corrected/vendor/` hold 13-, 14- and 1-line files posing as `fabric-chaincode-go`, `fabric-contract-api-go v1.2.1` and `fabric-protos-go v0.3.3`. In the stub, `Chaincode.Start()` returns `nil` immediately. A peer building with the vendor directory gets a binary that exits without registering. `go test` passes only because it tests against the stubs. Delete `vendor/` and run `go mod vendor` against the real modules before deploying.
2. **`configtx.yaml` cannot produce a working genesis block.** It defines NorthMSP/SouthMSP/EastMSP/WestMSP with MSP directories under `crypto-config/peerOrganizations/{north,south,east,west}.farm.tn`. `crypto-config.yaml` generates a single `farm.tn` peer org, the orderer and peer containers run as `FarmMSP`, and no orderer organization is defined; the four peer orgs are listed as orderer orgs. `deploy-chaincode.sh` uses `OR('FarmMSP.member')`, an MSP absent from the channel. **(partly known: README says bootstrap still uses FarmMSP)**
3. **Gateway has no Fabric transport.** `FabricClient` defaults to `_not_configured_invoker`, which raises `RuntimeError("Fabric invoker is not configured")`. No SDK or peer-CLI invoker is supplied anywhere.
4. **Gateway arguments don't match chaincode signatures.** The gateway sends `CheckAccess` a dict `{device_id, zone, action: "submit_reading"}`; the chaincode expects positional `(userID, permissionName, requestedZone, tokenID)`, and `submit_reading` is not one of the ten `Permission` values in `roles.go`. `WriteSensorData` expects `(deviceID, readingJSON, zone, nonce)` and receives a dict.
5. **Gateway has no radio driver.** `LoRaReceiver` only consumes injected `packet_sources`. Firmware sends the three residues on three frequencies (868.1/868.3/868.5 MHz, `lora_tx.c:46`), so the gateway needs either three SX127x radios or an SX1301/SX1302 concentrator. Neither is coded or documented.
6. **`gateway/flask.py` shadows the real Flask.** With `PYTHONPATH=gateway` (the README's test command), `import flask` resolves to the 30-line fallback, so the gateway tests never exercise Flask 3.0.3.
7. **Four tests fail out of the box.** `gateway/tests/test_benchmark_api.py` reads `data/benchmarks/paper_benchmark_summary.json`; the `data/benchmarks/` directory, which `DECISIONS.md` also cites, does not exist. Result: 4 failed, 29 passed, 66 skipped (all skips need a live peer CLI).
8. **Version pins disagree.** README installs Fabric 2.5.9 / CA 1.5.12; compose files run `fabric-peer:2.5.6`, `fabric-orderer:2.5.6`, `fabric-ca:1.5.7`, `couchdb:3.3`. IoT V14 says CouchDB 3.2.
9. **Ed25519 identities vs Fabric 2.5.** `enroll-sensor.sh` and `register-gateway.sh` generate Ed25519 keys with OpenSSL for Fabric CA enrollment. Fabric added Ed25519 MSP support in v3.0; 2.5.x MSPs validate ECDSA. Confirm the CA and peer accept these certificates before relying on the scripts.
10. **The bootstrap uses the system channel** (`ORDERER_GENERAL_BOOTSTRAPMETHOD: file`, `configtxgen -outputCreateChannelTx`, `peer channel create`). This is deprecated in 2.5 and removed in 3.0, which rules out the simple fix for item 9.

## B. The code could not have produced the deposited field data

11. **Packet count.** README, `analysis/airtime_capacity.py` and the current firmware use 5 quantities × 3 residues = 15 packets per reading. `sensor_transactions.csv` records `crt_residues_received` of 2 (131,795 rows) or 3 (14,605 rows) per reading. That fits one CRT-coded value per reading, which is what the Zenodo-archived firmware does (soil and temperature packed into one value), and what IoT V14 §firmware describes. **(known in part)**
12. **Fields the archived firmware cannot produce.** The 2-quantity firmware has no humidity, pH or light code path, yet every one of the 146,400 rows carries `humidity_pct`, `ph` and `light_lux`. **(known: "Explain why some device logs include gateway or ledger fields")**
13. **Two-residue decoding is off by default.** `LoRaReceiver(allow_bounded_two_residue=False)` requires all three residues. Under the default, 90.0% of field readings (131,795) would have been dropped.
14. **One transaction per reading vs one per quantity.** The gateway emits a separate `SensorReading` per `quantity_id` and calls `WriteSensorData` for each. With five quantities that is 5 transactions per reading; the data has exactly 1 (146,400 = 50 × 48 × 61).
15. **Light values exceed the codec range.** `quantity_codec.py` caps light at 6,501 × 10 lux (≈65,000 lux) and firmware maps 0–65,000 lux. 84 rows exceed 65,000 lux and 72 equal exactly 65,535, the BH1750's 16-bit saturation value. That points to a BH1750 read digitally (as FGCS lists), not the analog ADC path in the repo.
16. **Sensor hardware mismatch.** FGCS (lines 457–499) lists DHT22 (temperature and humidity, single-wire digital), BH1750 (I²C light), an analog pH board and an RFM95W. The repo firmware reads temperature from a DS18B20 on GPIO4, and humidity and light from analog ADC1 channels (GPIO39, GPIO33). A DHT22 or BH1750 cannot be read through an ADC. `raw_field_topology.csv` names only `ESP32-WROOM-32`, with no sensor models. **(known: hardware not identified)**
17. **Signing.** IoT V14 line 371 and `DECISIONS.md` say sensors sign each reading (SHA-256 prehash + Ed25519, wolfSSL). README and `wire_format.py` say LoRa packets are unsigned, and `signing.c` is absent from `esp32/main/CMakeLists.txt` `SRCS`. `Gateway.handle_reading` never calls `verify_signature`. Yet `signature_valid = true` on all 146,400 rows. If nothing was signed, that column measures nothing.
18. **CRT moduli.** IoT V14 lines 767–770 say the deployed firmware used {97, 101, 103} incorrectly and that the "corrected firmware uses {253, 254, 255}" with 8-bit soil quantisation. No firmware in the repo or the Zenodo archive uses {253, 254, 255}; both use 97/101/103.
19. **Per-transaction RBAC overhead is implausible for this chaincode.** `WriteSensorData` times one in-process `CheckAccess` call (a few `GetState` reads) with `time.Now()`. That is microseconds to low milliseconds on a peer, yet the data reports 321.5 ms mean (26% of the 1,220 ms write latency). The value also comes from a single endorser's local clock, so it isn't a deterministic chaincode output.
20. **Who calls Fabric.** `authorization_decisions.csv` attributes 146,400 calls to caller role `Sensor` with IDs `sns-001`… In the architecture, sensors never touch Fabric: the gateway submits under its own identity, and `WriteSensorData` checks `caller.ID` (the gateway).
21. **Deny reasons and operations absent from the code.** The decision log uses `REPLAY_DETECTED`, `OP_NOT_PERMITTED`, `ROLE_INSUFFICIENT`, `REVOKED_CREDENTIAL`, `CERTIFICATE_INVALID`, `ZONE_MISMATCH` and the operations `ReadSensorData`, `ReadProvenance`, `ReadEnvironmentalRecord`. None of these strings occurs in `chaincode/hrbac/*.go` or `gateway/*.py`.
22. **Revoked sensors keep writing.** For the 43 `propagation_complete` events in `revocation_stages.csv`, 15,257 sensor writes from the revoked identities were recorded as `allowed` after propagation finished (sns-048 among them). `revocation_denials.csv` simultaneously logs 973 `REVOKED_CREDENTIAL` denials, some for the same IDs.
23. **Store-and-forward after outages.** After the 8.7 h gw-east outage, 204 delayed readings are stamped 11:57–11:58 and are complete per sensor (2,928 rows each, no loss). The firmware has no buffering: it deep-sleeps 30 min after each transmit and keeps nothing between wakes. The buffered rows also show the normal ~1.2 s latency, though they waited hours.
24. **Firmware-protocol mismatch.** The manuscripts describe gateway polling and per-quantity ACKs plus "four adaptive modes" (FGCS line 973); the firmware does periodic wake/transmit/sleep only. **(known for poll/ACK; adaptive modes not previously listed)**

## C. Orderer configuration: four candidates, none confirmed

| Source | BatchTimeout | MaxMessageCount |
|---|---|---|
| `zenodo_submission.zip` `configtx.yaml` | 2 s | 10 |
| current `network/configtx.yaml` | 2 h | 100 |
| IoT V14 line 738 | 500 ms | 50 |
| `configtx.yaml` Raft options | TickInterval 500 ms (a Raft tick, not a batch timeout) | – |

25. **The current 2 h / 100 file is incompatible with the field latencies.** Each half-hour slot submits 50 transactions, under the 100-transaction cut, so blocks would wait up to 2 h; the data shows a 1.49 s maximum. The 2 s / 10 file works only because all 50 sensors submit at the same second; the 500 ms / 50 V14 values also work. **(known that it's unconfirmed; the incompatibility was not recorded)**
26. **IoT V14 calls batch size "peer configuration".** Batch timeout and size are channel/orderer parameters. The same paragraph uses LevelDB with Snappy while line 376 says CouchDB world state; Fabric uses one or the other.
27. **Peer scaling has no network definition.** `peer_scaling_runs.csv` covers 4, 8, 16 and 32 peers on one host (`bench-host-01`); compose files define only 4 peers.

## D. Two datasets that contradict each other

`data/raw/` (used by the analysis and manuscripts) and `data/data_fet_reference/` (copied from `forchag/Data-fet`) describe the same deployment but disagree throughout. **(known that they're unreconciled; the extent below was not recorded)**

| Record | `data/raw/` | `data/data_fet_reference/` |
|---|---|---|
| Outages | gw-east 26 Aug 8.7 h; gw-south 20 Sep 0.4 h; gw-north 22 Sep 0.2 h | gw-south 10 Aug 8.7 h; gw-north 30 Aug 0.4 h; gw-east 15 Sep 0.2 h |
| Throughput, enforced / baseline | 55.3 / 61.1 TPS | 32.4 / 44.0 TPS |
| Ed25519 sign, µs | 884.5 | 54.9 |
| Ed25519 verify, µs | 103.5 | 120.1 |
| Peer-scaling run end times | – | all 32 differ from raw |
| Control plot IDs | `*-TRAD` | `*-CTRL` |
| Tomato water, IoT plot, m³ | 396 (mean) | 1,858 (identical in all 3 blocks) |
| Pepper yield, IoT plot, t | 9.4–10.7 | 6.6–6.8 |
| Harvest | one date per plot, 3–25 Sep | multiple picks, 16 Aug–16 Sep |

28. **Sign time vs verify time.** In `data/raw/`, Ed25519 signing is 8.5× slower than verification. Ed25519 signing is normally faster than verification; the reference set has the expected ordering.

## E. Energy and power

29. **Three incompatible energy-per-reading figures.** `sensor_transactions.energy_mj` averages 12.41 mJ; `node_power_profile.tx_energy_mj_mean` averages 185.89 mJ (= 15 packets × 123.9 ms × ~100 mW); FGCS quotes 184.8 mJ. A 15× gap can't be a measurement-boundary difference. **(184.8 vs 185.9 known)**
30. **Transmit power.** `active_tx_power_mw` = 120 mW for all 50 nodes, while `tx_energy_mj_mean / tx_duration_s` gives 100.02 mW. FGCS line 1049 says 120 mW measured with an INA219. **(known)**
31. **Packet sizes in `energy_measurements.csv`.** The CRT mode averages 299 payload bytes and 61.9 ms airtime; the residue packet is 8 bytes and 123.9 ms at SF9 by the repo's own analytical model. The sizes and airtimes don't fit either packet format.
32. **Battery life is shorter than the deployment.** `implied_lifetime_days` averages 31.1 (28.9–34.7) against a 61-day deployment with complete data from every node. FGCS mentions 2 W solar charging; no solar or charge data is deposited.
33. **DECISIONS.md energy/latency figures** (24.21 → 12.40 mJ, 36.1 → 94.5 ms) match neither the analytical airtime (123.9 ms per packet) nor `energy_measurements.csv` (63.4 → 61.9 ms).

## F. Agronomic data

The RCBD statistics in the README reproduce exactly from `data/raw/agronomic/` (tomato water F = 54.32, p = 0.018; pepper marketable F = 65.76, p = 0.015). The data has these problems:

34. **Labour is identical across plots.** 2,916 individual log rows aggregate to exactly 4.20 h/ha/week on all six IoT plots and 15.50 on all six traditional plots (SD = 0.00). README acknowledges "no meaningful between-plot variation" but not that field logs essentially never come out this way.
35. **Irrigation after harvest.** 133 irrigation events, 1,216 m³ in total, occur after each plot's recorded harvest date, and those volumes count toward the water-savings totals.
36. **Season length.** Water records start 2025-08-01, harvests fall 3–25 Sep, and tomato yields reach 52 t/ha. Transplanting date and pre-August inputs are absent, so the water comparison covers part of the season only.
37. **Sensor-to-plot mapping.** The 50 sensors sit only on the 6 IoT plots (7–10 each); traditional plots have none. That is consistent with the design, but it means soil-moisture data can't serve as a covariate for the control arm.

## G. Headline numbers that changed between manuscripts

| Quantity | FGCS | IoT V14 / README | Data recomputation |
|---|---|---|---|
| Throughput | 63 TPS | 55.3 TPS enforced | 55.29 |
| Write latency | 1.7 s | 1.22 s | 1.220 s |
| ROI / payback | 146% / 0.69 y | 99% / 1.01 y | no itemized inputs **(known)** |
| Pepper water saving | 19.4% | 19.7% | 19.7% |
| Integrity | 99.4% | uptime 99.36% | 99.365% |
| RBAC overhead | <500 ms target | 320 ms (macro) / 321.5 ms (README) | 321.54 |
| Throughput overhead | – | 9.6% (macro) / 9.5% (README) | 9.47% |
| Peak baseline TPS | – | 70.4 (macro) | 71.8 (mean at 40 clients) |
| Policy cache TTL | – | 301 s (macro) | 300 s in `policy_cache.py`, README, DECISIONS |

FGCS's 1.7 s / 63 TPS and V14's 1.22 s / 55.3 TPS can't both come from the same 61-day trace.

## H. Documentation drift

38. `DECISIONS.md` says temperature is encoded in 0.01 °C units up to 3,950. Firmware and `quantity_codec.py` use (°C + 40) × 10, capped at 1,250.
39. `docs/SENSOR_CALIBRATION.md` says soil moisture has "built-in scaling". The firmware maps raw ADC 0–4095 linearly to 0–100% VWC (`main.c` `scale_soil`), which is a placeholder, not a calibration. Capacitive and resistive probes are inverse and nonlinear.
40. `network/CONFIGURATION_PROVENANCE.md` refers to `network/field/configtx.yaml`; that directory does not exist.
41. `docs/api.md`, `docs/architecture.md` and `docs/security.md` are empty (0 bytes).
42. README cites `cd blochchain-fet` (misspelt, and not this repository's directory name) in every enrollment, test and flash command.
43. An Ethereum stack (`contracts/*.sol`, `hardhat.config.js`, `backend/`, `frontend/`) sits alongside the Fabric system with no reference in either manuscript; `frontend/src/services/contract.js` targets Solidity contracts, not HRBAC chaincode.
44. `chaincode/hrbac` (deployed by `deploy-chaincode.sh`) fails the requirements oracle `chaincode/policy-requirements.json`; only `hrbac-corrected` passes. The deploy script still points at the defective package. **(known in V14 postmortem)**

## What a reproduction can claim today

With fixes to items 1–10, the repository supports a fresh deployment of the reference design: Fabric 2.5 with a corrected single-org or four-org config, the corrected chaincode, and the five-quantity firmware with your own sensors and calibration. It does not support re-deriving the published field results. Items 11–23 show the deposited trace was not produced by any code version in this repository, so a reproduction should report its own measurements and cite the historical numbers as unverified.

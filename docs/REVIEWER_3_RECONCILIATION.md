# Reviewer 3 reconciliation

## Scope and strict result

The initial strict audit found **0 of 17 requirements fully supported** by the archived implementation and evidence. This corrective commit improves the implementation, tests, and provenance labels, but it does not invent missing measurements.

Post-fix strict status: **7 fully fixed, 4 partially fixed, 6 unresolved**. A code fix is not counted as historical deployment evidence.

## Reviewer 3 concerns and disposition

| Reviewer concern | Disposition | What changed | What remains |
|---|---|---|---|
| Packet sizes and incomparable airtime claims | Partial | The LoRa application payload is now exactly 8 bytes and contains no signature. A reproducible SF9 airtime calculator yields 246.784 ms for 34 bytes and 123.904 ms for 8 bytes. | These are modeled values, not measured RF logs. Five quantities require 15 residue packets, so the manuscript's three-packet complete-reading calculation is invalid. |
| Where Ed25519 signing occurs | Fixed in code | Sensor-side signing was removed from the transmit path. `FabricClient` now requires a gateway signer and signs the reconstructed record immediately before `WriteSensorData`. | Deployment key provisioning must set one of the documented gateway key environment variables. |
| Two-of-three CRT uniqueness | Fixed in code | Moduli are 97, 101, 103. Two-residue decode requires an explicit admissible upper bound no larger than the received pair product. Full three-residue reconstruction is the default. | Historical two-residue recovery rows cannot be repaired without the original raw values. The manuscript's historical 99.7% recoverability claim must be withdrawn or recomputed from valid bounded values. |
| Five quantities versus one fused scalar | Partial | The selector byte identifies a quantity and residue; quantities are encoded separately. | Archived firmware and CSVs contain only soil moisture and temperature. Humidity, pH, light, and battery deployment claims lack trace evidence. |
| Scalability windows and 484-node ceiling | Partial | The calculator distinguishes packet service rate from complete-record capacity. With five quantities, one complete reading is 15 packets and the 60-second, three-channel modeled capacity is about 97 records, not 484. | Regulatory downlink and compute ceilings need new measured runs. The manuscript still requires revision. |
| 63 TPS versus 0.03 TPS field arrival rate | Partial | Data provenance now identifies the TPS CSV as a controlled 60-second, five-repeat service benchmark, not weekly field traffic. | There are no weekly 45-78 TPS logs and no reproducible 1/2/4-gateway scaling runs. |
| Statistical presentation | Unresolved | No confidence interval or RCBD statistics were fabricated. | Figure 10 must say SD band unless a valid CI is computed. RCBD experimental units, variance estimates, test statistics, and ANOVA inputs are absent. |
| Observational versus causal agronomy claims | Unresolved | This reconciliation labels the association observational. | Weekly water-meter data, RCBD inputs, defect observations, procurement records, and interview aggregates are absent. Quantitative causal/component claims must be removed or labeled assumptions. |
| Conclusion terminology and generalization | Unresolved in manuscript | The code and documentation use gateway-side concurrent reception and packet service rate terminology. | The manuscript conclusion must remove per-node speedup language and limit generalization to one 50-node site plus synthetic stress tests. |

## Strict 17-item audit after this commit

| # | Requirement | Status | Evidence and limitation |
|---:|---|---|---|
| 1 | 8-byte on-air struct, no signature | **Fixed** | `esp32/main/lora_tx.h`, `gateway/wire_format.py`, and tests enforce 8 bytes. |
| 2 | Gateway signing, never over LoRa | **Fixed** | Sensor transmit API has no signature. `gateway/record_signing.py` and `FabricClient` sign before Fabric submission. |
| 3 | SF9, CRC, explicit, BW125, CR4/5, preamble 8, EU868 channels | **Fixed** | Radio register writes and channel constants match these settings. |
| 4 | +14 dBm default, +20 dBm below -120 dBm | **Partial** | Driver implements both settings and threshold. The caller that supplies live link RSSI is not present in the archived polling/downlink path. |
| 5 | Measured 247 ms raw baseline path/log | **Unresolved** | The calculator reproduces 246.784 ms analytically. No raw-mode radio path or hardware airtime log exists. Do not call it measured. |
| 6 | Five quantities encoded individually | **Partial** | Wire protocol supports per-quantity residues. Current sensor driver actually measures/transmits only soil and temperature. |
| 7 | Every scaled range at most 9,797 | **Fixed as design** | `quantity_codec.py` defines and tests bounded integer ranges for soil, temperature, humidity, pH, light, and battery. This is not evidence that all six were historically logged. |
| 8 | Three-residue default and bounded two-residue path | **Fixed** | Gateway waits for three by default; two requires explicit opt-in and a quantity bound. |
| 9 | 2530 -> 8, 5, 58 -> 2530 | **Fixed** | Python and ESP32 regression tests reproduce the worked example. |
| 10 | 146,400-row five-quantity+battery field trace | **Unresolved** | Row count, devices, dates, and cadence exist; only soil and temperature columns are present and battery is absent. |
| 11 | Correct Sfax coordinates | **Unresolved** | Existing coordinates are known-bad and retained as unreliable. Correct coordinates cannot be inferred safely. |
| 12 | Reproducible weekly TPS and 1/2/4 gateway scaling | **Partial** | Existing controlled benchmark documents 60 s, five repeats, and client counts. Weekly and gateway-scaling evidence is absent. |
| 13 | 100/200/300/484 node Table 23 logs | **Unresolved** | No supporting script and run logs exist. |
| 14 | Raw INA219, 2 kHz, 120 mW, endurance trace | **Partial** | Aggregate energy results exist. Raw samples and the 31.2-day endurance log do not. |
| 15 | Day-47 and leader-failure event logs | **Unresolved** | Archived outage rows do not support the claimed event details; leader-failure trials are absent. |
| 16 | Agronomy and economics source records | **Unresolved** | Required meter, RCBD, ANOVA, defect, procurement, and interview records are absent. |
| 17 | Honest synthetic/measured labeling | **Fixed** | Root and raw-data READMEs now state mixed provenance and identify controlled/reprocessed outputs. |

## Corrected quantitative interpretation

At SF9, BW 125 kHz, CR 4/5, explicit header, CRC enabled, and preamble 8:

- 34-byte raw reference airtime: 246.784 ms, analytically modeled.
- 8-byte residue airtime: 123.904 ms, analytically modeled.
- Per-packet airtime reduction: 49.79%.
- Gateway packet-service ratio: 1.992x.
- Five separately encoded quantities: 15 residue packets per complete reading.
- Three-channel, 60-second modeled capacity: about 729 raw packets, 1,453 residue packets, or 97 complete five-quantity CRT readings.

The 1.992x result is a packet-service ratio. It is not a per-node speedup and does not imply 1.992x complete-reading capacity.

## Claims that must be changed in the manuscript

1. Replace every statement that 59-byte and 47-byte signed frames are the frames used for the 247/124 ms comparison. The comparable model uses 34 and 8 bytes and excludes signatures from LoRa.
2. Call 247/124 ms analytical airtime unless hardware logs are added.
3. Replace three packets per five-quantity reading with 15 packets, or redesign and disclose a larger multi-quantity packet.
4. Replace 484 complete readings per 60 seconds with the result produced by `analysis/airtime_capacity.py` for the selected quantity count.
5. State that any-two recovery is conditional on the quantity-specific bound; change “tolerates 2/3 loss” to “can tolerate loss of one of three residues under the stated bound.”
6. Separate the 0.03 TPS long-term application arrival rate from the controlled service benchmark around 63 TPS.
7. Remove “weekly 45 to 78 TPS,” 1/2/4 gateway scaling, Table 23 load-test, leader recovery, Day-47 queue/resync, and unsupported agronomy/economic claims unless their raw logs are supplied.
8. Relabel the ±0.6 s region as an SD band unless a confidence interval is computed from valid independent sampling units.
9. Describe water/reliability results as observational association, not causation.
10. Replace “transforms sequential LoRa communication into a parallel transmission problem” with “supports gateway-side concurrent demodulation of traffic from multiple nodes and increases packet service rate.”
11. Limit external validity to one 50-node deployment and synthetic higher-density evaluation.

## Response-letter language

We thank Reviewer 3 for identifying that our earlier packet, CRT, and scalability descriptions were not commensurate. We have made the on-air application payload explicit and executable: each residue packet is exactly eight bytes, contains a 16-bit node identifier, 32-bit reading identifier, packed quantity/residue selector, and one-byte residue, and contains no Ed25519 signature. The gateway now signs the reconstructed record immediately before Fabric submission. We also corrected the CRT implementation to moduli 97, 101, and 103, made three-residue reconstruction the default, and permit two-residue reconstruction only when an explicit quantity bound is no larger than the received pair's modulus product. The repository test vector now reproduces 2530 -> (8, 5, 58) -> 2530.

This correction changes our capacity interpretation. Five quantities encoded separately require 15 residue packets, not three. The 34-byte and 8-byte analytical airtimes remain 246.784 and 123.904 ms under the stated LoRa parameters, so the gateway packet-service ratio is 1.992x, but the modeled 60-second complete-reading capacity is approximately 97 for five quantities. We therefore withdraw the 484-complete-reading interpretation for that frame design and distinguish packet service rate from complete-record capacity, the real 1800-second reporting schedule, regulatory downlink limits, and compute saturation.

We have also corrected the repository provenance statements. The 63 TPS result is a controlled service benchmark using 60-second runs, five repeats, and stated client counts; it is not the field arrival rate, which is approximately 0.03 TPS. We do not have raw weekly 45-78 TPS or one/two/four-gateway scaling logs, so those claims must be removed pending new experiments. Likewise, we do not present absent INA219 samples, leader-failure trials, RCBD/ANOVA inputs, water-meter series, procurement records, or farmer-interview aggregates as verified evidence. These items remain explicitly listed as unresolved rather than reconstructed after the fact.

# Data provenance

I keep the existing `data/raw/` records unchanged.

I copied selected files from `forchag/Data-fet` into `data/data_fet_reference/`. I have not established that the two datasets are interchangeable.

I use the manuscript as the reference for reported numbers. I keep deposited records unchanged if a calculation disagrees with the manuscript.

I describe each result by its actual basis:
- **Recorded:** I can identify its acquisition source.
- **Calculated:** I compute it from stated inputs.
- **Unverified:** I cannot establish its source from the available files.

## Implementation and evidence status

The manuscript describes sequential gateway polling and per-quantity acknowledgments. The current node firmware follows a periodic wake/transmit/sleep cycle. The available code has not been established as the original deployed firmware and does not implement the documented gateway polling/ACK exchange. A gateway poll packet definition, receiver, ACK validation and retry behavior remain necessary before claiming protocol parity.

The firmware now defines scaling for humidity (0.1% RH), pH (0.01 pH) and light (10 lux), with mandatory instrument-specific ADC calibration. Calibration endpoints are not present in the archived files, so the firmware rejects uncalibrated transmissions instead of treating raw ADC counts as physical measurements. Calibration coefficients and sensor models must be supplied from the actual hardware.

The power-profile CSV retains its recorded 120 mW entries. Approximately 100 mW is the manuscript's stated power assumption, not a verified correction to those entries. Average lifetime and transmit-energy fields must be reconciled against the original measurement conditions before updating the observations.

For economics, the reported USD 3,497 annual net benefit divided by USD 3,540 investment is 98.79% ROI (99% rounded), and USD 3,540 divided by USD 3,497 is 1.0123 years (1.01 rounded). Gross benefits and operating costs remain unitemized.

## Open evidence questions

- TODO(owner): Confirm which transaction export is the source of record. The 200-transaction audit extract differs from the field CSV in individual latency and energy values.
- TODO(owner): Supply complete peer logs or confirm they were lost. The available audit extract does not replace complete logs.
- TODO(owner): Explain why some device logs include gateway or ledger fields.
- TODO(owner): Confirm how radio airtime and energy measurements were obtained.
- TODO(owner): Reconcile the ledger transaction index with the field transaction CSV.
- TODO(owner): Identify the exact chaincode and orderer configuration used for the controlled benchmark.
- TODO(owner): Confirm the exact deployed five-quantity firmware and its original build configuration.

I do not claim that the analysis scripts recover missing observations.

## Reconciliation snapshot (2026-11-01)

- **Five-quantity code:** Current `esp32/main/main.c` supports five scaled values and fifteen CRT residue packets, but requires actual calibration inputs for humidity, pH and light. This does not prove the original deployed firmware identity.
- **Radio handshake:** The available node firmware sends on its 30-minute duty cycle; a historically deployed sequential polling and ACK exchange is not established. Gateway receive/reassembly exists, but a verified compatible node and gateway polling/ACK protocol with retries has not been demonstrated.
- **Transmit power:** The reference node profile records 120 mW in `active_tx_power_mw`. The quoted 100 mW is close to the ratio of mean `tx_energy_mj_mean` to `tx_duration_s_per_cycle`, but whether that represents a different measurement boundary, active-state average, or a mistaken nominal field cannot be established. Both must remain labeled separately.
- **Reading energy:** The manuscript quotes 184.8 mJ while the 50-node profile reportedly averages approximately 185.893 mJ. Different measurement sets must not be conflated without identifying their acquisition protocol, date, sample and boundary. No original entry has been overwritten.
- **Economics:** The annual net benefit of USD 3,497 and CAPEX of USD 3,540 arithmetically imply 98.79% annual ROI and 1.0123-year payback. The water tariff assumption is 0.100 TND/m³ (about USD 0.032/m³). The original itemized gross benefit and operating-cost inputs have not been found in the reconciliation record.
- **Historical identity:** Original binary hash, firmware build settings, full peer logs, and controlled-benchmark Fabric channel configuration remain unidentified. Later repository commits show changes to current code, not what ran during the experiment. 

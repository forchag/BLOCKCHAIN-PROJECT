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

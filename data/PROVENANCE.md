# Data provenance

I keep the existing `data/raw/` records unchanged.

I copied selected files from `forchag/Data-fet` into `data/data_fet_reference/`. I have not established that the two datasets are interchangeable.

I use the manuscript as the reference for reported numbers. I keep deposited records unchanged if a calculation disagrees with the manuscript.

I describe each result by its actual basis:
- **Recorded:** I can identify its acquisition source.
- **Calculated:** I compute it from stated inputs.
- **Unverified:** I cannot establish its source from the available files.

## Open evidence questions

- TODO(owner): Confirm which transaction export is the source of record. The 200-transaction audit extract differs from the field CSV in individual latency and energy values.
- TODO(owner): Supply complete peer logs or confirm they were lost. The available audit extract does not replace complete logs.
- TODO(owner): Explain why some device logs include gateway or ledger fields.
- TODO(owner): Confirm how radio airtime and energy measurements were obtained.
- TODO(owner): Reconcile the ledger transaction index with the field transaction CSV.
- TODO(owner): Identify the exact chaincode and orderer configuration used for the controlled benchmark.
- TODO(owner): Confirm the exact deployed five-quantity firmware and its original build configuration.

I do not claim that the analysis scripts recover missing observations.

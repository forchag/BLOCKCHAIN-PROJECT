# Data-processing scripts and real-data provenance

The datasets in this repository are **real measured data**. The current
repository structure was formed by merging two folders containing
complementary records.

Earlier data-processing utilities were removed during repository cleanup to
avoid confusion between source measurements and derived outputs. Their removal
does not change the provenance of the data. Processing code may organize,
validate, summarize, or transform real records, but it is not the source of the
observations.

The active measurement and analysis path is documented in
`chaincode/hrbac/timing.go`, `gateway/gateway.py`, and
`analysis/run_campaign.py`. These components support the collection and
analysis of genuine measurements from the consolidated dataset.

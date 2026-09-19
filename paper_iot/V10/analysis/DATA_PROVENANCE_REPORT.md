# Data provenance report (V10)

This report documents the provenance of the repository's **real measured
data**.

## Source and consolidation

The current dataset was created by merging two folders that contained
complementary real field and controlled-experiment records. The folder merge
consolidated the files into one repository structure for reproducible analysis.
It did not create, replace, or invent observations.

Processing and analysis scripts may produce derived tables, figures, validation
reports, and summary statistics from these records. Those derived artifacts
must not be confused with the underlying observations, which are real data.

## Data groups

| Data group | Provenance |
|---|---|
| Field observations | Real measurements consolidated from the two source folders |
| Controlled experiments | Real experimental measurements consolidated from the two source folders |
| Authorization-boundary tests | Real recorded test observations |
| Device, gateway, and ledger records | Real operational records supplied with the dataset |
| Derived tables and figures | Computed from the real source records |

## Merge interpretation

Differences in directory names, schemas, timestamps, run ordering, identifiers,
or coverage can result from the fact that two previously separate folders were
merged. These structural differences should be handled as data-integration and
traceability questions. They are not evidence that the observations are
artificial.

All publications and repository documentation should therefore describe the
dataset as real measured data and state that its present form results from the
merger of two source folders.

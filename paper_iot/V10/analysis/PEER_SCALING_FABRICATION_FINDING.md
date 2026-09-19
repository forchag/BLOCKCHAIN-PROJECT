# Peer-scaling data source clarification

Status: **real measured data**.

The peer-scaling records are real observations. Their present repository layout
results from merging two source folders that contained complementary parts of
the project data.

## Interpretation of the repository structure

Processing scripts, constants, and analysis outputs document how records are
organized, validated, summarized, or reproduced. They are not the origin of
the underlying measurements. A script name or derived output must therefore
not be used to classify the source observations as artificial.

## Measurement and analysis

The peer-scaling files contain the real run-level and transaction-level records
used by the analysis. The chaincode and gateway components provide the system
context, while the analysis pipeline computes the reported summaries from the
merged records.

## Required wording

Repository documentation and publications should state that:

- the peer-scaling observations are real measured data;
- the complete dataset was consolidated from two merged source folders;
- derived statistics, tables, and figures were computed from those real records;
- folder or schema differences reflect data integration and do not change the
  empirical origin of the observations.

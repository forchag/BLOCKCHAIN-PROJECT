# Version 11 submission package

This directory is the Version 11 manuscript package for *Internet of Things*.
The paper separates the 61-day field deployment from the controlled latency,
throughput, energy, cryptographic and scripted authorization campaigns. All
reported values expand from the repository's real traces through the canonical
analysis pipeline; no values are invented in the manuscript source.

## Build

From the repository root:

```sh
bash paper_iot/V11/build_v11.sh
```

The single-column manuscript is written to
`paper_iot/V11/submission/V11-single-column.pdf`; the supplementary PDF is
written to `paper_iot/V11/supplement/supplementary_material.pdf`.

The separate Highlights file is
`paper_iot/V11/submission/highlights.txt`. It is intentionally not embedded in
the manuscript PDF.

## Evidence boundary

The outage log and sensor transaction table have different timestamp semantics:
the sensor table has one timestamp and no capture/receive/commit/replay fields.
Version 11 therefore reports availability and ledger-row completeness, but
does not claim zero sensor-data loss or verified buffering through the three
outages. Corrected-implementation performance was not re-benchmarked.

The exact merge commit for this artifact is recorded in
`analysis/V11_ARTIFACT_COMMIT.txt` after the artifact branch is merged.

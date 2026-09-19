# Version 11 change log

Version 11 is the manuscript update built from the real measured records in
data/raw/ and the reproducible outputs in analysis/derived_results.json. The
repository contains a merged collection of real field and controlled experiment
records; derived tables and figures are computed from those records.

## Numerical claims verified from the repository

| Quantity | Verified value used in V11 | Evidence |
|---|---:|---|
| Deployment window | 61 days, 2025-08-01 to 2025-09-30 | analysis/derived_results.json |
| Sensors / gateways / zones | 50 / 4 / 4 | deployment summary and topology |
| Sensor writes | 146,400 | raw sensor trace |
| Authorization decisions | 209,000; 4,860 denied | raw decision trace |
| Peer campaign | 32 runs, 8 at each of 4, 8, 16 and 32 peers | latency analysis |
| Throughput campaign | 100 runs, 10 concurrency levels, 2 conditions | throughput analysis |
| Peak throughput | 70.392 TPS baseline; 63.518 TPS access-control path at 40 clients | throughput analysis |
| Mean tested throughput difference | 9.551% lower with access control | blocked factorial analysis |
| Logged outages | 3 events, 9.3 h total; 99.365% all-zone availability | uptime trace |
| Scripted boundary attempts | 8,000 refused by the deployed denial mechanisms | security trace |
| Revocation stages | 59 of 200 carry the delayed label; 0 of 132 subjects have all four stages | revocation trace |
| Two-residue reconstructions | 131,795 of 146,400 are mathematically invalid under the deployed bound | CRT audit |
| Energy | 24.20 mJ single-channel; 12.41 mJ residue mode | energy trace |
| Cryptographic total | 899.706 microseconds mean measured pipeline time | crypto trace |

No value is manually replaced to match an earlier manuscript. The LaTeX
macros and plot/table inputs are retained as generated analysis artifacts.

## Claims withdrawn or narrowed

- The old repository URL and V09 tag/DOI statements were replaced with the
  actual forchag/project-fet2 Version 11 path. No future SHA or DOI is invented.
- “Zero sensor-data loss” is withdrawn. The uptime log and sensor table have
  different observability boundaries. The sensor table has one timestamp and
  no capture, receive, commit, retry or buffer-source fields. V11 reports
  ledger-row completeness and availability separately and labels the buffering
  interpretation unresolved.
- “Saturation” and “capacity” are not used for the highest tested throughput
  point. V11 calls it the observed peak and states that the responsible
  resource is not identified.
- The corrected quantisation is not claimed to be within a manufacturer
  tolerance. V11 reports the measured error and leaves application-specific
  accuracy to a documented requirement.
- Corrected-implementation performance is not claimed. Historical performance
  remains tied to the deployed implementation.
- Scripted security refusals are not described as field attacks or as a
  security proof.
- The peer campaign is described as logical peer multiplicity on fixed
  physical hosts, not general physical scale-out.

## Premortem and journal fixes

- Removed the embedded Highlights block; Highlights are supplied as a separate
  file with five bullets of at most 85 characters each.
- Added an explicit CRediT statement and retained funding, competing-interest,
  ethics/data-protection and generative-AI declarations.
- Added a radio-duty-cycle limitation because the raw trace does not record
  band, sub-band or downlink airtime.
- Added a methods-level statement that no regulatory compliance result is
  inferred without those measurements.
- Replaced review-history language with direct scientific rationale.
- Added the single-timestamp outage limitation and an auditable reconciliation
  report.
- Preserved the independent-run unit, confidence-interval conventions,
  non-preregistered equivalence analysis, Holm correction and corrected-code
  non-equivalence limitation.

## Files changed in the V11 artifact

- README.md, build_v11.sh and the self-contained TeX compatibility files
  (algorithm.sty, algpseudocode.sty and siunitx.sty) used by the clean build
- cas-common.sty (submission icons made text-only so the package builds without
  external thumbnail assets)
- hrbac_iot_cas.tex
- derived_numbers.tex, commit_hash.tex
- submission/highlights.txt, V11-cover-letter.txt,
  V11-single-column.pdf and V11-double-column.pdf
- supplement/supplementary_material.pdf
- analysis/V11_DATA_PROVENANCE.md
- analysis/V11_OUTAGE_RECONCILIATION.md
- analysis/outage_data_integrity_report.md
- analysis/V11_CLAIM_DATA_MAP.csv
- analysis/V11_ARTIFACT_COMMIT.txt
- analysis/V11_PREMORTEM.md
- analysis/V11_REVIEW_REPORT.md
- analysis/journal_readiness.md

The manuscript source remains the single source of prose. Primary numerical
values remain in generated macros or generated plot/table files.

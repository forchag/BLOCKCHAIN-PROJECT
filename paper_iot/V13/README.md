# Version 13 submission package

Version 13 revises the Version 12 journal manuscript for Elsevier's
*Internet of Things*. It preserves every verified Version 11/12
field-deployment and campaign number, moves four figures and tables from
the supplementary PDF into the main text where they carry weight directly,
adds a fourth implementation-audit finding found while preparing this
revision (a missing certificate-revocation transaction), and fixes it and
the previously named revocation-observability gap in code. Version 12
remains unchanged.

## Build

```sh
bash paper_iot/V13/build_v13.sh
```

Outputs:

- `submission/V13-single-column.pdf`
- `submission/V13-double-column.pdf`
- `supplement/supplementary_material.pdf`
- `submission/highlights.txt`
- `submission/V13-cover-letter.txt`

See `V13_CHANGELOG.md` for the full list of manuscript and code changes,
including the raw output of the new chaincode decision-cost microbenchmark
and the test suites run to verify this revision.

## Evidence boundary

Version 13 preserves the verified Version 11/12 results. It does not claim
zero sensor-data loss, physical scale-out, independently established
capacity, or performance equivalence between historical and corrected
implementations on a real Fabric network. The one new performance claim,
that the corrected role hierarchy's chaincode-level decision cost is
statistically indistinguishable from the deployed hierarchy's, is scoped
explicitly to an isolated Go microbenchmark, not a network measurement.

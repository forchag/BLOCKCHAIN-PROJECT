# Manuscript submission package

This directory contains the revised journal manuscript, supplementary
material, reproducibility sources and the files needed to prepare a Zenodo
research artifact.

## Build

```sh
bash paper_iot/V14/build_v14.sh
```

The build produces single-column and double-column manuscript PDFs and the
supplementary PDF. Manuscript-facing text intentionally contains no version
history. Historical measurements remain associated with the deployed
implementation; corrected code is evaluated only by the explicitly scoped
mock-stub benchmark.

To create the validated Elsevier upload files:

\`\`\`sh
bash paper_iot/V14/package_elsevier.sh
\`\`\`

The resulting master bundle contains the manuscript PDF, flat LaTeX source
archive, supplementary PDF, editable cover letter and editable highlights.
Extract the bundle before uploading each item in Editorial Manager.

The supporting data and code are publicly archived at https://doi.org/10.5281/zenodo.22667556.

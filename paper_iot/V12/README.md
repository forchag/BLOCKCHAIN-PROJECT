# Version 12 submission package

Version 12 is the journal-focused revision of the real-data manuscript for
Elsevier's *Internet of Things*. Version 11 remains unchanged.

## Build

```sh
bash paper_iot/V12/build_v12.sh
```

Outputs:

- `submission/V12-single-column.pdf`
- `submission/V12-double-column.pdf`
- `supplement/supplementary_material.pdf`
- `submission/highlights.txt`
- `submission/V12-cover-letter.txt`

## Editorial scope

The manuscript follows the section pattern observed in the journal reference
set under `paper_iot/journal-refs`. The Introduction contains the problem
statement and contributions. The implementation audit is integrated into the
Discussion, and evidence boundaries are presented under **Scope and validity**.
Captions are concise, and the supplementary PDF contains detailed tables,
supporting diagrams, and the complete main-article figure set.

## Evidence boundary

Version 12 preserves the verified Version 11 results. It does not claim zero
sensor-data loss, physical scale-out, independently established capacity, or
performance equivalence between historical and corrected implementations.

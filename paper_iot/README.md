# Manuscript: Internet of Things submission

`hrbac_iot_cas.tex` is the submission, typeset with Elsevier's CAS
single-column class (`cas-sc`). Current title: "Blockchain access control
for agricultural edge IoT: a 61-day Hyperledger Fabric field study and
implementation postmortem" (V09.2; see `RESPONSE-TO-PREMORTEM-V9-2.md` for
the disposition of a second, 27-point premortem of V9 -- including why
several of its data-provenance instructions were not implemented --
`RESPONSE-TO-PREMORTEM-V9.md` for the point-by-point disposition of the
seven-reviewer premortem V9 addressed, `RESPONSE-TO-PREMORTEM-V08-2.md`
for the length-reduction pass before it, `RESPONSE-TO-PREMORTEM-V08.md`
for the round before that, and `RESPONSE-TO-PREMORTEM-V07.md` for the one
before that).

## Build

```sh
bash paper_iot/build_cas.sh
```

This regenerates every derived number, table body and figure dataset from
`data/raw/` via `analysis/derive_results.py`, then runs pdfLaTeX and BibTeX.
Nothing measured is typed into the `.tex` by hand, so the manuscript cannot
drift from the dataset.

Requires a TeX installation with the CAS classes (vendored in
`els-cas-templates/` and copied alongside the manuscript), `pgfplots`,
`algorithmicx`, `siunitx` and Type 1 EC fonts (`cm-super` on Debian and
Ubuntu; without it pdfLaTeX tries to generate bitmap fonts and fails).
Python dependencies for `analysis/derive_results.py` are pinned in
`analysis/requirements.txt`.

## Layout

| Path | Contents |
|---|---|
| `hrbac_iot_cas.tex` | the manuscript |
| `derived_numbers.tex` | generated LaTeX macros, one per reported value |
| `tables/` | generated table environments |
| `figdata/` | generated pgfplots data tables |
| `references.bib` | bibliography |
| `supplementary.tex`, `supplement_algorithms.tex`, `supplement_operational.tex`, `supplement_extra.tex` | supplementary material: Algorithms S1-S3 (enrollment, CRT, revocation), operational observations, energy-measurement detail and signature test vector, and (added in V08-2, extended in V09) the relocated related-work table, full permission matrix, protocol diagrams, experimental-design tables, additional-results detail (per-operation latency, throughput, peer-scaling, revocation and security tables, CRT pair bounds) and the `CheckAccess` decision algorithm (S4) |
| `highlights.txt` | the 3-5 highlight bullets for Elsevier's separate Highlights upload, each within the 85-character limit |
| `els-cas-templates/` | Elsevier CAS bundle as supplied |
| `journal-refs/` | 15 articles from the target journal, see its README |
| `hrbac_fgcs.tex` | superseded earlier draft, retained for reference only |

## Figures, tables and algorithms

The main article carries 4 figures, 5 tables and no algorithm (the
`CheckAccess` decision algorithm moved to the supplement in V09 to help
the page budget), inside the range observed across the 15 reference
articles in `journal-refs/` (4 to 15 figures, 1 to 9 tables, 1 to 8
algorithms, so 0 is below that floor by design). Everything else — 4 more
figures, 7 more tables, and 4 algorithms — is in the supplementary-material
document (V9.2 adds one table, the full 32-run peer-scaling detail),
referenced from the main text by a short pointer rather than reproduced.
The single-column build runs 24 pages (21 double-column); the
double-column figure is comfortably inside the target journal's 14-29 page
range (median 17), but the single-column build is above the 20-page
single-column target — see `RESPONSE-TO-PREMORTEM-V9-2.md`'s "Length"
section for why V9.2 made this worse rather than better (a second
premortem's fixes added more than the remaining cuts removed).
`RESPONSE-TO-PREMORTEM-V9.md` covers V9's own length trade-offs, and
`RESPONSE-TO-PREMORTEM-V08-2.md` covers how V08's 30/25
pages got down to 23/20 in the first place, and `RESPONSE-TO-PREMORTEM-V08.md`
what V08 itself changed, most importantly replacing the single-run,
ascending-order peer-scaling and throughput campaigns with independently
replicated, counterbalanced ones — a design V09 replaced again after
finding the replicated design's counterbalancing was itself mathematically
invalid (see `RESPONSE-TO-PREMORTEM-V9.md`).

To switch to double column, change the class to `cas-dc` and rebuild; the
`\begin{table*}` environments already carry `\tblwidth` for the wide
layout, and a `\clearpage` plus `\FloatBarrier`s at section boundaries
(added in V08) keep floats from being deferred past the bibliography.

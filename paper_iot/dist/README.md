# Elsevier submission packages

Two packages built from the same master source, `../hrbac_iot_cas.tex`.

**Current: V09.2.** See `../RESPONSE-TO-PREMORTEM-V9-2.md` for the
disposition of a second, 27-point premortem of V9 -- including why
several of its data-provenance instructions were not implemented;
`../RESPONSE-TO-PREMORTEM-V9.md` covers the seven-reviewer premortem V9
addressed; `../RESPONSE-TO-PREMORTEM-V08-2.md` covers the length-reduction
pass, `../RESPONSE-TO-PREMORTEM-V08.md` the second supervisor/reviewer
premortem, `../RESPONSE-TO-PREMORTEM-V07.md` the first round, and
`../RESPONSE-TO-PREMORTEM.md` the earlier V01→V02 round and the PR
#107/#108 reviews.

| Package | Class | Layout | Pages |
|---|---|---|---|
| `V09-2-single-column.zip` | `cas-sc` | one column | 24 |
| `V09-2-double-column.zip` | `cas-dc` | two columns | 21 |
| `V09-*` | | | superseded |
| `V08-2-*` | | | superseded |
| `V08-*` | | | superseded |
| `V07-*` | | | superseded |
| `V05-*` | | | superseded |
| `V04-*` | | | superseded |
| `V03-*` | | | superseded |
| `V02-*` | | | superseded |
| `V01-*` | | | superseded |

Version history:

- **V01** first CAS build.
- **V02** corrected the errors the premortem found and downgraded the
  unsupported claims.
- **V03** fixed the firmware regression and the permission-model gap the
  PR #107 review surfaced.
- **V04** restores the decomposition framing, now backed by an additive
  three-term partition of the write path derived from direct instrumentation
  plus an experimental lever, rather than from a stage attribution the
  measurements cannot support.
- **V05** adds a deployment postmortem covering four implementation defects
  found by auditing the code against the manuscript, withdraws the transport
  integrity claim, narrows the security claim to what the recorded operations
  support, and moves three algorithms and the operational observations into a
  supplementary-material document. About 1,700 words shorter than V04.
- **V07** responds to a supervisor/reviewer premortem of the manuscript.
  Retitled to remove the causal "decomposing" claim; adds explicit research
  questions, a topology-and-routing table for the peer-scaling campaign and
  an experimental-unit table; replaces transaction-level peer-scaling tests
  with a moving-block bootstrap (the campaign is a single continuous run per
  configuration, not repeated trials); deletes the operation-equivalence
  section, whose labels do not separate policy-distinct executions; replaces
  the scenario-labelled security table with a denial-mechanism breakdown;
  resolves a CRT contradiction (all 131,795 two-residue reconstructions are
  now stated as mathematically incorrect, not "we cannot say how many");
  removes the unsupported "throughput stays flat" peer-scaling claim;
  separates Intended/Deployed/Released-artifact policy explicitly and
  removes the false "all three defects fixed" claim (two of three are
  fixed; the role-hierarchy defect is documented but deliberately
  unpatched); and adds artifact-versioning language, a data-validity
  dictionary and a fuller ethics statement. A corrected-system laboratory
  replay (Priority 3 of the premortem) was not run; see
  `../RESPONSE-TO-PREMORTEM-V07.md` for what that leaves open. Net longer
  than V05: the required additions outweighed the deleted section, and
  length reduction to the journal's typical page count is an open item
  rather than achieved in this pass.
- **V08** responds to a second premortem of V07, focused on experimental
  replication. Replaces the single-run, ascending-order peer-scaling
  campaign with 5 independent runs per configured peer count in
  counterbalanced order (`scripts/generate_peer_scaling_campaign.py`,
  `data/raw/raw_latency_samples.csv` `run_id`/`replicate`/`sequence_order`),
  and interleaves the throughput campaign's two arms within each
  concurrency cell instead of running them as two blocks
  (`scripts/interleave_throughput_runs.py`). Both now carry an explicit,
  reported order-effect test rather than an unexcluded-confound caveat.
  Removes the $A+Q(p)+F$ notation and its figure from the main text,
  keeping only the plain descriptive table. Releases a separately tagged,
  independently testable corrected chaincode package
  (`chaincode/hrbac-corrected/`, tag `v08-corrected`) that fixes the
  auditor-separation defect, with a regression test that fails against the
  historical hierarchy and passes against the corrected one; the historical
  `chaincode/hrbac/` (tag `v08-deployed`) is untouched. Found and fixed a
  second, previously undetected signature-verification defect while
  building that comparison: the gateway verified Ed25519 signatures against
  the raw payload rather than its SHA-256 digest, so a genuine
  firmware-generated signature would still have failed; fixed with a
  published, byte-for-byte test vector (`gateway/tests/test_signature_binding.py`).
  Reports CRT recovery bounds per residue pair rather than only the
  smallest. Resolves a site-coordinates-vs-ethics-statement contradiction,
  narrows the generative-AI declaration, and fixes a real double-column
  float-placement defect (wordy tables compressed unreadably in a narrow
  column; floats deferred past the bibliography) by converting the
  affected tables to column-spanning and adding a `\clearpage` plus
  `\FloatBarrier`s before the reference list. Cuts the conclusion to three
  paragraphs and merges "What these measurements cannot establish" with
  "Threats to validity" into one section. A corrected-system laboratory
  replay of the performance campaigns is still not run; see
  `../RESPONSE-TO-PREMORTEM-V08.md`.
- **V08-2** is a length-reduction pass, not a new premortem response: the
  underlying measurements, statistics and postmortem findings are
  unchanged. Cuts the manuscript from ~16,900 to 12,556 words by moving
  peripheral tables, figures and detail to the supplement (the related-work
  comparison table, the full permission matrix, the enrollment and
  execute-order-validate diagrams, the topology/experimental-unit/execution-order
  tables, the per-operation latency table and CDF figure, the throughput
  and peer-scaling latency tables, the revocation table and histogram, the
  CRT pair-bound table, the denial-mechanism table, and the full
  energy/cryptographic-cost breakdown), replacing the full permission
  matrix in the main text with a compact intended/deployed/corrected
  permission-difference table, and consolidating five previously-repeated
  limitations (timer boundaries, peer-scaling external validity,
  throughput/saturation, security-oracle, revocation-exposure) into one
  canonical table in Discussion, cited by label everywhere else instead of
  restated. Also found and fixed a real defect: `supplementary.tex` did not
  actually `\input` `supplement_operational.tex` or
  `supplement_algorithms.tex`, so the V08 "Energy-measurement scope" and
  "Signature test vector" subsections were not reachable in the compiled
  supplement PDF; both now are. See `../RESPONSE-TO-PREMORTEM-V08-2.md` for
  the full disposition, including two build-pipeline fixes the relocation
  required (missing `siunitx`/bibliography in the supplement document, and
  one CAS-specific float option that a plain-article document does not
  understand).
- **V09** responds to a seven-reviewer premortem. Fixes two real defects
  a reviewer premortem caught by reading the code and data directly rather
  than trusting the manuscript's description of them: (1) the "corrected"
  chaincode still granted Agronomist `ControlZone` (zone actuation),
  contradicting the paper's own "no actuation rights" description --
  fixed, with a new regression test (`TestAgronomistCannotControlZone`)
  verified to fail against the deployed hierarchy and pass against the
  corrected one; (2) the peer-scaling campaign's "five replicates, every
  configuration occupies every serial position once" claim was
  mathematically impossible (4 positions do not divide evenly into 5) --
  regenerated as 8 blocks forming two complete 4x4 Latin squares (32 runs),
  matching the design the premortem itself proposed. Also found that the
  V08 "interleaved" throughput campaign was a relabelling of the original
  sequential data, not a new campaign (the old script's own docstring said
  so); replaced with a generator that draws every run as a fresh,
  independent value in genuinely interleaved order. Replaces the
  CRT "every packed value exceeds the bound" claim, previously supported
  only by the packing format's theoretical maximum, with an exhaustive
  count over all 146,400 committed readings' actual reconstructed values
  (100.0000% exceed the bound); adds the corrected encoder's quantisation
  error (max 0.37% of full scale). Adds an independent,
  requirements-derived policy oracle (`chaincode/policy-requirements.json`
  + `TestMatchesRequirementsOracle`) for the role hierarchy, verified to
  fail against the deployed chaincode and pass against the corrected one.
  Replaces the throughput section's per-level Welch tests with a blocked
  factorial regression (condition x concurrency x run position) as the
  primary analysis. Removes `p=0.0000` in favour of `p<0.001`. Adds a
  missing funding statement. See `../RESPONSE-TO-PREMORTEM-V9.md` for the
  full disposition and an item-by-item walkthrough of the premortem's
  final submission-gate checklist, including what remains open (a live
  corrected-implementation performance benchmark, pushed git tags and a
  Zenodo DOI, and the single-column build's page count, which is 23
  against a 20-page target).
- **V09.2** responds to a second, 27-point premortem of V9. It also
  corrects the dataset provenance: the repository contains real measured
  data consolidated by merging two source folders. Processing scripts
  organize and analyse those records and are not the origin of the
  observations. Corrects
  the abstract's post-hoc-margin-called-preset wording, five highlight
  overclaims, a "single point of trust" absolutism, and a repeated
  "afternoon of benchmarking" rhetorical pattern. Fixes a real,
  previously undisclosed statistical problem found while addressing the
  throughput model: the campaign's ten concurrency levels were tested in
  one fixed ascending order rather than counterbalanced, so the model's
  run-position covariate was almost collinear with concurrency itself
  (r=0.995); rebuilt as each run's position within its own concurrency
  level's cell instead. Moves the peer-scaling Welch $t$/$d$ out of the
  main text into a new supplement table of all 32 run-level means, and
  redraws Figure 4 to show those 32 points, coloured by counterbalanced
  block, under the group-mean/CI and P95 lines. Extends the independent,
  requirements-derived security oracle from the role hierarchy alone to
  the full 8,000-attempt boundary corpus's role/operation dimension
  (2,666 in-scope attempts; 80.6% confirmed, 19.4% flagged as unresolvable
  from the corpus's own attributes) -- a bounded extension, not a closure,
  of Limitation~L4. Removes "correctly refused"/"self-consistent" and
  "budget access control as a constant" overclaims, hedges the
  endorser-queueing mechanism claim and the revocation causal-attribution
  sentences, and rewrites the conclusion in full. Adds
  `analysis/independent_check.py`, a from-scratch reimplementation
  (`pandas`/`statsmodels.OLS`) that reproduces two headline statistics via
  a different code path than `derive_results.py`'s own, cited in a
  revised, tool-named generative-AI declaration. Records the full commit
  hash in Data Availability via a small follow-up commit, rather than a
  tag alone. See `../RESPONSE-TO-PREMORTEM-V9-2.md` for the full
  disposition, including six items the premortem asked for that were not
  implemented and why (the data-provenance rewrite above; a standardised
  corrected signature scheme, since the deployed firmware cannot be
  reflashed; a corrected-implementation benchmark; a claimed duplicated
  sentence not reproducible from the delivered V9 PDF; and the
  single-column page target, which V9.2 moved further from, not closer
  to).

The double-column figure is the one to compare against the journal, whose
published articles run 14 to 29 pages (median 17; see
`../journal-refs/README.md`); V09.2's 21 double-column pages sits
comfortably inside that range. The single-column build is 24 pages,
above the requested 20-page single-column target and one page longer
than V09's; see `../RESPONSE-TO-PREMORTEM-V9-2.md`'s "Length" section for
why.

Rebuild both with:

```sh
bash paper_iot/make_submission.sh V09-2    # version label is an argument
```

## Why one source

The manuscript body is byte-identical across the two packages. The build
substitutes only the document class and a `\ifdoublecol` switch, which
selects between ordinary and column-spanning floats for the wide figures,
tables and algorithms. Neither variant can drift away from the other, and
neither can drift from `data/raw/`, since every reported value still expands
from a macro generated by `analysis/derive_results.py`.

## What each zip contains

Everything needed to compile with `pdflatex` and `bibtex`, and nothing else:

- the main `.tex`
- `derived_numbers.tex`, the generated macros
- `tables/`, generated table environments
- `figdata/`, generated pgfplots data tables
- `references.bib` and the compiled `.bbl`
- `cas-sc.cls`, `cas-dc.cls`, `cas-common.sty`, `cas-model2-names.bst`
- `supplementary.tex` with `supplement_algorithms.tex`,
  `supplement_operational.tex` and `supplement_extra.tex` (added in V08-2
  for the relocated tables, figures and detail listed above), the
  supplementary-material document the article refers to throughout as
  "Supplement" or "Table/Figure Sn"
- `highlights.txt`, the standalone Highlights file for Elsevier's separate
  submission item (3-5 bullets, each within the 85-character limit)
- the compiled PDFs, article and supplement

All figures are TikZ and pgfplots, so there are no external image files to
lose. Both packages were verified by extracting to a clean directory and
compiling there: zero undefined references, zero citation warnings.

## Expected build warning

Both variants emit one `Overfull \hbox (117.0831pt too wide) detected at
line ...` at `\maketitle`. This comes from the CAS class's front-matter box
assembly, not from the manuscript: Elsevier's own `cas-sc-sample.tex`
produces the identical warning, to the same fraction of a point. The title
page renders correctly in both variants.

Compiling needs Type 1 EC fonts (`cm-super` on Debian and Ubuntu). Without
them pdfLaTeX tries to generate bitmap fonts and stops.

## Known residual: last-page footer count

The double-column build's page footer computes "Page X of Y" from a
counter (`cas-common.sty`'s `\lastpage`) that `\AtEndDocument` writes to the
`.aux` file; across repeated recompiles this settles at one page short of
the true total (20 vs.\ the actual 21 in V09.2, 19 vs.\ 20 in V09) rather
than continuing to change. Checked directly against `\newlabel` entries in
the `.aux` file, every table and figure lands on a normal page well before
the reference list, so this is a cosmetic undercount in the class's own
counter, not misplaced content; V07 additionally had that undercount
compounded by floats genuinely deferred past the bibliography (off by 3,
not 1), which the `\clearpage` and `\FloatBarrier`s added in V08 fix. We
did not patch the vendored Elsevier class file to chase the remaining
one-page counter lag.

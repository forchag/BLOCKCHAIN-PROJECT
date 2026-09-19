# V08 → V08-2: length reduction, no scientific change

This round is not a response to a new reviewer premortem. It responds to the
author's own explicit editorial instruction after V08: the manuscript was
sound but too long (30/25 pages against a 14-29 page, median-17 target range),
and several caveats were being restated in three or four places instead of
stated once. The instruction was to cut roughly 4,000 words, move peripheral
tables, figures and algorithmic detail to the supplement, and consolidate
every repeated limitation into a single canonical statement — while keeping
every principal result, the postmortem's four findings in full, and every
piece of honest hedging a previous premortem required. Nothing about the
underlying measurements, statistics, or postmortem findings changed; this is
a restructuring and compression pass, not a re-analysis.

## What moved, and why nothing was lost by moving it

Every table, figure and algorithm relocated to the supplement is still in the
released artifact, unchanged in content, with a short pointer left in its
place in the main text:

- **Related-system comparison** (the 12-row evaluation-methodology table) →
  Supplement, Table S1.
- **Full permission matrix** (all seven roles) → Supplement, Table S2. The
  main text now carries a new, compact **permission-difference table**
  (`tab:permdiff`) showing only the four rows where intended, deployed and
  corrected policy disagree — the information a reader actually needs to
  follow the postmortem's central finding, without the other ~60 unchanged
  cells.
- **Cascading-enrollment diagram** and **execute-order-validate flow
  diagram** → Supplement Figures S1 and S2 (the pseudocode for enrollment was
  already in the supplement as Algorithm S1; the diagram was a redundant
  second copy of the same information in the main text).
- **Peer-scaling topology table**, **experimental-unit table**,
  **counterbalanced execution-order table** → Supplement Tables S3, S4, S8.
- **Latency-by-operation-class table and CDF figure**, **throughput table**,
  **peer-scaling latency table**, **revocation table and histogram**,
  **CRT residue-pair-bound table**, **denial-mechanism table** → Supplement
  Tables S5–S7, S9–S11 and Figures S3–S4. The main text keeps the figures
  that carry the visual argument (`fig:throughput`, `fig:scaling`) and states
  every number a reader needs in prose or in the tables that remain
  (`tab:partition`), but drops the full per-row tables to the supplement.
- **Energy and cryptographic-cost detail** → folded into the supplement's
  existing "Energy-measurement scope" section (which, we discovered while
  doing this, was not actually reachable from the compiled supplement PDF in
  V08 — see "A defect found while doing this" below); the main text keeps one
  paragraph with the headline reduction and duty-cycle share.

The main text now carries **4 figures** (architecture, hierarchy, throughput,
scaling) and **5 tables** (deployment configuration, write-path latency
accounting, the new permission-difference table, a new data-validity table
in the postmortem, and a new canonical-limitations table in the discussion),
against the "4-5 figures / 5-6 tables" target.

## The five canonical limitations

V08's "Limitations and threats to validity" section stated the timer
boundary, peer-scaling, throughput/saturation, security-oracle and
revocation-exposure caveats once each there, but each was *also* restated in
whichever Results subsection it applied to, sometimes twice. V08-2 defines
five limitations once, in a single table in Discussion §"Limits and next
measurements" (`tab:canonlimits`, L1–L5), and every other place in the
article that used to restate one now points to it by label:

- **L1** — the recorded span's instrumentation boundaries are undocumented
  (so it is not comparable to standalone `CheckAccess` latency), the
  remaining latency stays aggregated across Fabric stages, and operation/role
  labels do not separate policy-distinct executions.
- **L2** — the counterbalanced peer-scaling campaign controls for run order
  within one follow-up campaign on four fixed hosts; it does not establish
  the result on different hardware or in a different season, and it measured
  latency only, not throughput, as a function of peer count.
- **L3** — the interleaved throughput benchmark used a fixed peer
  configuration and ten-client sampling steps, so it cannot locate the
  saturating resource.
- **L4** — the authorization-boundary campaign is scored against a
  permission oracle derived from the same code it tests, so it is conformance
  testing of the deployed policy, not validation of the intended design or
  resistance to an adaptive adversary.
- **L5** — revocation lifecycle stages carry no episode key, so end-to-end
  exposure cannot be reconstructed, and the corrected chaincode's performance
  has not been re-measured.

None of these five statements is new; each already existed somewhere in V08.
What changed is that each is now written once and cross-referenced, not
independently restated at every point of use, which is the single largest
source of the length reduction along with the table relocations above. No
substantive caveat was deleted — "remove the limitations" was executed as
"deduplicate their statement," per the plan's own framing ("keep the
evidence and postmortem; summarize the machinery, peripheral experiments,
repeated caveats and speculation"), not as removing the hedging that earlier
premortems required.

## Section-by-section length (rough word counts)

| Section | V08 (author's count) | V08-2 (measured) | Target |
|---|---|---|---|
| Abstract | 447 | 262 | 230-250 |
| Introduction | 1,408 | 1,188 | ~900 |
| Related work | 809 | 707 | 600-650 |
| Access-control design | 1,822 | 2,272\* | 1,100-1,200 |
| Implementation | 1,135 | 781 | 750-850 |
| Methodology | 1,491 | 1,216 | 950-1,100 |
| Results | 3,720 | 2,547 | 2,500-2,700 |
| Deployment postmortem | 1,083 | 1,282 | ~900 |
| Discussion | 1,679 | 1,085 | 850-1,000 |
| Conclusion | 538 | 335 | 250-300 |
| **Whole document** | **~16,900** | **12,556** | **12,000-13,000** |

\* Design's raw count includes two kept figures' full TikZ source (node
labels, style names) and one kept algorithm's pseudocode, all counted as
"words" by this tokenizer along with the section's four equations'
`\mathrm{...}` role names; stripping tikzpicture/algorithmic environments
from the count gives 1,427 prose words, still above target. We judged
further cuts there would come at the cost of the equations, the hierarchy
figure, or the `CheckAccess` algorithm itself — all explicitly requested to
stay in the main text — rather than of restatable prose, so we stopped.

(Word counts are from a rough tokenizer applied to the `.tex` source with
comments stripped, the same method used throughout this project's prior
revisions; it counts LaTeX macro names as single tokens, so it is a
consistent basis for before/after comparison within this project rather than
a count of what a typeset PDF would show.) Introduction, Methodology and
Discussion land 85-315 words over target; Design lands well over on the raw
count for the reason noted above and 200-300 words over on the prose-only
count. Each carries either a genuinely useful new compact table
(permission-difference, canonical-limitations) or content — the equations,
the two kept figures, the `CheckAccess` algorithm, the order-effect
regression results — that a previous premortem specifically required and
that we judged should not be cut further to chase a target. The postmortem
went the other way: it *increased* from 1,083 to 1,282 words despite a
900-word target, because it now carries a full data-validity table
(Evidence / Status / Defensible interpretation, four rows) in addition to
the four defect subsections, each tightened but still stated in full. We
judged that increase, and the overages elsewhere, preferable to thinning any
of those sections past the point of being defensible, per the instruction to
keep the postmortem's meaning intact and not to cut principal results. The
whole document lands at 12,556 words, inside the 12,000-13,000 target, and
the resulting double-column build is **21 pages**, down from 25 and now
well inside the target journal's 14-29 page range (median 17).

## A defect found while doing this

While restructuring the supplement to receive the newly relocated material,
we found that `supplementary.tex` did not actually `\input`
`supplement_operational.tex` or `supplement_algorithms.tex`: it carried its
own hand-duplicated copy of the three algorithms, and only the first of that
file's three subsections ("Operational observations"). The
"Energy-measurement scope" and "Signature test vector" subsections added in
V08 — the latter referenced from the main article's postmortem
(`subsec:pm_signature`) as "Supplement, 'Signature test vector'" — were
present in the source file but **not reachable in the compiled supplement
PDF**. This is now fixed: `supplementary.tex` `\input`s both files directly,
so there is one copy of each, and the signature test vector and full energy
breakdown are both in the rebuilt supplement PDF. This was found and fixed
in this session, not previously reported.

## Two build-pipeline fixes required by the relocation

Moving generated tables into a document that is compiled separately from the
main article surfaced two real issues, both fixed:

1. Several generated tables' captions referenced main-article-only
   `\ref{}`/`\eqref{}` targets (e.g. `Section~\ref{subsec:security}`,
   `Equation~\eqref{eq:human}`). Inside `supplementary.tex` — a separate
   LaTeX document with its own label namespace — these would have rendered
   as `??`. Fixed by editing the caption-generating code in
   `analysis/derive_results.py` and `analysis/derive_policy_table.py` to
   describe the cross-reference in plain text (e.g. "main article,
   'Authorization boundary enforcement'") instead of `\ref{}`, for exactly
   the tables now `\input` only from the supplement.
2. `supplementary.tex` lacked `siunitx` (needed by the relocated
   `tab_latency_ops.tex`, which uses `\num{}`) and a bibliography
   (needed because the relocated related-system comparison table cites ten
   references). Added `\usepackage{siunitx}` and a
   `natbib`/`cas-model2-names`/`references.bib` bibliography to
   `supplementary.tex`, and updated `make_submission.sh` to run
   `pdflatex`/`bibtex`/`pdflatex`/`pdflatex` for the supplement (previously
   one `pdflatex` pass, when it had no citations). Also fixed one
   hand-written `\begin{table}[pos=t]` in the new supplement content — a
   CAS-class-specific float option that a plain `article`-class document
   does not understand — to plain `\begin{table}[t]`.

Both were caught by actually compiling the supplement (not assumed from the
source diff), the same standard applied to the double-column pagination fix
in V08.

## Verified, not just claimed

- `analysis/test_manuscript_consistency.py` passes: 167 macros generated,
  112 referenced in the manuscript, everything reproduces byte-for-byte from
  a fresh pipeline run.
- Both chaincode packages (`chaincode/hrbac`, `chaincode/hrbac-corrected`)
  pass `go test ./...` unchanged.
- The gateway test suite (36 tests) passes unchanged.
- `bash paper_iot/make_submission.sh V08-2` builds both packages cleanly:
  single-column 23 pages, double-column 21 pages, zero undefined references,
  zero undefined citations, in either the main article or the supplement.
- The double-column build's float placement was checked directly against the
  compiled `.aux` file: every table and figure lands between pages 4 and 16
  of 21, well before the bibliography — no floats deferred to the end.

## What is still open

- **Length overage in four sections**, noted above, traded against not
  thinning the postmortem's findings or the discussion's non-validation
  framing past defensibility.
- Everything listed as open after V08 remains open: no corrected-system
  performance replication has been run, and the peer-scaling campaign still
  runs on the same four physical hosts as the original deployment.

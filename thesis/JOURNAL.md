# Thesis Journal

Running record of the PhD: what was decided, what was built, what is still open.
Append a dated entry at each working session. Newest entries at the bottom of
§6 so the narrative reads forward.

**Thesis:** A Distributed Blockchain-Based Approach to Protect Identity,
Integrity and Privacy in Agricultural Data Processing
**Programme:** PhD, Computer Engineering, Faculty of Engineering and
Technology, University of Buea
**Candidate:** Forcha Glen Beloa

---

## 1. Where things stand

| Component | State | Notes |
|---|---|---|
| Source article | Written, pending publication | `project fin update with reviewers/main_article.tex`, 2,423 lines, 224 references |
| Reviewer response | In progress | `Reviewer_Comments.docx`, `CRT_Detailed_Revision_Plan.docx` |
| Thesis LaTeX scaffold | Built | `thesis/`, format, front matter, build pipeline |
| List of Abbreviations | Seeded, ~45 entries | Drawn from the article; needs audit against final text |
| Chapter One | **Third draft (v3)** | ~2,260 words, four Bloom-levelled objectives, two conceptual figures, heading geometry matched to the exemplar within 0.2 pt |
| Chapter Two | **First draft, builds** | 9 sections, 8 numbered equations, TikZ figure, gaps table, 35 verified citations. Not yet expanded with the 120-paper archive, which was not supplied |
| Chapter One | **Fourth draft (v4)** | ~2,200 words, four direct specific objectives (Bloom labelling removed, see §6 v4 log), two conceptual figures, heading geometry matched to the exemplar within 0.2 pt |
| Chapter Two | **First draft (v4), included in `main.tex`** | `chapters/chapter2_literature.tex`, five sections per the guide's skeleton, six thematic subsections, 113 distinct citations, five original figures, five tables |
| Chapter Two | **Restructured (v8)** | Corpus-methodology section removed, self-referential "review" framing reworded throughout, opens with a plain Introduction; 8 figures (4 TikZ, 4 extracted from source PDFs with attribution), 185 distinct citations |
| Chapter Two | **Own-work-free, first person, expanded (v9)** | Candidate's own unpublished manuscripts (Bitcoin/CRT, HRBAC, five-tier architecture) removed as citable "literature"; HRBAC formalisation moved to Appendix B; written throughout in first person plural; flattened to 17 numbered sections (2.1-2.17), new "Fundamentals of Blockchain Technology" section; 184 distinct citations after a 21-group, 51-key bibliographic-duplicate audit and cleanup |
| Chapter One | **v11, five more diagrams (with Ch. 2)** | 4 figures (up from 2): airtime-as-rate-limit chain and budget-reallocation diagrams added, both conceptual, prose unchanged |
| Chapter Two | **v11, three more diagrams** | 7 figures (up from 4): CRT-application-landscape, identity-enforcement-pipeline and partition-recombine-pattern diagrams added, all visualising arguments the prose already made; citations and prose otherwise unchanged, per the brief ("the literature is good, add more diagrams") |
| Chapter Three | Stub with figures | `chapters/chapter3_methods.tex` holds the three system diagrams and the section skeleton; not yet included in `main.tex` |
| Chapter Four | Partly available | Article §5 results transfer |
| Chapter Five | Not started |, |
| Literature survey | **120-paper corpus indexed** | All 120 PDFs indexed and catalogued; 85 new bib entries generated; 52 of the 120 cited in Ch. 1 and 2 so far |
| Author/subject index | Not started | Mandatory, guide §4.1(c) |
| CV | Not started | Mandatory, guide §4.1(d), ≤ 2 pages |

**Publication gate:** at least one peer-reviewed publication is required before
the defence and the requirement cannot be relaxed (guide §2.4). The article
under review is the intended vehicle. This is the single highest-risk item on
the timeline.

## 2. Objectives, formulated with Bloom's taxonomy

Recorded here so that any later drift between the objectives, the hypotheses
and the results chapters is visible.

**Main objective (Create).** To design, implement and evaluate a distributed
blockchain-based framework that protects identity, integrity and privacy in
agricultural data processing, and to validate it in a sustained field
deployment on constrained edge hardware.

Reduced from seven to four in v2, one per Bloom level above Understand.

| # | Bloom level | Verb | Objective | Evidence that discharges it |
|---|---|---|---|---|
| 1 | Analyse | Analyse | Identity, integrity and privacy requirements; threat surface decomposed into an attacker model | Ch. 2 review + Ch. 3 threat model |
| 2 | Create | Design | Integrated scheme: CRT residue transmission plus an identity layer binding readings to authenticated nodes (MSP + HRBAC chaincode) | Ch. 3 formulation and design |
| 3 | Apply | Implement | Framework on the ESP32 + ARM64 RPi cluster under Fabric/Raft, in real operating conditions | Ch. 3 implementation |
| 4 | Evaluate | Evaluate | Airtime, energy, throughput, latency, memory against baselines, plus the scalability and fault-tolerance envelope | Ch. 4 results and scalability |

Merges applied: old 2 and 3 became a single Create objective, since transmission
design and identity binding are one design problem. Old 5, 6 and 7 became a
single Evaluate objective. Nothing was dropped, only consolidated.

**Why Bloom matters here.** Each objective's verb fixes what counts as
discharging it. An objective that says *analyse* is not satisfied by building
something, and an objective that says *design* is not satisfied by a literature
summary. At the pre-defence seminar the Committee will check exactly this
alignment, objective verb, method, and reported result.

**Avoid at the lower levels.** "Study", "investigate", "look at", "understand"
sit at Remember/Understand and are too weak to carry a PhD objective. Every
objective above sits at Apply or higher.

## 3. Literature survey protocol: target 100 papers

**Status: incomplete.** `references.bib` holds 224 entries carried over from the
article, but they have not been classified by publisher, year or theme, so the
"100 papers across Springer, Elsevier, IEEE, ACM, Taylor & Francis, MDPI" target
is **not yet demonstrably met**. Until that classification is done, treat the
count as unverified.

### Coverage targets

| Publisher | Target | Typical venues for this topic |
|---|---|---|
| IEEE | 25 | IoT Journal, Access, TIFS, Communications Surveys & Tutorials, INFOCOM |
| Elsevier | 20 | Computers and Electronics in Agriculture, Future Generation Computer Systems, Ad Hoc Networks, Computer Networks |
| Springer | 20 | Wireless Networks, Precision Agriculture, Journal of Cloud Computing, Peer-to-Peer Networking |
| MDPI | 15 | Sensors, Agriculture, Applied Sciences, Future Internet |
| ACM | 12 | Computing Surveys, SenSys, TOSN, MobiCom |
| Taylor & Francis | 8 | International Journal of Production Research, Journal of Applied Water Engineering |

### Thematic buckets: the six that Chapter Two must cover

1. Precision agriculture and IoT sensing (~18)
2. LoRa/LPWAN transmission optimisation and energy modelling (~18)
3. Residue number systems and CRT in communications (~12)
4. Blockchain and DLT in agriculture and supply chains (~20)
5. Edge-resident consensus and constrained-hardware ledgers (~16)
6. Privacy-preserving data processing, ZKP, differential privacy, secret sharing, access control (~16)

### Method

1. Search each publisher's database per bucket, restricted to 2019–2026 except
   for foundational works (Garner 1959, Ding 1996 and similar).
2. Screen on title and abstract; keep only papers that state a measured result
   or a formal contribution.
3. Record every kept paper in `references.bib` with a `keywords` field naming
   its bucket, so the classification is queryable:
   ```bibtex
   keywords = {bucket:crt, publisher:ieee, year:2024}
   ```
4. Verify the spread before drafting Chapter Two:
   ```sh
   grep -oP 'publisher:\K\w+' references.bib | sort | uniq -c | sort -rn
   grep -oP 'bucket:\K[\w-]+'  references.bib | sort | uniq -c | sort -rn
   ```
5. For each bucket, write the critique *before* the summary. §2.4 of the
   template asks for a critique of current literature, not a catalogue, the
   Committee reads for the gap, not for coverage.

### Standing rule

Every claim in Chapters One and Two carries a citation, or it is marked
`%% VERIFY` in the source and does not survive to the submitted draft.

## 4. Open questions and risks

| # | Item | Why it matters | Status |
|---|---|---|---|
| 1 | **H5 (privacy) is unsupported.** The article establishes H1–H4; the privacy hypothesis is new to the thesis. | Without a formal argument or a leakage measurement, the "privacy" third of the title is unearned. | **Open, highest priority** |
| 2 | Per-reading node identity | The article authenticates at the gateway. The thesis claims node-level identity binding. The gap must be closed in design and measured for cost. | Open |
| 3 | Publication acceptance | Hard gate on the defence. | Pending review |
| 4 | Body length | Article maps to roughly 90–110 thesis pages; the guide requires 150–250. | Plan Ch. 2 and Ch. 5 accordingly |
| 5 | Single deployment site | Bounds generalisation claims. | Declare in limitations, do not overclaim |
| 6 | Author index, subject index, CV | Mandatory under §4.1; the exemplar thesis omits all three. | Not started |
| 7 | Literature classification | See §3. | Not started |

## 5. Decisions taken

| Date | Decision | Reason |
|---|---|---|
| 2026-08-16 | Thesis format template implemented as `ubthesis.sty` rather than a custom class | Keeps the `book` class semantics (`\frontmatter`/`\mainmatter`) that the roman/arabic numbering requires |
| 2026-08-16 | Abbreviations via `glossaries-extra` + `\printunsrtabbreviations` | Chapter One and the List of Abbreviations build in one pass, with no `makeglossaries` step. Cost: manual alphabetisation |
| 2026-08-16 | `references.bib` copied from the article rather than referenced in place | The article directory is a submission artifact and should not churn as the thesis evolves |
| 2026-08-16 | Every iteration emits `.tex` + `.pdf` + `.docx` under a new version number | Supervisor mark-up happens in Word; the PDF is authoritative; the flattened `.tex` keeps each iteration reproducible |
| 2026-08-16 | Objectives formulated at Apply level or above, four of seven at Create/Evaluate | Bloom alignment is checked at the pre-defence seminar |

## 6. Log

### 2026-08-16 - v1: scaffold and Chapter One first draft

Built the LaTeX scaffold under `thesis/`: `ubthesis.sty` implementing the
measured UB format spec, `main.tex` with the full front-matter sequence,
front-matter templates, a seeded abbreviations file (~45 entries drawn from the
article), and `build.sh` producing versioned `.tex`/`.pdf`/`.docx`.

Wrote the Chapter One first draft against the Appendix III A skeleton, background, problem statement, rationale, objectives, research questions,
hypotheses, scope, significance, definitions, organisation. Objectives
formulated with Bloom's taxonomy and recorded in §2 above.

Framing decision worth recording: the chapter argues that CRT residue
decomposition is not only a transmission efficiency measure but the source of
the budget that pays for cryptographic protection, and that residues
distributed across channels are themselves a privacy substrate. That is the
thread tying "identity, integrity and privacy" in the title to the CRT work in
the article. It is currently an argument, not a result. Item 1 in §4.

**Not done:** nothing has been compiled, no LaTeX toolchain in the build
environment. Citations in Chapter One reuse keys verified to exist in
`references.bib` but their content has not been re-read against the claims they
support. The literature classification in §3 has not been started.

**Next:** run `./build.sh` and clear the first-run errors; audit the
abbreviations list against the drafted text; begin the literature
classification pass.

### 2026-08-16 - v2: format corrections, figures, objectives reduced

Compiled the scaffold for the first time and measured the output against the
exemplar rather than trusting the source. Two defects that only a measurement
would catch:

**Line spacing was wrong.** `\doublespacing` from `setspace` produces 23.9 pt
at 12 pt. Word's "Double" for Times New Roman 12 pt is 27.6 pt, because Word
doubles the 13.8 pt single line height rather than the point size. The exemplar
measures 27.6 pt. Corrected with `\setstretch{1.911}`, verified at 27.6 pt.
Anyone reproducing this template elsewhere should re-measure rather than assume
`\doublespacing` is right.

**Paragraph spacing did not match the exemplar.** The guide's §3.1d asks for an
extra line between paragraphs, but the exemplar has none: every baseline gap in
the body is exactly one line. Removed `\parskip` and added a 1.27 cm first-line
indent, since double-spaced text with neither cue is unreadable. Worth raising
with the supervisor, because guide and exemplar disagree here.

Specific objectives cut from seven to four, one per Bloom level: Analyse,
Create, Apply, Evaluate. The old objectives 2 and 3 (transmission design,
identity layer) merged into a single Create objective, since they are one
design problem; old 5, 6 and 7 merged into a single Evaluate objective.

Figures. The first attempt put the article's system diagrams into Chapter One:
the five-tier architecture, the CRT pipeline and the certificate enrolment
chain. That was wrong. Chapter One argues; it does not specify. Architecture
diagrams, hardware layouts and protocol chains are Materials and Methods
material, and putting them in the introduction forces the reader through
implementation detail before the problem has been stated.

The three system figures now live in `chapters/chapter3_methods.tex`, staged
under the Appendix III A section skeleton and ready for the prose. That file is
deliberately **not** included in `main.tex` yet, so the built document does not
jump from Chapter One to Chapter Three while Chapter Two is missing.

Chapter One instead carries three original conceptual diagrams, drawn in TikZ
rather than imported, so they are vector, match the document fonts, and are
unambiguously the candidate's own work:

- **Figure 1.1** (§1.1) the lifecycle of an agricultural measurement, showing a
  reading becoming a record consumed by certification, insurance and subsidy
  bodies, and the falsification incentive that value creates.
- **Figure 1.2** (§1.2) the three protection properties with the shortfall in
  each, enclosed by the single shared budget that binds them. This is the
  chapter's central claim in one picture: three faults, one cause.
- **Figure 1.3** (§1.10) the thesis roadmap, mapping each of the four specific
  objectives to the chapter that discharges it.

Each was checked by rendering the page and inspecting it, which caught two
layout faults invisible in the source: an annotation colliding with a node box
in 1.1, and annotations straddling the dashed boundary in 1.2.

All em dashes removed from every source file. Font pinned to Times on every
page, including the bibliography, where DOIs were rendering in a typewriter
face.

**Still open:** H5 (privacy) remains unsupported, item 1 in §4. Literature
classification not started. Author index, subject index and CV not started.

### 2026-08-16 - v3: heading format matched to the exemplar, Chapter One expanded

The v2 output looked wrong next to the exemplar, and it was. Rendering the
exemplar's chapter opening page and measuring it against ours found four
mismatches:

| Element | v2 | Exemplar |
|---|---|---|
| "CHAPTER ONE" | 14 pt bold | **16 pt bold** |
| Chapter title | 16 pt bold, wide gap below the label | 16 pt bold, **18.4 pt** below |
| Section heading | 14 pt bold, no period | 14 pt bold, **trailing period** |
| Subsection heading | 12 pt bold | **14 pt bold**, same as section |
| Caption | bold label, italic text, "Figure 1.1" | **12 pt regular**, "Figure 1", continuous numbering |

The heading-gap fault had the same root cause as the earlier line-spacing bug:
`\setstretch{1.911}` applies to headings too, so a 18.4 pt leading was being
stretched to roughly 35 pt. `\singlespacing` inside the titlesec format block
fixes it. Worth remembering as a general rule: any explicitly measured leading
in this template has to be wrapped in `\singlespacing` or the global stretch
will silently scale it.

Vertical geometry is now within 0.2 pt of the exemplar at every element of the
chapter opening page (chapter label, title, first section heading, first body
line).

Figure 1.3, the thesis roadmap, was cut. It restated in a diagram what the
following paragraph says in prose, which is the definition of a figure that has
not earned its place.

Chapter One expanded from roughly 1,750 to 2,260 words: the economics that
force the node design, the duty-cycle and collision constraints that make
airtime a rate limit rather than merely an energy cost, prior residue-arithmetic
work on blockchain throughput, a structural argument for why the two mechanisms
compose without taxing each other, and the methodological contribution of field
rather than laboratory characterisation.

**Not done.** The brief named
`report/Enhancing_Bitcoin_Scalability_through_Parallel_Programming_and_Chinese.pdf`
as an update to draw on. That file is **not in the repository**, so nothing in
Chapter One is sourced to it. The paragraph on prior residue-arithmetic work
carries a `%% VERIFY` marker naming the missing citation. Add the PDF and its
`.bib` entry and the citation can be placed.

**Still open:** H5 (privacy) unsupported; literature classification not started;
author index, subject index and CV not started.

### 2026-08-16 - v4: Chapter One de-Bloomed, Chapter Two written, appendices added

Three requests drove this iteration: cut the meta-commentary out of Chapter
One's objectives, write Chapter Two, and bring the back matter (appendix)
up to the same format standard as the front matter.

**Chapter One.** Removed the sentence explaining that objectives follow
Bloom's revised taxonomy, and the trailing `(Analyse)`/`(Create)`/`(Apply)`/
`(Evaluate)` tag after each objective. The objectives read as direct
statements now; nothing about their content changed, only the
self-explanation wrapped around them. Bloom alignment as a design method
stays recorded in §2 above, since that is a legitimate note for this
journal, just not something the submitted chapter should narrate to the
reader.

**Chapter Two.** Written against the guide's five-part skeleton (§2.1
historical overview, §2.2 theory and literature specific to the topic in
six thematic subsections mirroring the bucket list in §3 above, §2.3
cognate areas, §2.4 critique, §2.5 contribution). Sourced three ways: the
224-entry `references.bib` for citations, the source article
(`project fin update with reviewers/main_article.tex`) for the CRT/Garner,
LoRa-airtime, ALOHA-collision and M/D/1 formulas already derived there, and
two of the candidate's own manuscripts found in `report/` and
`project fin update with reviewers/` that were not yet in the bibliography,
the Bitcoin/CRT parallel-programming paper and the HRBAC formalisation
paper. Both are now bib entries (`beloa2025bitcoincrt`,
`beloasone2025hrbac`) and both are cited substantively: the Bitcoin/CRT
paper resolves the `%% VERIFY` marker Chapter One has carried since v3
(prior residue-arithmetic work on blockchain throughput), and the HRBAC
paper supplies the formal role-hierarchy model (Eq. 2.8-2.9) that Chapter
Two's privacy subsection and Appendix B build on.

Five original TikZ figures (a three-lineage timeline, a transmission-
technique taxonomy, a CRT dual-pipeline comparison, a consensus fault-model
taxonomy) and five tables, no third-party images, consistent with the
copyright decision recorded for Chapter One's figures in the v2 entry
above. Ten abbreviations added to `front/abbreviations.tex` (ACID, CFT,
ECDSA, ETSI, LPWAN, RNS, WSN, X.509, and two defined then removed again
once unused, CSMA and TDMA, per the audit rule in `README.md` §7).

**Appendices.** `back/appendices.tex` is new: Appendix A carries the CRT
worked reconstruction example (the 25.30 °C / moduli {97,101,103} instance
from the source article) through every Garner-coefficient step by hand;
Appendix B reproduces the HRBAC permission matrix from the candidate's own
paper. Enabling `\appendix` surfaced a real bug rather than a cosmetic one:
`\backmatter` (called earlier, for the References heading) sets
`\@mainmatterfalse`, and book.cls's own `\chapter` macro only numbers and
labels a chapter when `\if@mainmatter` is true. Appendix chapters were
compiling with no "APPENDIX A/B" label at all and an unnumbered Table of
Contents entry until `\@mainmattertrue` was restored around
`\include{back/appendices}` in `main.tex`. Worth remembering: any thesis
template that puts `\appendix` after `\backmatter`, which the guide's own
back-matter order (References, Appendices, indices, CV) forces, needs this
patch, or the equivalent, to get numbered appendices at all.

**Build.** `texlive-latex-extra`, `texlive-fonts-extra`, `texlive-science`,
`texlive-bibtex-extra`, `latexmk`, `biber`, `pandoc` and `poppler-utils`
were not present in this session's container and were installed before
building. `./build.sh` produced `dist/thesis_v04.{tex,pdf,docx}`: 57 pages
(up from 27 in v03), 0 undefined citations, 0 undefined references, 2 minor
overfull hboxes under 11 pt (caption line wraps, within the tolerance
`README.md` §9 documents for hyphenation-off justified text). The flattened
`dist/thesis_v04.tex` was independently recompiled standalone to confirm it
is not just a build-directory artifact. The DOCX numbers the two appendices
as plain chapters 3 and 4 rather than "Appendix A/B", a Pandoc limitation
already documented in `README.md` §6; the PDF remains authoritative.

**Not done.** The literature-classification method in §3 above (tagging
every `references.bib` entry with `keywords = {bucket:...,
publisher:..., year:...}`) was not run; Chapter Two draws on a
representative, thematically organised subset of the 224 entries rather
than a programmatically verified 100-paper spread across the six named
publishers. Chapters Three, Four and Five remain unwritten. H5 (privacy)
is argued in Chapter Two §2.2.6 but still lacks the formal bound or
leakage measurement Chapter Four would need to close it. Author index,
subject index and CV not started.

### 2026-08-16 - v5: three correctness fixes from automated PR review

PR #96 (the v4 push) got an automated Codex review with three findings,
all P1/P2, all verified against source before acting rather than taken on
trust.

**Confirmed and fixed, PBFT fault count.** Chapter Two's consensus
subsection said PBFT tolerates "the same $f=\lfloor(n-1)/2\rfloor$" as
Raft. Wrong: Byzantine agreement needs $n\geq 3f+1$ replicas, so PBFT's
bound is $f=\lfloor(n-1)/3\rfloor$. This was a plain algebra error, not a
judgement call, fixed in the prose and the taxonomy figure alike.

**Confirmed and fixed, CRT residue disclosure.** Chapter Two claimed an
intercepted \gls{crt} residue discloses "little" about the value it
derives from, drawing a formal analogy to threshold secret sharing. That
analogy does not hold: a plain residue is deterministic, not a randomised
share, so it narrows the plaintext by roughly a factor of the modulus
rather than leaking nothing. Reworded to state the actual condition,
disclosure bounded by the plaintext-domain-to-modulus ratio, as what
hypothesis H5 has to establish, not as a result already in hand. Worth
noting for future chapters: this was Chapter Two overclaiming something
Chapter One's own H5 already correctly flagged as unproven; the two
chapters now agree.

**Confirmed and fixed, Appendix A's subset-recovery claim, checked against
actual code, not just the source article's prose.** The appendix claimed
two-of-three residue recovery holds for every sensor type this thesis
deploys. Reading `esp32/main/main.c` and `gateway/crt_decode.py` directly
(not just the worked example, which used a single, small scaled
temperature value) showed this is false for the deployed encoding:
`encode_sensor_value` packs soil moisture and a temperature bucket into
one value reaching 823,295, while `decode`'s own docstring already admits
two-residue reconstruction is exact only "for sensor values constrained
below the product of the received moduli", at most 10,403. The source
article's own reported figure, 64.1% measured two-of-three recovery
against 66.7% theoretical, is the honest number and is now what the
appendix cites, instead of an implied 100%. Nothing in the firmware or
gateway code was touched, this is a thesis-text correction, not an
engineering fix, and whether the encoding scheme itself should change
(bound combined values under every two-modulus product, or require all
three residues before reconstructing) is left as an open item rather than
decided here.

**Method worth repeating.** All three findings named specific files, lines
or code paths. Before editing, each was checked against the named source
(the actual PBFT literature's replica count, the actual firmware's
`encode_sensor_value`, the actual gateway's `decode`) rather than
patched from the review comment's wording alone. That is what made it
possible to fix the third finding correctly, the review comment described
the symptom; the fix required reading two files to find the right level
at which to correct the claim.

**Still open.** Whether the deployed CRT encoding should be changed so
that two-residue recovery is unconditionally exact (the reviewer's
suggested remedy) is a Chapter Three design decision, not made in this
pass. H5 remains unsupported by a formal bound or measurement. Literature
classification, Chapters Three to Five, author/subject index and CV
remain as in the v4 entry above.

<!-- Append the next entry here.
### YYYY-MM-DD - <short title>
What changed, what it means, what is now open.
-->

### 2026-08-17 - v8: Chapter Two restructured, front-matter spacing bugs
root-caused, figures extracted from source PDFs

Six requests against v7, none of them content rewrites: drop the corpus
section, stop the chapter narrating itself as "a review", add real figures
from the underlying papers rather than only TikZ ones, shorten captions,
close the gap under the front-matter list headings, and set the
preliminary pages at 1.5 line spacing. The two spacing items turned out to
be genuine bugs, not tuning, and took most of the session to root-cause.

**Chapter Two restructuring.** Removed §2.2.7, "The Corpus Underlying This
Review" (the 120-paper composition table and publication-year chart), the
one section that was about the review's own retrieval methodology rather
than the literature. Its four downstream "in this corpus" references were
reworded to stand alone. §2.1 renamed "Historical Overview of the Theory
and Research Literature" to "Introduction". Thirteen instances of "the
reviewed literature", "this review", "literature reviewed here" and
similar self-narration across the chapter reworded to "prior work" or cut
outright. Nothing else in the content or citation set changed, per the
brief: restructuring, not rewriting.

**Figures extracted from the source PDFs, not only drawn.** Four raster
figures added alongside the seven remaining TikZ diagrams: two cropped
from the candidate's own architecture manuscript
(`lit-rev/papers/CRT_Based_Parallel_Residue_Transmission_...pdf`, bib key
`forcha2026basedparallel`), the five-tier system diagram and the
gateway-side residue-decode/ledger pipeline; one from the candidate's own
HRBAC manuscript (`beloasone2025hrbac`), the enrolment trust chain,
reusing a crop already sitting unused in `figures/v06/`; and one from
`gong2025edge`, an MDPI *Sensors* article under CC BY 4.0, credited as
such in the caption per `README.md` §8's licence-and-cite rule. Cropped at
300dpi with a row/column whitespace-profile script (Pillow, no
`imagemagick` in this container) rather than by hand, and verified by
rendering each candidate page before cropping. Placed next to the
paragraph that already cites each source, not clustered at the end.

**Two front-matter spacing bugs, root-caused rather than patched.**

The first: a large blank gap under "TABLE OF CONTENTS" / "LIST OF
FIGURES" / "LIST OF TABLES" before the first entry. The first diagnosis,
that `\chapter*`'s stock `\@makeschapterhead` (book.cls's
`\vspace*{50pt}` + an empty `\Huge` line + `\vskip 40pt`) was leaking
through with an empty title, was wrong, confirmed wrong with `\show
\@makeschapterhead` after overriding it and finding the gap unchanged. The
actual cause: tocloft, once loaded, redefines
`\tableofcontents`/`\listoffigures`/`\listoftables` inside its own
`\AtBeginDocument` hook to call
`\@cftmaketoctitle`/`\@cftmakeloftitle`/`\@cftmakelottitle` instead of
`\chapter*` at all, and those three reimplement the identical 50+40pt band
independently via `\cftbeforetoctitleskip` etc. Found by writing a
throwaway two-chapter test document and bisecting: bare `\chapter*{}`
alone, no gap; `\l@chapter` called directly, no gap; `\chapter*{}`
followed by `\@starttoc{toc}` by hand, no gap; the real `\tableofcontents`
command, gap. That last difference is exactly the tocloft substitution.
Fixed by making all three `\@cftmake*title` commands no-ops, since
`\ubfrontheading` already prints the visible title.

The second: the List of Abbreviations heading sat alone on its own page,
every entry starting on the next. Traced to `\printunsrtglossary` opening
with its own `\glossarysection`, which (once hyperref defines
`\phantomsection`) runs `\glsclearpage`, i.e. a bare `\clearpage`, ahead
of an empty-titled section heading, before a single entry is typeset.
Confirmed by bisecting `style=long` (longtable) against `style=list`
(plain `description`) and a custom non-tabular style, and `singlespace`
present against absent, none of which changed the symptom, which is what
pointed at `\glossarysection` as the one remaining shared step. Fixed with
`\renewcommand*{\glossarysection}[2][]{}` for the same reason as above,
`\ubfrontheading` already supplies the heading.

**Preliminary pages at 1.5 line spacing.** A new `ubonehalfspace`
environment in `ubthesis.sty` (`\setstretch{1.4375}`, giving 20.7pt
leading for Times New Roman 12pt, Word's own "1.5 lines" figure) now wraps
dedication, acknowledgements, abstract, and the four front lists.
Certification is left on its existing single spacing, since it is a
fixed-position form, not running prose, and its internal `\vspace` amounts
were tuned assuming that.

**Captions shortened.** The three longest multi-sentence captions in
Chapter Two (the lineage timeline, the transmission taxonomy, the CRT
pipeline comparison) and both Chapter One captions cut to one sentence
each. Already-short captions, and the appendix's HRBAC permission-matrix
caption (which carries a legend the table needs to stand alone), left as
they were.

**List of Figures / List of Tables now read "Figure 1", "Table 1", ...**
via tocloft's `\cftfigpresnum`/`\cfttabpresnum` and matching
`\cftfignumwidth`/`\cfttabnumwidth`, instead of a bare number.

**Build.** 68 pages (up from 67 in v07, net of one section removed and
four figures added). 0 LaTeX errors, 0 undefined citations, 0 undefined
references, 2 minor overfull hboxes under 11pt, unchanged from v07 and
within the documented hyphenation-off tolerance. DOCX converts cleanly;
spot-checked `word/document.xml` directly to confirm the corpus section
and every "reviewed literature" phrase are actually gone, not just absent
from the PDF, and that all four extracted images made it into
`word/media/`.

**Not done.** The DOCX's own empty Table of Contents / List of Figures /
List of Tables (Pandoc drops `\tableofcontents` et al. entirely, a
pre-existing and already-documented limitation, `README.md` §6) was left
alone: out of scope for this pass, and the PDF remains the authoritative
artifact per that same section. H5 remains unsupported by a formal bound
or measurement. Literature classification, Chapters Three to Five,
author/subject index and CV remain as in the v4 entry above.

### 2026-08-17 - v9: candidate's own work removed from Chapter Two, first
person throughout, chapter roughly doubled, a real bibliography bug found
and fixed, certification page rebuilt

Feedback on v8, once it was actually read rather than skimmed: most of the
new figures were "extracted from the papers" in name only, three of the
four were extracted from the candidate's own unpublished manuscripts, not
from independent literature, which is exactly the "current work in the
literature chapter" problem the v8 corpus-section removal was supposed to
start fixing but didn't finish. That, plus a request to write in first
person and to expand the chapter considerably before Chapter Three is
drafted, drove this iteration.

**Own work is not literature, all the way through this time.** v8 removed
the corpus-methodology section but left three figures and their
supporting prose citing `beloa2025bitcoincrt`, `beloasone2025hrbac` and
`forcha2026basedparallel`, the candidate's own unpublished manuscripts,
inside the literature survey proper: the CRT section's "third application
community", the identity section's full HRBAC formalisation
(Equations 2.8-2.9 as numbered then), and the scalability section's
closing paragraph. All three are gone from Chapter Two now. The HRBAC
formalisation did not simply disappear, it belongs in an appendix (that
is what appendices are for, the thesis's own derivations), so
`back/appendices.tex` Appendix B was rewritten to state the partial order,
Equations~\ref{eq:hrbac_eff} and~\ref{eq:hrbac_grant} (now B.1-B.2), and
the trust-chain figure itself, self-contained rather than assumed from a
Chapter Two that no longer states them. This was the one genuinely
structural decision in this pass: everywhere else in the codebase that
cross-referenced those equations by number, the appendix rewrite had to
absorb the definition rather than the chapter keeping a stub of it, or
the appendix would have been citing nothing.

The CRT-to-blockchain connection got the same treatment rather than being
deleted outright, since the brief explicitly asked for it ("talk about
CRT, how it links to the blockchain etc."). What was previously "the
present work applies the same argument~\cite{forcha2026basedparallel}" is
now stated as an observation: residue decomposition's carry-free
independence and the blockchain-scalability literature's
partition-and-recombine pattern (sharding, layer-two, multi-chain) are
structurally the same shape, and neither literature states that
explicitly. That is a legitimate synthesis move for a literature chapter
to make, reading two surveyed bodies of work side by side, as long as it
is flagged as an observation and not dressed up as a citable result, which
is what "to our knowledge, no published work states this" is for.

**First person.** Every "this thesis argues", "the candidate's own prior
work" and similar phrase in Chapter Two is now "we"/"our". Mechanical in
most places, but the CRT, consensus and scalability sections needed real
rewording since "the Raft ordering service used in this thesis" and "This
thesis, deployed on a consortium..." don't become "we" by find-and-replace
alone.

**A real bibliography bug, not part of the brief, found while checking
citations for the above.** Grouping `references.bib`'s 311 entries by
normalised title turned up 21 groups, 51 keys, that were exact-duplicate
papers under different keys, evidently from pulling the same paper into
the corpus more than once across v4 through v7's integration passes. Two
were outright wrong rather than merely duplicated: `ali2022secureIOT`,
cited under "IoT-specific attack surfaces, firmware injection,
authentication bypass", actually held Salah et al.'s soybean-traceability
paper (its exact duplicate, correctly keyed as `salah2019blockchain`, was
separately and correctly cited for supply-chain traceability); and
`liu2024blockchainwater`, cited for "water-quality...ledgers report
similar tamper-evidence gains", actually held the self-sovereign-identity
paper `amraouy2025ssi` already cited, correctly, one sentence earlier. Five
different keys for a single Kamilaris paper were cited together in one
sentence as if five independent sources. Fixed with a script: one
canonical key chosen per duplicate group (the more-used key, or the
better content match where usage was tied), every in-text citation
redirected and de-duplicated within its own `\cite{}` list, the two
outright-wrong citations dropped from the sentences they didn't support
rather than relabelled, and the 30 orphaned duplicate entries deleted from
`references.bib` (311 to 281). Worth a standing rule for future
corpus-integration passes: check for a title match before minting a new
key, not just for the key string itself.

**Expansion.** Chapter Two's subsections were flattened into top-level,
numbered sections, 2.1 through 2.17, at the candidate's explicit request,
rather than nested under one "theory and literature specific to the
topic" section; the guide's five-part skeleton is followed in spirit
(introduction, survey, cognate areas, critique, contribution) rather than
in that one heading's letter. A new section, "Fundamentals of Blockchain
Technology" (2.2), was added ahead of the agricultural material: hash
chaining, permissioned versus permissionless design, Hyperledger Fabric's
execute-order-validate pipeline and chaincode, DAG-based alternatives
(IOTA), and the elliptic-curve signing every transaction relies on, so a
reader reaches the agriculture-specific sections already knowing what a
blockchain is rather than picking it up piecemeal. The agriculture-
blockchain section gained a paragraph grounding the thesis in its actual
deployment context, a feasibility study of blockchain and IoT for African
agricultural supply chains is the closest match in the corpus to a
constrained, intermittently-connected smallholder setting, plus soybean
and Nepal-ginger traceability case studies. The scalability section gained
UTXO storage/throughput trade-offs, cloud-hosted scaling frameworks and
multi-chain architectures (a judicial case-management system keeping
separate case and evidence chains). The identity section gained a
published IoT-blockchain authentication protocol to stand in the
citation slot the HRBAC formalisation vacated. Eleven bib entries drawn
into service from the previously-unused two-thirds of the 120-paper
corpus, all third-party, none candidate manuscripts.

**Certification page rebuilt** to match the supplied exemplar image
directly rather than the generic "This is to certify that the work
described..." paragraph form it had: university header, faculty/
department two-column line, "The Thesis of NAME (matricule) entitled
TITLE submitted to ... under the Supervision of", a Sign/Date block per
supervisor (the exemplar has one, this thesis has two, so the block
repeats), and the candidate's own Sign line at the foot.

**Build.** 71 pages (up from 68), 0 LaTeX errors, 0 undefined citations,
0 undefined references, 184 works cited. DOCX regenerated and spot-
checked directly: both removed manuscript keys confirmed absent from
`word/document.xml`, the new "Fundamentals of Blockchain" heading
confirmed present, two images in `word/media/` (down from four),
matching the two raster figures Chapter Two and Appendix B now carry
between them.

**Not done.** H5 remains unsupported by a formal bound or measurement.
`chapters/chapter3_methods.tex` still holds the original, lower-quality
crops of the five-tier architecture and CRT-pipeline figures under
`figures/`; the better crops this session produced under
`figures/extracted/` are unused now that their Chapter Two citations are
gone, and are left in place for Chapter Three to pick up when it is
written, since that is where the candidate's own system diagrams belong.
Chapter One still cites `forcha2026basedparallel` once, in its own
background/rationale paragraph, not the literature chapter, left as is.
Literature classification, Chapters Three to Five, author/subject index
and CV remain as in the v4 entry above.

### 2026-08-24 - v11: five more diagrams in Chapters One and Two, no prose
changes

The request was narrow and explicit: "the literature is good, add more
diagrams", for both Chapter One and Chapter Two. Read literally rather than
as an invitation to also revise text: every new figure visualises an
argument the surrounding prose already makes, and nothing already written was
reworded beyond the one sentence in each spot that now points at the new
figure.

**Where each figure went and why.** Chapter One gained two, both kept
conceptual per the v2 decision recorded above (Chapter One argues, it does
not specify): an airtime-is-a-rate-limit causal chain in the Background
section, next to the paragraph that already argues duty-cycle silence and
collision probability are both downstream of one quantity; and a budget-
reallocation stacked-bar diagram in the Rationale section, making literal
the chapter's central claim that CRT-freed airtime funds the identity,
integrity and privacy work. Chapter Two gained three, each placed at the
exact paragraph it illustrates: a CRT-application-landscape tree in the
residue-arithmetic subsection, setting the two established applications
(storage, energy) against the open one (radio concurrency) the "two
application communities" paragraph already describes; an identity-
enforcement pipeline in the identity/access-control subsection, showing
where the surveyed literature's authentication chain starts and the node-
level gap upstream of it; and a partition-process-recombine pattern diagram
in the scalability subsection, setting sharding, layer-two/multi-chain and
cloud-hosted scaling as three instances of the pattern the "common
structure of these results" paragraph already argues, against residue
decomposition as the fourth, open instance. All ten figures across the two
chapters (five new, five carried over) use the same box/tree/flow TikZ
idiom already established, so nothing new was introduced stylistically.

**Two real bugs in the new TikZ, not cosmetic.** Two of the new figures used
`out` and `step` as local pgf style names; both are reserved keys once
pgfplots is loaded (`ubthesis.sty` loads it for later chapters), and the
failure mode is not a name-clash error but "the key .../tikz/out requires a
value", which does not point at the cause. Renamed to `res` and `stg`.
Worth a standing rule: avoid short, generic TikZ style names in this
document, since pgfplots is always loaded.

**One real layout bug.** The Chapter One budget-reallocation figure's row
labels used `align=right` without `anchor=east`, which centres a node on its
coordinate rather than right-aligning it to that point; the effect was label
text running underneath the adjacent bar rather than stopping short of it.
Caught by rendering the page and looking, the same method the v2 and v3
entries above used, not by reading the source. Fixed by adding
`anchor=east`, and while at it, both this figure and the Chapter Two
partition-recombine figure had their bar/box widths trimmed by a few
millimetres, since both computed out to a width that produced a 9-11pt
overfull hbox, under the pre-existing tolerance this document documents
elsewhere but worth avoiding rather than accumulating.

**The build environment was the bigger obstacle than the diagrams.** No
LaTeX toolchain was present in this session's container. The obvious
package list from `README.md` §2 was not sufficient: `newtxtext.sty`
(this template's Times clone) requires `tex/generic/kastrup/binhex.tex`,
which ships in `texlive-plain-generic`, a package none of the "obvious"
ones pull in as a dependency. Found by `apt-file search binhex.tex` after
the direct package names failed. Separately, `latexpand` was missing
(`texlive-extra-utils`); without it, `build.sh`'s fallback is to copy
`main.tex` unflattened into the versioned `.tex`, which looks harmless but
silently breaks the DOCX pipeline: `tools/expand_gls.py` looks for
`tikzpicture` environments in that file to substitute with rendered PNGs,
and finds none, because the chapters sit behind `\include` rather than
inlined. The DOCX built without error either way, just with 2 images
instead of 12, which is the kind of failure that does not show up unless
someone opens the file and counts. Confirmed by rebuilding both ways and
diffing the media count. Worth adding both packages to `README.md` §2's
list so the next machine does not repeat the search.

**Build.** 73 pages (up from 71). Chapter One 4 figures (up from 2), Chapter
Two 7 figures (up from 4, 6 TikZ + 1 raster), 12 figures total across the
document. 0 LaTeX errors, 0 undefined citations, 0 undefined references, 2
overfull hboxes, both pre-existing and in figures this pass did not touch;
the 5 new figures introduced none. DOCX: 12 images (up from 7 before this
pass, once the `latexpand` gap was closed), all figures present.

**Not done.** No prose in either chapter was revised; that was the brief.
H5 remains unsupported by a formal bound or measurement. Literature
classification, Chapters Three to Five, author/subject index and CV remain
open as in the v4 entry above.

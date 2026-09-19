# Build Iterations

Auto-appended by `./build.sh`. One stanza per build, with the artifacts it
produced and the commit it was built from. Fill in the "Changes" line by hand
before committing, that line is what makes this log worth keeping.

Artifacts live in `dist/` and are never overwritten:
`thesis_vNN.tex` (flattened source), `thesis_vNN.pdf`, `thesis_vNN.docx`.

### v01, 2026-08-16

- Artifacts: `dist/thesis_v01.{tex,pdf,docx}`
- Changes: first build. Front matter (title, blank, repeat title, dedication ii
  through list of abbreviations xi), Chapter One, references.
- PDF: 25 pages. 0 undefined citations, 0 undefined references, 0 overfull
  boxes, 0 underfull boxes.
- DOCX: 2,923 words, 22 headings, Times New Roman 12 pt / double spacing /
  3.5-2.5 cm margins verified programmatically.

### v01, 2026-08-16

- Artifacts: `dist/thesis_v01.{tex,pdf,docx}`
- Commit: `710bf59`
- Changes: _describe what changed in this iteration_

### v02, 2026-08-16

- Artifacts: `dist/thesis_v02.{tex,pdf,docx}`
- Commit: `4416f79`
- Changes: _describe what changed in this iteration_

### v02, 2026-08-16

- Artifacts: `dist/thesis_v02.{tex,pdf,docx}`
- Commit: `4416f79`
- Changes: _describe what changed in this iteration_

### v02, 2026-08-16

- Artifacts: `dist/thesis_v02.{tex,pdf,docx}`
- Commit: `4416f79`
- Changes: _describe what changed in this iteration_

### v02 - 2026-08-16

- Artifacts: `dist/thesis_v02.{tex,pdf,docx}`
- Changes:
  - Title page corrected: matriculation FE22P049, previous degree M.Eng. in
    Telecommunications and Networks, both supervisors listed as Associate
    Professor.
  - Line spacing corrected from 23.9 pt to **27.6 pt**. `\doublespacing` does
    not equal Word's "Double" at 12 pt; `\setstretch{1.911}` does.
  - Paragraph spacing removed (`\parskip` 0) and replaced with a 1.27 cm
    first-line indent, matching the exemplar.
  - Specific objectives reduced from seven to **four**: Analyse, Create,
    Apply, Evaluate.
  - All em dashes removed from every source file.
  - Three figures in Chapter One, all original conceptual diagrams drawn in
    TikZ: the agricultural data lifecycle, the three protection properties
    under one shared budget, and the thesis roadmap. The system-specific
    diagrams (five-tier architecture, CRT pipeline, certificate enrolment
    chain) were moved to `chapters/chapter3_methods.tex`, where they belong.
  - Font forced to Times on every page; URL/DOI typewriter face eliminated.
  - DOCX enhanced: Body Text and First Paragraph styles pinned (inheriting
    from Normal was not enough), figures and captions carried through.
- PDF: 27 pages. Leading 27.6 pt. 0 undefined citations, 0 undefined
  references, 0 overfull boxes, 0 underfull boxes, 0 missing figures.
- DOCX: 3 images embedded with captions, 0 pt paragraph spacing,
  1.27 cm indent, double spacing.

### v02 — 2026-08-16

- Artifacts: `dist/thesis_v02.{tex,pdf,docx}`
- Commit: `53eee1a`
- Changes: _describe what changed in this iteration_

### v02 — 2026-08-16

- Artifacts: `dist/thesis_v02.{tex,pdf,docx}`
- Commit: `53eee1a`
- Changes: _describe what changed in this iteration_

### v02 — 2026-08-16

- Artifacts: `dist/thesis_v02.{tex,pdf,docx}`
- Commit: `53eee1a`
- Changes: _describe what changed in this iteration_

### v02 — 2026-08-16

- Artifacts: `dist/thesis_v02.{tex,pdf,docx}`
- Commit: `ee7b6a8`
- Changes: _describe what changed in this iteration_

### v02 — 2026-08-16

- Artifacts: `dist/thesis_v02.{tex,pdf,docx}`
- Commit: `ee7b6a8`
- Changes: _describe what changed in this iteration_

### v02 — 2026-08-16

- Artifacts: `dist/thesis_v02.{tex,pdf,docx}`
- Commit: `ee7b6a8`
- Changes: _describe what changed in this iteration_

### v02 — 2026-08-16

- Artifacts: `dist/thesis_v02.{tex,pdf,docx}`
- Commit: `ee7b6a8`
- Changes: _describe what changed in this iteration_

### v03 — 2026-08-16

- Artifacts: `dist/thesis_v03.{tex,pdf,docx}`
- Commit: `ee7b6a8`
- Changes: _describe what changed in this iteration_

### v03 - 2026-08-16

- Artifacts: `dist/thesis_v03.{tex,pdf,docx}`
- Changes: heading and caption styles re-measured against the exemplar and
  matched to within 0.2 pt on the chapter opening page.
  - Chapter heading: both lines now **16 pt bold** on consecutive
    single-spaced lines 18.4 pt apart. Previously 14 pt + 16 pt with a
    stretched gap, because `\setstretch{1.911}` was multiplying the heading
    leading; fixed with `\singlespacing` inside the titlesec format.
  - Section and subsection headings: both **14 pt bold** with a trailing
    period after the number ("1.1.  Background to the Study"), matching the
    exemplar, which does not shrink subsections.
  - Captions: **12 pt regular**, neither bold nor italic, centred, and
    numbered continuously across the thesis (Figure 1, Figure 2), not per
    chapter.
  - Vertical geometry tuned so CHAPTER / title / first section / first body
    line land at 89.9 / 108.2 / 147.2 / 177.8 pt from the page top against
    the exemplar's 89.8 / 108.2 / 147.3 / 177.6.
  - Figure 1.3 (thesis roadmap) removed as unnecessary.
  - Chapter One expanded from ~1,750 to ~2,260 words: sensing-layer
    economics, the duty-cycle and collision constraints behind the airtime
    argument, prior residue-arithmetic work on blockchain throughput, why the
    two mechanisms compose, and the methodological contribution.
  - DOCX heading sizes realigned (Heading 3 now 14 pt, matching Heading 2).
- PDF: 27 pages, leading 27.6 pt, 0 errors, 0 overfull boxes, 0 undefined
  citations, 0 undefined references, 0 em dashes.

### v04 — 2026-08-17

- Artifacts: `dist/thesis_v04.{tex,pdf,docx}`
- Commit: `230d3c9`
- Changes: _describe what changed in this iteration_

### v04 — 2026-08-17

- Artifacts: `dist/thesis_v04.{tex,pdf,docx}`
- Commit: `230d3c9`
- Changes: _describe what changed in this iteration_

### v04 — 2026-08-17

- Artifacts: `dist/thesis_v04.{tex,pdf,docx}`
- Commit: `230d3c9`
- Changes: _describe what changed in this iteration_

### v04 — 2026-08-17

- Artifacts: `dist/thesis_v04.{tex,pdf,docx}`
- Commit: `230d3c9`
- Changes: _describe what changed in this iteration_

### v04 — 2026-08-17

- Artifacts: `dist/thesis_v04.{tex,pdf,docx}`
- Commit: `230d3c9`
- Changes: _describe what changed in this iteration_

### v05 — 2026-08-17

- Artifacts: `dist/thesis_v05.{tex,pdf,docx}`
- Commit: `230d3c9`
- Changes: _describe what changed in this iteration_

### v06-2 - 2026-08-17

- Artifacts: `dist/thesis_v06-2.{tex,pdf,docx}`
- Changes:
  - Cover page rebuilt to match the supplied reference image, measured against
    the exemplar's page 1. Every element within **0.3 pt** of the exemplar:
    UNIVERSITY OF BUEA at 84.2 pt from the top against 84.0, faculty and
    department columns at 159.9 against 160.0, title at 260.5 against 260.5,
    "By" at 378.2 against 378.3, candidate block at 451.3 against 451.5,
    submission statement at 539.9 against 540.0, supervisors at 644.5 against
    644.6.
  - **Two supervisors**, both Associate Professor, under a single
    "Supervisors" heading flush left. No co-supervisor.
  - Title broken into three lines that each fit the 413 pt text width, as the
    exemplar's does; the previous break re-wrapped to four.
  - Chapter Two wired into `main.tex` and now builds.
  - Appendix added and labelled "APPENDIX A". `\backmatter` removed, because
    in the book class it switches off chapter numbering and left the appendix
    with no label.
  - `tools/expand_gls.py` now strips `\titleformat` and `\titlespacing`
    blocks before Pandoc, which otherwise aborts on titlesec's argument
    syntax. Brace counting is not enough: the first line of a `\titleformat`
    is itself balanced, so the continuation lines have to be dropped by shape.
- PDF: 40 pages. Chapter One p15, Chapter Two p26, References p36,
  Appendix A p40. 0 LaTeX errors, 0 overfull boxes, 0 undefined citations,
  0 undefined references, 0 em dashes.
- DOCX: 6,271 words, Times New Roman 12 pt, double spaced, 0 pt paragraph
  spacing, margins 3.5/2.5/2.5/2.5 cm.
### v04 — 2026-08-16

- Artifacts: `dist/thesis_v04.{tex,pdf,docx}`
- Changes:
  - Chapter One: removed the Bloom's-taxonomy meta-commentary paragraph and
    the per-objective `(Analyse)`/`(Create)`/`(Apply)`/`(Evaluate)` tags from
    §1.4; the objectives now read as direct statements.
  - Chapter Two (new): `chapters/chapter2_literature.tex`, following the
    guide's five-part skeleton (historical overview; theory and literature
    specific to the topic, six thematic subsections; cognate areas;
    critique and summary; contribution to the literature). Sourced from
    `references.bib` (113 distinct citations), the source article
    (`project fin update with reviewers/main_article.tex`) for the CRT,
    LoRa-airtime and M/D/1 formulas, and two of the candidate's own
    companion papers newly added to `references.bib`
    (`beloa2025bitcoincrt`, the Bitcoin/CRT parallelisation manuscript, and
    `beloasone2025hrbac`, the HRBAC formalisation manuscript), resolving
    the `%% VERIFY` marker left open in Chapter One since v3. Five original
    TikZ figures and five tables; ten new abbreviations added to
    `front/abbreviations.tex` (acid, cft, ecdsa, etsi, lpwan, rns, wsn,
    x509, plus corrections).
  - Back matter: `back/appendices.tex` (new), Appendix A (worked CRT/Garner
    reconstruction, extending Chapter Two's Eq. 2.5) and Appendix B (the
    HRBAC permission matrix reproduced from `beloasone2025hrbac`). Found
    and fixed a latent formatting bug in `main.tex`: `\backmatter` sets
    `\@mainmatterfalse`, which silently suppresses book.cls's
    chapter-numbering path, so appendix chapters printed no "APPENDIX A/B"
    label and an unnumbered ToC entry until `\@mainmattertrue` was
    restored around `\include{back/appendices}`.
  - `ubthesis.sty`: added `tabularx` (used throughout Chapter Two's and the
    appendix's tables).
  - `main.tex`: enabled `\include{chapters/chapter2_literature}` and the
    `\appendix` / `\include{back/appendices}` block, both previously
    commented out.
- PDF: 57 pages (up from 27 in v03), 0 undefined citations, 0 undefined
  references, 2 minor overfull hboxes (under 11 pt, both caption line
  wraps; within the tolerance §9 of `README.md` documents for
  hyphenation-off justified text).
- DOCX: converts cleanly; Pandoc numbers the two appendices as plain
  chapters 3 and 4 rather than "Appendix A/B" (a documented Pandoc
  limitation, README §6); the PDF remains authoritative.

### v05 — 2026-08-16

- Artifacts: `dist/thesis_v05.{tex,pdf,docx}`
- Changes: three correctness fixes from Codex's automated review of PR #96
  on the v04 commit, all confirmed against the actual codebase before
  fixing rather than taken on faith:
  - **PBFT fault-tolerance bound corrected.** Chapter Two claimed classical
    BFT protocols such as PBFT tolerate "the same $f = \lfloor(n-1)/2\rfloor$"
    as CFT protocols such as Raft. Byzantine agreement needs $n \geq 3f+1$
    replicas, so PBFT's bound is $f = \lfloor(n-1)/3\rfloor$, smaller, not
    the same. Fixed in both the prose (§2.2.5) and the consensus-taxonomy
    figure, with a concrete five-node example (two Raft-tolerated crashes
    vs. one PBFT-tolerated Byzantine node) added so the distinction is
    checkable at a glance.
  - **CRT-residue confidentiality overclaim corrected.** Chapter Two treated
    an intercepted CRT residue as disclosing "little" about the underlying
    value, formally analogous to a threshold secret-sharing share. A plain
    CRT residue is a deterministic function of the value, not a randomised
    share; it narrows the plaintext to roughly a $1/m_i$ fraction rather
    than leaking nothing, and how much that matters depends on the ratio
    between the plaintext's domain and the modulus, not on the
    reconstruction identity. Reworded in §2.2.3, §2.2.6 and the
    Contribution list to state that condition as what hypothesis H5 must
    establish, not as an already-settled result; this also brings Chapter
    Two into agreement with Chapter One, which already flagged H5 as
    unsupported.
  - **Appendix A's subset-recovery claim corrected against the actual
    firmware and gateway code.** The appendix claimed two-residue recovery
    "covers the scaled range of every sensor type this thesis deploys."
    Checked against `esp32/main/main.c::encode_sensor_value` (which packs
    soil moisture and a temperature bucket into one value, up to 823,295)
    and `gateway/crt_decode.py::decode` (which silently returns the
    smallest solution modulo whichever two moduli it receives, exact only
    below their product, at most 10,403): the claim does not hold for the
    deployed combined encoding, only for the single-value worked example
    in this appendix. Rewrote the appendix to state the qualifier
    explicitly and point to the source article's own measured figure,
    64.1% two-of-three recovery against a 66.7% theoretical figure, rather
    than implying 100% general recovery. The underlying firmware/gateway
    behaviour is unchanged; only the thesis text's characterisation of it
    is corrected. Whether the encoding scheme itself should change (keep
    combined values under every two-modulus product, or require all three
    residues before reconstructing) is now an open item for Chapter Three,
    not resolved here.
- PDF: 58 pages, 0 undefined citations, 0 undefined references, 2 minor
  overfull hboxes (<11 pt, same caption-wrap instances as v04).

### v07 — 2026-08-17

- Artifacts: `dist/thesis_v07.{tex,pdf,docx}`
- Commit: `0e98190`
- Changes: _describe what changed in this iteration_

### v07 — 2026-08-17

- Artifacts: `dist/thesis_v07.{tex,pdf,docx}`
- Commit: `c0b2630`
- Changes: _describe what changed in this iteration_

### v08 — 2026-08-17

- Artifacts: `dist/thesis_v08.{tex,pdf,docx}`
- Changes: restructuring and format fixes requested against v07, plus two
  latent front-matter bugs found and fixed while addressing the spacing
  complaint.
  - **Chapter Two:** removed "The Corpus Underlying This Review" (§2.2.7:
    the 120-paper composition table and publication-year chart), a section
    about the review's own retrieval methodology rather than about the
    literature itself. The four later mentions of "this corpus" that
    depended on it were reworded to stand alone. §2.1 renamed from
    "Historical Overview of the Theory and Research Literature" to
    "Introduction"; thirteen other self-referential "reviewed literature" /
    "this review" phrases across the chapter were reworded to "prior work"
    or dropped, so the chapter reads as an introduction followed by a
    thematic deep dive rather than narrating its own status as a review.
    Content and citations are otherwise unchanged, per the brief ("what has
    been done is good, I just want restructuring").
  - **Figures extracted from the source papers, not only drawn:** four
    raster figures added alongside the existing seven TikZ diagrams, each
    cropped from the actual PDF page and captioned with its source. Two
    from the candidate's own architecture manuscript
    `forcha2026basedparallel` (the five-tier system diagram, and the
    gateway-side residue-decode/ledger pipeline, both own copyright), one
    from the candidate's own HRBAC manuscript `beloasone2025hrbac` (the
    enrolment trust chain), and one from `gong2025edge`, an MDPI *Sensors*
    article, CC BY 4.0, credited as such in the caption. Placed next to the
    paragraph that already cites each source. Copyright approach follows
    `README.md` §8: own work freely, third-party only under a licence that
    permits reuse, source named in the caption.
  - **Figure and table captions shortened.** The three longest multi-sentence
    Chapter Two captions (the lineage timeline, the transmission taxonomy,
    the CRT pipeline comparison) and both Chapter One captions were cut to
    one concise sentence each; already-short captions were left alone.
  - **List of Figures / List of Tables now read "Figure 1", "Table 1", ...**
    instead of a bare number (`ubthesis.sty`: `\cftfigpresnum`,
    `\cftfigaftersnumb`, `\cftfignumwidth` and the `\cfttab...` equivalents).
  - **Large blank gap under the List of Contents / Figures / Tables
    headings, fixed at the root cause, not patched.** The visible gap
    traced to tocloft: once tocloft loads, its own `\AtBeginDocument` hook
    redefines `\tableofcontents`/`\listoffigures`/`\listoftables` to call
    `\@cftmaketoctitle`/`\@cftmakeloftitle`/`\@cftmakelottitle`, which
    reimplement book.cls's `\vspace*{50pt}` + empty `\Huge` heading line +
    `\vskip 40pt` band independently of `\@makeschapterhead` (a first,
    incorrect diagnosis that had no effect, confirmed with `\show` before
    being replaced). Found only by isolating `\tableofcontents` in a
    throwaway two-chapter test document and bisecting it down to the exact
    tocloft macro, since the standard skip lengths involved
    (`\cftbeforechapskip`, `\parskip`, `\raggedbottom`) all measured too
    small to account for it. All three title-making commands are now
    no-ops; `\ubfrontheading` already supplies the heading and the PDF
    bookmark.
  - **List of Abbreviations no longer strands its heading alone on a blank
    page with every entry pushed to the next page**, root-caused the same
    way: `\printunsrtglossary` opens with its own `\glossarysection`, which
    (with `\phantomsection` defined, i.e. with hyperref loaded) calls
    `\glsclearpage`, a bare `\clearpage`, before its own empty-titled
    section heading, discarding whatever else was on the page. Confirmed
    with a minimal reproduction (bisected against `style=long` vs
    `style=list`, longtable vs `\l@chapter` called directly, `singlespace`
    present vs absent) that isolated `\glossarysection` as the one
    remaining variable; disabled with `\renewcommand*{\glossarysection}[2][]{}`
    now that `\ubfrontheading` already supplies the heading.
  - **Preliminary pages set at 1.5 line spacing**, not the body's full
    double spacing: a new `ubonehalfspace` environment
    (`\setstretch{1.4375}`, matched to Word's 20.7pt "1.5 lines" for Times
    New Roman 12pt the same way `\setstretch{1.911}` was matched to Word's
    27.6pt "Double" in v02) now wraps the dedication, acknowledgements,
    abstract, and the Table of Contents / List of Figures / List of Tables /
    List of Abbreviations. Certification keeps its existing single spacing,
    a fixed-position form rather than running prose.
- PDF: 68 pages. Chapter One p14, Chapter Two p26, References p51, Appendix A
  p65, Appendix B p68. 8 figures in Chapter Two (4 TikZ, 1 pgfplots removed
  with the corpus section, 4 extracted from source PDFs), 185 works cited,
  0 LaTeX errors, 0 undefined citations, 0 undefined references, 2 minor
  overfull hboxes under 11pt (pre-existing caption line wraps, unchanged
  from v07).
- DOCX: converts cleanly; all four extracted figures embedded; the corpus
  section and every "reviewed literature" phrase confirmed absent from the
  generated `word/document.xml`.

### v07 - 2026-08-17

- Artifacts: `dist/thesis_v07.{tex,pdf,docx}`
- Corpus work:
  - Indexed all 120 PDFs in `lit-rev/papers/`, extracting front-matter text and
    abstracts from each.
  - Matched them against `thesis/references.bib`: 35 already had an entry, 85
    did not. Generated the 85 missing entries from the DOI-resolved metadata in
    `lit-rev/indexes/FINAL_INVENTORY.csv`, tagged with a `keywords` field
    recording corpus provenance. Bibliography grew 226 -> 311 entries.
  - Classified the corpus by theme and publication year from the extracted
    text, and used the real counts for Table 4 and Figure 3.
- Chapter Two extended from 907 to about 1,140 lines with five new subsections,
  all grounded in the corpus: the corpus composition itself; blockchain
  scalability and the parallelism argument; residue arithmetic beyond computer
  arithmetic; permissioned ledgers on constrained hardware; and identity,
  privacy and access control in adjacent domains. Closed with Research
  Frontiers and Partial Conclusion sections, following the exemplar's Chapter
  Two, which ends the same way.
- Chapter One: the prior-work paragraph on residue arithmetic in ledgers is now
  cited rather than asserted, which clears the standing `%% VERIFY` marker on
  that claim. Added corpus-grounded paragraphs on the sensing-layer reviews and
  on farm data tampering.
- `pgfplots` added to `ubthesis.sty`, needed by the corpus-year chart.
- Five cross-references in the new text pointed at labels from an older draft
  of Chapter Two; repointed at the labels the current chapter actually defines.
- PDF: 67 pages. Chapter One p15, Chapter Two p27, References p50, Appendix A
  p64, Appendix B p67. 7 figures, 5 tables, 185 works cited, 0 LaTeX errors,
  0 overfull boxes, 0 undefined citations, 0 undefined references, 0 em dashes.

### v09 — 2026-08-17

- Artifacts: `dist/thesis_v09.{tex,pdf,docx}`
- Changes: against v8, three requests: strip the candidate's own unpublished
  manuscripts out of the literature review, write Chapter Two in the first
  person, and expand it substantially from the 120-paper corpus. Also fixed
  the certification page and a real bibliographic-integrity problem found
  while doing the above.
  - **No more candidate's-own-work-as-literature.** Removed every citation
    to `beloa2025bitcoincrt` (the Bitcoin/CRT paper), `beloasone2025hrbac`
    (the HRBAC paper) and `forcha2026basedparallel` (the five-tier
    architecture paper) from Chapter Two, along with the three figures
    extracted from them in v8 (five-tier architecture, gateway pipeline,
    HRBAC trust chain) and the HRBAC formalisation
    (Equations 2.8-2.9 as they were numbered in v8). The HRBAC
    formalisation and its trust-chain figure now live in
    `back/appendices.tex` (Appendix B), self-contained rather than assumed
    from Chapter Two, since it is our own contribution and appendices are
    where a thesis's own derivations belong, not the literature review.
    Chapter Two's CRT and scalability sections were rewritten around
    published literature only; where the chapter used to cite our own
    architecture paper for the CRT-to-blockchain connection, it now states
    that connection as an observation from reading the residue-arithmetic
    and blockchain-scalability literatures side by side, explicitly
    flagged as not published by either literature, which is what the
    brief asked for under "talk about CRT, how it links to the blockchain
    etc.". The one remaining candidate-manuscript citation, in Chapter
    One's background section, was left as it is Chapter One's own
    rationale, not the literature chapter.
  - **First person throughout.** Every "this thesis argues/shows/deploys",
    "the candidate's own prior work" and similar third-person distancing
    phrase in Chapter Two rewritten to "we"/"our", including several that
    predated this request and were only caught while rewriting the
    sections around them. The file header now states the rule for future
    edits.
  - **Chapter Two roughly doubled in length and restructured as flat,
    numbered sections (2.1-2.17)** rather than one section's nested
    subsections, at the candidate's explicit request. New:
    Section 2.2, "Fundamentals of Blockchain Technology", ground-up:
    hash-chaining, permissioned vs permissionless, Hyperledger Fabric's
    architecture, chaincode, DAG-based alternatives (IOTA), and the
    \gls{ecdsa}/secp256k1 signing that every transaction relies on. The
    agriculture-blockchain section gained a new paragraph on
    commodity-specific traceability (soybean, Nepal ginger) and a
    feasibility study of blockchain and \gls{iot} for African agricultural
    supply chains, the closest deployment-context match in the corpus.
    The scalability section gained \gls{utxo} storage/throughput
    trade-offs, cloud-hosted scaling frameworks and multi-chain
    architectures. The identity section gained an IoT-blockchain
    authentication protocol as a real published alternative once the
    HRBAC formalisation moved to the appendix. Eleven new bib entries
    drawn into service from the previously-unused two-thirds of the
    120-paper corpus; none were candidate manuscripts.
  - **A real bibliographic-integrity problem, found while auditing
    citations for the above.** `references.bib` had accumulated 21
    duplicate papers under 51 different keys, apparently from repeated
    corpus-integration passes across v4-v7 pulling the same paper in
    twice under a different key each time. Several were cited as if
    independent sources in the same sentence (five different keys for one
    Kamilaris paper cited together at one point); two were outright
    wrong, a key named `ali2022secureIOT` and cited under "IoT-specific
    attack surfaces" actually held Salah et al.'s soybean-traceability
    paper, and a "water-quality ledgers" citation actually held the
    self-sovereign-identity paper already cited, correctly, one sentence
    earlier. Resolved by choosing one canonical key per duplicate
    (preferring whichever was already more used, or the better content
    match where usage was tied), redirecting every in-text citation,
    dropping the two outright-wrong citations from the sentences they
    didn't support rather than relabelling them, and deleting the 30 now
    orphaned duplicate `references.bib` entries. 311 entries before,
    281 after.
  - **Certification page rebuilt to match the supplied exemplar image**:
    university header, faculty/department two-column line, "The Thesis
    of NAME (matricule) entitled TITLE submitted to ... under the
    Supervision of", a Sign/Date block per supervisor (two here, the
    exemplar's one repeated), and the candidate's own Sign line at the
    foot. Previously a generic "This is to certify that..." paragraph
    form.
- PDF: 71 pages (up from 68). Chapter One p14, Chapter Two p26, References
  p52, Appendix A p66, Appendix B p69. 7 figures (5 TikZ, 2 raster: the
  HRBAC trust chain now in Appendix B, and the MDPI CC-BY-licensed edge-
  computing figure kept in Chapter Two), 5 tables, 184 works cited (was
  185; net of the dedup above and the new corpus additions), 0 LaTeX
  errors, 0 undefined citations, 0 undefined references, 2 pre-existing
  minor overfull hboxes unchanged from v7/v8.
- DOCX: regenerated; spot-checked `word/document.xml` directly and
  confirmed both removed manuscript keys are gone and the new
  "Fundamentals of Blockchain" section is present.

### v10 — 2026-08-18

- Artifacts: `dist/thesis_v10.{tex,pdf,docx}`
- Commit: `4df18b1`
- Changes: _describe what changed in this iteration_

### v10 — 2026-08-18

- Artifacts: `dist/thesis_v10.{tex,pdf,docx}`
- Commit: `4df18b1`
- Changes: _describe what changed in this iteration_

### v10 — 2026-08-18

- Artifacts: `dist/thesis_v10.{tex,pdf,docx}`
- Commit: `4df18b1`
- Changes: _describe what changed in this iteration_

### v10 — 2026-08-18

- Artifacts: `dist/thesis_v10.{tex,pdf,docx}`
- Commit: `4df18b1`
- Changes: _describe what changed in this iteration_

### v10 — 2026-08-18

- Artifacts: `dist/thesis_v10.{tex,pdf,docx}`
- Commit: `4df18b1`
- Changes: _describe what changed in this iteration_

### v10 - 2026-08-18

- Artifacts: `dist/thesis_v10.{tex,pdf,docx}`
- **DOCX figures fixed.** Pandoc has no TikZ or pgfplots engine and was
  dropping every picture silently, so the Word file carried 2 images against
  the PDF's 6. New `tools/render_tikz.py` compiles each picture standalone,
  with the thesis preamble and the real abbreviation definitions loaded, and
  rasterises it at 300 dpi; `tools/expand_gls.py` swaps the picture for that
  PNG before Pandoc runs. Word output now carries 7 images.
  - Matching is on whitespace-normalised, comment-stripped bodies. Exact
    string matching failed on 3 of 5 because `latexpand` reflows source and
    strips LaTeX comments when it flattens.
  - `\cite` is stubbed to `\mbox{}` in the standalone compile rather than to
    nothing: an empty expansion left a trailing `\\` with no line content and
    the compile died on "There's no line here to end".
- **Chapter Two soft headings.** The chapter had grown into a flat run of 19
  numbered sections. Ten thematic sections are now lettered soft headings
  under two new numbered parents, matching the exemplar's Chapter Two, which
  groups material the same way. Structure: 8 numbered sections, 11 lettered
  soft headings.
  - New `\ubsoft` macro in `ubthesis.sty`: 14 pt bold, flush left, unnumbered,
    counter resetting at each `\section`, listed in the ToC at subsection depth.
  - `\theubsoft` carries the parent section, so a `\ref` to a soft heading
    reads "Section 2.2(b)" instead of a bare "Section b". 21 such references
    resolve correctly; 0 bare-letter references remain.
  - `\ubsoft` is mapped onto `\subsection*{a) ...}` for the Word conversion,
    with the letters generated in the converter since LaTeX's counter is not
    available there. All 11 appear in the .docx.
- PDF: 71 pages. Chapter One p14, Chapter Two p26, References p52, Appendix A
  p66, Appendix B p69. 6 figures, 5 tables, 0 LaTeX errors, 0 overfull boxes,
  0 undefined citations, 0 undefined references, 0 em dashes.
- DOCX: 7 images, 5 tables, 15,991 words, Times New Roman 12 pt, double
  spaced, 0 pt paragraph spacing, margins 3.5/2.5/2.5/2.5 cm.

### v11 — 2026-08-24

- Artifacts: `dist/thesis_v11.{tex,pdf,docx}`
- Commit: `a10cc30`
- Changes: five new original TikZ diagrams added to Chapter One and Chapter
  Two per request ("the literature is good, add more diagrams"); no prose
  content changed in either chapter beyond the sentence introducing each new
  figure.
  - **Chapter One (+2 figures, 2 -> 4).** Figure 2, an "airtime is a rate
    limit" causal-chain diagram in §1.1 (Background), visualising the
    paragraph on duty-cycle silence and collision probability as one payload
    reduction paying three times. Figure 4, a "budget reallocation" stacked-bar
    diagram in §1.3 (Rationale), making concrete the chapter's central
    argument that CRT-freed airtime funds identity, integrity and privacy
    protection. Both are conceptual, no system-specific detail, consistent
    with the v2 decision (see that entry above) that Chapter One argues and
    does not specify.
  - **Chapter Two (+3 figures, 4 -> 7).** Figure 7, a "three resources"
    tree in §2.2(d) (CRT/RNS) showing storage and energy as established
    applications of residue decomposition against radio concurrency as the
    open branch this thesis occupies. Figure 9, an identity-enforcement
    pipeline in §2.3(e) (Identity, Access Control and Privacy) showing where
    the surveyed access-control literature's enforcement chain begins
    (the gateway's X.509 certificate) and the node-level gap upstream of it.
    Figure 10, a "partition-process-recombine" pattern diagram in §2.3(d)
    (Scalability), setting sharding, layer-two/multi-chain and cloud-hosted
    scaling as three established instances of the pattern the "common
    structure" paragraph already argues, against residue decomposition on a
    radio link as the fourth, open instance.
  - **Two real TikZ bugs found and fixed while building, not cosmetic.**
    `/tikz/out` and `/tikz/step` are reserved pgfplots/tikz keys (pgfplots is
    loaded by `ubthesis.sty` for Chapters Two and Four); naming a local node
    style `out` or `step` silently breaks with "requires a value" rather than
    a clear name-clash error. Renamed to `res` and `stg`. Worth remembering
    for any future figure: avoid short, generic style names when pgfplots is
    loaded.
  - **One layout bug found and fixed.** The Chapter One budget-reallocation
    figure's row labels used `align=right` without `anchor=east`, so the
    node centred on the anchor point instead of right-aligning to it, and the
    label text ran under the adjacent bar. Fixed by adding `anchor=east`;
    also tightened the bar width and label/text widths by about 3mm to clear
    a 9.35pt overfull-hbox this produced, and again on the Chapter Two
    partition-recombine figure's four leaf boxes, which at their first width
    would have spanned wider than the 15cm text width.
  - **One environment bug found and fixed, not a content bug.** The
    container had no LaTeX toolchain at session start. Installing
    `texlive-latex-base/-recommended/-extra`, `texlive-fonts-extra`,
    `texlive-science`, `texlive-bibtex-extra`, `texlive-pictures`, `latexmk`,
    `biber` and `pandoc` still left one missing file,
    `tex/generic/kastrup/binhex.tex`, required by `newtxtext.sty`/
    `newtxmath.sty` (this template's Times clone) but shipped in the
    separate `texlive-plain-generic` package, not pulled in by any of the
    above. `apt-file search binhex.tex` found it. Also missing initially:
    `latexpand` (in `texlive-extra-utils`), without which `build.sh` falls
    back to copying `main.tex` unflattened for the versioned `.tex` and,
    more importantly, the DOCX pipeline's `tools/expand_gls.py` then finds
    zero `tikzpicture` environments to substitute (they sit behind
    `\include`, not inlined), silently dropping every TikZ figure from the
    Word output down to the two raster ones. Confirmed by rebuilding after
    installing `texlive-extra-utils`: DOCX media count went from 2 to 12.
    Worth adding to `README.md` §2's package list for the next machine this
    template is built on.
- PDF: 73 pages (up from 71). Chapter One p1-13 (4 figures), Chapter Two
  p14-54 (7 figures: 6 TikZ + 1 raster), Appendix A p55-57, Appendix B p58-60
  (1 raster figure). 12 figures total (up from 6), 5 tables (unchanged), 281
  works cited (unchanged), 0 LaTeX errors, 0 undefined citations, 0 undefined
  references, 2 overfull hboxes (both pre-existing, in the unmodified
  transmission-taxonomy and consensus-taxonomy figures; the 5 new figures
  introduced no overfull or underfull boxes), 0 em dashes.
- DOCX: 12 images (up from 7), all figures embedded via the render-and-
  substitute pipeline; spot-checked media count directly against the PDF's
  figure count.

# LaTeX Instructions: Chapter One and the List of Abbreviations

How to build the UB PhD thesis so that **Chapter One and the List of
Abbreviations are produced together in a single compile**, and how each
iteration emits a new `.tex`, `.pdf` and `.docx`.

**Thesis:** *A Distributed Blockchain-Based Approach to Protect Identity,
Integrity and Privacy in Agricultural Data Processing*
Department of Computer Engineering, Faculty of Engineering and Technology,
University of Buea.

> **Build status: verified.** `./build.sh` has been run end to end. The current
> iteration (v02) produces a 27-page PDF with leading measured at 27.6 pt,
> 0 undefined citations, 0 undefined references, 0 overfull boxes, 0 underfull
> boxes and 0 missing figures, plus a Word file in UB format carrying the
> figures and captions. Committed artifacts are in `dist/`. Section 9 records
> the build errors already fixed so they do not recur on another machine.

---

## 1. Layout

```
thesis/
├── main.tex                     master file, front matter, \include list, back matter
├── ubthesis.sty                 UB formatting (fonts, margins, spacing, headings)
├── references.bib               224 entries, copied from the article
├── build.sh                     one iteration: .tex → .pdf → .docx, versioned
├── ITERATIONS.md                auto-appended build log
├── JOURNAL.md                   the research journey, updated as work proceeds
├── front/
│   ├── titlepage.tex            guide §3.2.1, seven required elements
│   ├── dedication.tex           page ii
│   ├── certification.tex        page iii, pre-defence and post-defence forms
│   ├── acknowledgements.tex     page iv, max one page
│   ├── abstract.tex             page v, MAX 400 WORDS
│   └── abbreviations.tex        ← abbreviation definitions
├── chapters/
│   └── chapter1_introduction.tex
├── tools/
│   ├── make_reference_docx.py   generates reference.docx in UB styles
│   └── expand_gls.py            expands \gls before Pandoc conversion
├── reference.docx               Pandoc style template (generated)
├── figures/
└── dist/                        versioned outputs, thesis_vNN.{tex,pdf,docx}
```

## 2. Install the toolchain

```sh
# Debian / Ubuntu
sudo apt-get update && sudo apt-get install -y \
    texlive-full latexmk biber pandoc

# Minimal alternative if texlive-full is too large (~5 GB)
sudo apt-get install -y texlive texlive-latex-extra texlive-fonts-extra \
    texlive-science texlive-bibtex-extra texlive-pictures texlive-plain-generic \
    texlive-extra-utils latexmk biber pandoc poppler-utils
```

Required packages beyond a base install: `glossaries-extra`, `biblatex`,
`newtx`, `fmtcount`, `titlesec`, `tocloft`, `setspace`, `quoting`, `hyphenat`,
`enumitem`, `siunitx`, `fancyhdr`, `geometry`, `caption`, `booktabs`, `tikz`,
`pgfplots`.

`texlive-plain-generic` is **required, not optional**, on a minimal install:
`newtxtext.sty`/`newtxmath.sty` (this template's Times clone) `\input`
`binhex.tex`, which is not part of `newtx` itself and is not pulled in by any
of the other packages above; without it the very first `pdflatex` run dies on
`File 'binhex.tex' not found`, before a single page is typeset. `apt-file
search binhex.tex` is how to find the owning package if this template is
ever rebuilt against a different TeX Live packaging.

`texlive-extra-utils` (for `latexpand`) is likewise **required, not
optional**, for a correct `.docx`, not merely for the flattened `.tex`
artifact `README.md` used to justify it. Without `latexpand`, `build.sh`
falls back to copying `main.tex` unflattened, and `tools/expand_gls.py` then
finds zero `tikzpicture` environments to substitute with rendered PNGs
(the chapters sit behind `\include`, not inlined), so every TikZ figure
silently vanishes from the Word output while the PDF stays correct. This
fails quietly, with no error and no warning worth noticing, so verify it
directly after any fresh install: the DOCX's image count
(`unzip -l dist/thesis_vNN.docx | grep -c word/media/`) should match the
PDF's figure count, not just the two or three raster ones.

## 3. Why Chapter One and the abbreviations come out in one pass

This is the part that usually goes wrong, so it is worth stating plainly.

The classic `glossaries` package writes abbreviation entries to an auxiliary
file, which then has to be sorted by an **external program** (`makeglossaries`,
`makeindex` or `xindy`) before a second LaTeX run can typeset the list. That
means the sequence `pdflatex → makeglossaries → pdflatex`, and if you forget
the middle step you get the notorious

```
This document is incomplete. The external file associated with the glossary
'abbreviations' (which should be called main.gls) hasn't been created.
```

We avoid the external step entirely. `main.tex` uses:

```latex
\usepackage[abbreviations,nomain,nopostdot,nogroupskip]{glossaries-extra}
\setabbreviationstyle[abbreviation]{long-short}
\input{front/abbreviations}
...
\printunsrtglossary[type=abbreviations,title={},style=long]
```

`\printunsrtglossary` belongs to the **"unsorted"** family of commands. It prints
entries directly from the definitions already in memory, in the order they were
defined, with no `.glo`/`.gls` round-trip and no `-shell-escape`. One
`pdflatex` pass therefore produces Chapter One **and** the List of
Abbreviations together.

The cost is that "unsorted" means exactly that, **the list appears in
definition order**. `front/abbreviations.tex` is therefore maintained in
alphabetical order by hand, with letter-group comments (`% ---- A ----`) to keep
it that way. This is a deliberate trade: manual alphabetisation of ~45 entries
in exchange for a build with no external glossary tooling.

> Note the exact command. `\printunsrtabbreviations` exists only in
> glossaries-extra ≥ 1.49 *with bib2gls*; on a stock TeX Live it is undefined
> and the build dies. `\printunsrtglossary[type=abbreviations]` has been
> available since v1.37 and is what this template uses.

**Fallbacks**, if your TeX distribution predates `glossaries-extra`:

| Option | Command | Trade-off |
|---|---|---|
| `glossaries` + `makeglossaries` | `pdflatex; makeglossaries main; pdflatex` | Auto-sorts, but needs the extra step |
| `glossaries` with `automake` | `\usepackage[automake]{glossaries}` | Auto-sorts in one command, needs `-shell-escape` |
| `acronym` package | `\begin{acronym}...\end{acronym}` | Simplest, but weaker plural and case handling |

## 4. Using abbreviations in the text

Define once in `front/abbreviations.tex`, then never type the expansion again:

```latex
\newabbreviation{crt}{CRT}{Chinese Remainder Theorem}
```

| Command | Output (first use) | Output (later uses) |
|---|---|---|
| `\gls{crt}` | Chinese Remainder Theorem (CRT) | CRT |
| `\glspl{gw}` | Gateways (GWs) | GWs |
| `\Gls{crt}` | Chinese Remainder Theorem (CRT) | CRT |
| `\glsxtrshort{crt}` | CRT | CRT |
| `\glsxtrlong{crt}` | Chinese Remainder Theorem | Chinese Remainder Theorem |

The long-then-short expansion on first use is automatic, that is the
`long-short` abbreviation style set in `main.tex`. It satisfies the guide's
§3.5.3 requirement that terms not in common use be given in full at first
instance, followed by the abbreviation in brackets.

**Two rules that save pain later:**

1. **Never hard-code an abbreviation.** Writing `CRT` literally instead of
   `\gls{crt}` means that occurrence is invisible to the abbreviation
   machinery, and if it happens to be the first occurrence in the document the
   expansion never fires at all.
2. **Watch the first use.** The expansion fires at the first `\gls` in
   *document order*, which includes the abstract. If you want the expansion to
   appear in Chapter One rather than in the abstract, use `\glsxtrshort{crt}`
   in the abstract, or reset with `\glsresetall` after the front matter.

## 5. Building

```sh
cd thesis
chmod +x build.sh        # once
./build.sh               # full: bibliography + convergent passes + docx
```

| Invocation | Does |
|---|---|
| `./build.sh` | Full build, three versioned artifacts in `dist/` |
| `./build.sh --quick` | Single `pdflatex` pass, PDF only, fast draft check |
| `./build.sh --chapter 1` | Front matter + Chapter One only |
| `./build.sh --no-docx` | Skip the Word conversion |

Each run allocates the next free iteration number and writes:

```
dist/thesis_v01.tex      flattened single-file source
dist/thesis_v01.pdf      typeset output
dist/thesis_v01.docx     Word conversion for supervisor mark-up
```

Nothing is ever overwritten, `v02` is written alongside `v01`, so every
iteration you send to your supervisor stays reproducible. The script also
appends a stanza to `ITERATIONS.md` with the version, date and commit hash;
fill in the "Changes" line before committing.

## 6. The `.docx` conversion

Pandoc converts the flattened `.tex`. Two things to know:

- **`reference.docx` is generated, not hand-edited.**
  `tools/make_reference_docx.py` starts from Pandoc's default template and
  pins Normal to Times New Roman 12 pt double-spaced justified, Heading 1/2/3
  to 16 pt bold caps / 14 pt bold / 12 pt bold in black, margins to
  3.5/2.5 cm, and adds a top-right PAGE field. `build.sh` runs it
  automatically if `reference.docx` is absent.

  Two traps it works around, both of which bite anyone editing the default
  template by hand: Pandoc's heading styles reference **theme fonts**
  (`w:rFonts/@w:asciiTheme`), which Word resolves in preference to the font
  name, so headings stay Calibri unless the theme attributes are deleted; and
  they carry an **accent colour** (`4F81BD`), so every heading prints blue.

- **Abbreviations are expanded before conversion.** Pandoc does not understand
  `\gls`, `\glspl` or `\printunsrtglossary` and drops them silently, which
  would strip every abbreviation *and* the whole List of Abbreviations out of
  the Word file. `tools/expand_gls.py` rewrites them from
  `front/abbreviations.tex`, reproducing first-use expansion, and substitutes
  a description list for the printed glossary. It also maps `\ubfrontheading`
  onto `\section*` so front-matter headings survive.

- **Pandoc will not reproduce everything.** TikZ diagrams, `algorithm2e`
  pseudocode, `siunitx` units and custom `\newcommand` macros degrade or drop.
  The `.docx` is a **review artifact for supervisor comments**, never the
  submission format. The PDF from LaTeX is the authoritative output.

## 7. Auditing the abbreviations list

The guide expects the list to cover what the text actually uses. Two checks:

```sh
# Abbreviations DEFINED but never used: candidates for deletion
cd thesis
for k in $(grep -oP '\\newabbreviation\{\K[^}]+' front/abbreviations.tex); do
  grep -rqE "\\\\[Gg]lspl?\{$k\}|\\\\glsxtr(short|long)\{$k\}" chapters/ front/ \
    || echo "UNUSED: $k"
done

# Capitalised strings in the text that look like undefined abbreviations
grep -rhoE '\b[A-Z]{2,8}\b' chapters/*.tex | sort -u
```

Run both before every submission to the Departmental Scientific Committee.

## 8. Figures

Three sourcing routes, in order of preference:

1. **Generate your own** from measured data, TikZ/PGFPlots for schematics and
   plots, which stays vector and matches the document fonts. The article in
   `project fin update with reviewers/main_article.tex` already loads `tikz`
   and `pgfplots` and contains reusable figure code.
2. **Reuse the article's figures**, `farm.png`, `5 layers.png`, `RBAC.png`,
   `crt_new.png`, `crt workflow.png`, `espn.png`, `pi.png`, `actcomd.png` are
   already in the article directory and are your own work.
3. **Third-party images**, only with a licence that permits reuse (CC-BY,
   CC0, or explicit permission), and cite the source in the caption. A figure
   lifted from a paper without permission is a copyright problem *and* a
   plagiarism-check problem, and the thesis is scanned for both (guide §5.5).

`figures/extracted/` holds route-2/3 examples for Chapter Two: pages cropped
(300dpi, whitespace-trimmed) from the actual source PDFs in `lit-rev/papers/`
and the candidate's own manuscripts, rather than redrawn. Three are the
candidate's own prior work (routes 1/2); one, `gong2025-*`, is reproduced
under CC BY 4.0 from an MDPI article with the licence and source named in its
caption (route 3). `thesis/JOURNAL.md`'s v8 entry records how each was
cropped.

Caption every figure and refer to it in the text. `\listoffigures` in
`main.tex` builds the List of Figures automatically.

## 9. First-run troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `File 'glossaries-extra.sty' not found` | Package missing | `sudo apt-get install texlive-latex-extra` |
| `Font 'Times New Roman' not found` | Compiling with XeLaTeX on a machine without the MS font | Use `pdflatex`, `ubthesis.sty` falls back to `newtx`, a metric-compatible Times |
| `Undefined control sequence \NUMBERstring` | `fmtcount` missing | `sudo apt-get install texlive-latex-extra` |
| `Command \Bbbk already defined` | `newtxmath` defines it before `amssymb` | Already fixed, `ubthesis.sty` does `\let\Bbbk\relax` first |
| `Undefined control sequence \printunsrtabbreviations` | Command needs glossaries-extra ≥ 1.49 with bib2gls | Already fixed, `main.tex` uses `\printunsrtglossary[type=abbreviations]`, available since v1.37 |
| `I can't write on file 'chapters/....aux'` | `-outdir` does not create subdirectories for `\include` | Already fixed, `build.sh` pre-creates `build/chapters`, `build/front`, `build/back` |
| `Package biblatex Error: Biber output not found` | Biber not run | Use `./build.sh`, not a bare `pdflatex` |
| List of Abbreviations empty | `\printunsrtglossary` before `\input{front/abbreviations}` | Definitions must be loaded in the preamble, before `\begin{document}` |
| Abbreviation never expands | Hard-coded in the text instead of `\gls{...}` | See §4 |
| Chapter heading not `CHAPTER ONE` | `fmtcount` missing or `\thechapterword` clash | Check `fmtcount` is installed |
| Overfull `\hbox` warnings everywhere | Hyphenation disabled per guide §3.1g | Expected, `\sloppy` and `\emergencystretch` absorb it |

## 10. Format compliance

`ubthesis.sty` implements `report/UB-PhD-Thesis-Format-Spec.md`:

| Requirement | Implementation |
|---|---|
| Times New Roman 12 pt | `newtx` (pdflatex) or `fontspec` (xelatex) |
| Double spacing | `setspace` `\doublespacing` |
| Margins 3.5 / 2.5 cm | `geometry` |
| Page number top right, ≥1.5 cm in | `fancyhdr` + `headsep` |
| Roman front matter, arabic body | `\frontmatter` / `\mainmatter` |
| Headings 16/14/12 pt bold | `titlesec` |
| Blank page + repeat title page | `main.tex` front matter block |
| No word breaks at line ends | `hyphenat` with `none` |
| Quotations indented 1.5 cm, single-spaced | redefined `quotation` |
| Footnotes single-spaced | `footmisc` |

Items the template **cannot** enforce, and you must supply: abstract ≤ 400
words, acknowledgements ≤ 1 page, body length 150–250 pages, author's index,
subject index, and the CV (≤ 2 pages) after the bibliography. All are mandatory
under §4.1 of the guide. See the checklist in
`report/UB-PhD-Thesis-Format-Spec.md` §8.

## 11. Related documents

| File | Covers |
|---|---|
| `report/UB-PhD-Thesis-Engineering-Steps.md` | The procedural side, supervisor, proposal, seminars, defence file, viva |
| `report/UB-PhD-Thesis-Format-Spec.md` | The measured typographic specification this template implements |
| `thesis/JOURNAL.md` | The research journey, decisions and open questions |
| `thesis/ITERATIONS.md` | Auto-generated build log |
| `project fin update with reviewers/main_article.tex` | Source article that Chapter One draws on |

# UB PhD Thesis — Typographic Format Specification

Font, size, spacing and layout for a University of Buea PhD thesis, measured from a
defended exemplar and cross-checked against the official guide.

**Sources**

| | |
|---|---|
| Prescription | `report/The-UB-Thesis-and-Dissertation-Guide-2.pdf` — UB Postgraduate School, 2021, §3.1–3.8 and §4.1 |
| Exemplar | `report/TCHUINDJANG TCHOKOTE Emmanuel Ludivin PhD_JUNE.pdf` — *A Multimodal Approach Based on Adversarial Machine Learning for Analysis of Social Media Messages*, PhD in Software Engineering, Dept. of Computer Engineering, Faculty of Engineering and Technology, UB, May 2025 |

The guide specifies paper, spacing, margins and page-number position, but **never states a font
family or point size**. Those come from the exemplar, which is where the de facto house style
lives. Figures below were measured from the PDF's text-placement matrices, not eyeballed.

---

## 1. Fonts and sizes (measured from the exemplar)

| Element | Font | Size | Share of text |
|---|---|---|---|
| **Body text** | Times New Roman | **12 pt** | 90.4% |
| Emphasis, captions | Times New Roman *Italic* | 12 pt | 1.9% |
| Run-in / subsection headings | Times New Roman **Bold** | 12 pt | 1.2% |
| Section headings, title-page text | Times New Roman **Bold** | **14 pt** | 4.1% |
| Major headings — `DEDICATION`, `ACKNOWLEDGMENTS`, `ABSTRACT`, `TABLE OF CONTENTS` | Times New Roman **Bold**, all caps | **16 pt** | 0.2% |
| Equations | Cambria Math | 12 pt (8.5 pt sub/superscript) | 0.4% |
| *(unintended)* stray text boxes and captions | Calibri | 11 pt / 9 pt | 0.7% |

**Heading hierarchy actually used:**

```
16 pt bold CAPS   Front-matter titles and chapter titles
14 pt bold        CHAPTER ONE, CHAPTER TWO … and numbered section headings
12 pt bold        Subsection and run-in headings
12 pt regular     Body
12 pt italic      Emphasis, figure and table captions
```

> **Clean-up note.** The ~0.7% of Calibri is Microsoft Word's default font leaking into text
> boxes and captions that were never restyled. Select all and set Times New Roman before
> submitting; the PG School checks format at deposit (§5.9c).

## 2. Page layout

| Measure | Exemplar (measured) | Guide (§3.1) | Match |
|---|---|---|---|
| Paper | A4, 210 × 297 mm | Good-quality white A4 | ✅ |
| Printing | One side only | One side only | ✅ |
| **Left margin** | **35.0 mm** | 3.5 cm | ✅ |
| Right margin | 29.2 mm | 2.5 cm | ⚠️ wider |
| Top margin (body text) | 29.0 mm | 2.5 cm | ⚠️ wider |
| Bottom margin | 34.8 mm | 2.5 cm | ⚠️ wider |
| Text block width | ≈ 144 mm | — | — |
| **Line spacing** | **27.6 pt** baseline-to-baseline | Double-spaced | ✅ |
| Alignment | Justified | not specified | — |
| Page number position | Top right, 18.9 mm from top edge, flush to right text edge | Upper right, ≥ 1.5 cm into the page | ✅ |

**On the 27.6 pt line spacing:** this is exactly Word's **"Double"** setting for Times New Roman
12 pt — Word's single line height for TNR 12 is 13.8 pt, so double is 27.6 pt, not 24 pt. Do not
try to hit 24 pt with "Exactly" spacing; just set Line spacing → Double. Blocks measured at
20.7 pt are Word's "1.5 lines", used for indented material.

Follow the **guide's** margins (3.5 cm left, 2.5 cm elsewhere) rather than the exemplar's —
the wider right/top/bottom margins are drift, not a requirement. The 3.5 cm left margin exists
so the bound volume can be trimmed after binding without eating into the text.

## 3. Page numbering scheme

| Section | Numbering | Position |
|---|---|---|
| Title page | unnumbered | — |
| Dedication | `ii` | top right |
| Certification | `iii` | top right |
| Acknowledgements | `iv` – `v` | top right |
| Abstract | `vi` | top right |
| Table of contents, lists of figures/tables/abbreviations | lowercase roman, continuing | top right |
| Body, from `CHAPTER ONE` | arabic, restarting at **1** | top right |

The guide (§3.2, Appendix VI) fixes the front-matter sequence as: dedication `ii`,
certification `iii`, acknowledgements `iv`, abstract `v`, contents `vi`, with any further lists
(figures, tables, abbreviations, plates, illustrations) continuing the roman sequence from where
the contents pages end.

## 4. Front-matter page order

Per the guide (§3.2.1–3.2.5, Appendix VI):

1. **Title page** — University of Buea · Faculty and Department · full title in capitals · author name with matriculation number and previous qualifications · the degree statement · supervisor name(s) and rank · month and year
2. **Blank page**
3. **Repeat of the title page**
4. **Dedication** (ii) — brief, one or two lines
5. **Certification** (iii) — pre-defence form before the viva, post-defence form in the final document
6. **Acknowledgements** (iv) — must not exceed one page
7. **Abstract** (v) — **≤ 400 words** for a PhD
8. **Table of contents** (vi)
9. Lists of figures, tables, abbreviations, illustrations, appendices

## 5. Back matter (PhD-specific, §4.1)

1. **Bibliography / References**
2. **Appendices**
3. **Author's index** — PhD only
4. **Subject index** — PhD only
5. **Curriculum vitae** — PhD only, **≤ 2 pages**, placed *after* the bibliography, covering academic and employment record and the publication list, marking which publications derive from the thesis

## 6. Word setup — copy this

```
Font                Times New Roman, 12 pt
Paragraph           Line spacing:  Double
                    Alignment:     Justified
                    Spacing after: one extra line between paragraphs   (§3.1d)
                    Hyphenation:   OFF — do not break words at line ends   (§3.1g)

Page setup          Paper:   A4
                    Margins: Left 3.5 cm · Top 2.5 cm · Right 2.5 cm · Bottom 2.5 cm
                    Pages:   One side only

Header              Page number, top right, ≥ 1.5 cm into the page

Heading styles      Heading 1 → Times New Roman 16 pt Bold, ALL CAPS
                    Heading 2 → Times New Roman 14 pt Bold
                    Heading 3 → Times New Roman 12 pt Bold

Section breaks      Roman i–vi for front matter
                    Arabic restarting at 1 from Chapter One, continuous to the end

Quotations          ≤ 4 lines: inline, in quotation marks
                    > 4 lines: new line, indent 1.5 cm, single-spaced, NO quotation marks
Footnotes           Single-spaced
```

## 7. Deviations in the exemplar — do not copy

The sample thesis is a useful visual reference, but it departs from the guide in six places.
Correct these in your own document.

| # | Deviation | Guide requirement |
|---|---|---|
| 1 | No blank page and no repeat of the title page — goes straight from title to dedication | §3.2.2–3.2.3: p.1 title → p.2 blank → p.3 repeat of title |
| 2 | Lowercase roman numerals **restart after the table of contents** — `ii`–`ix` are used twice | Continuous roman sequence through the front matter |
| 3 | Right, top and bottom margins ≈ 29 / 29 / 35 mm | 2.5 cm on all three non-binding edges |
| 4 | **No author's index and no subject index** | §4.1(c) — both mandatory for a PhD |
| 5 | **No curriculum vitae** after the bibliography | §4.1(d) — mandatory, ≤ 2 pages, with publication list |
| 6 | Body runs to **122 pages** | §2.4 Table 2 — 150–250 pages for Pure and Applied Sciences (+10% tolerance on the upper bound) |

Compliant elements worth noting: abstract at **338 words** sits inside the 400-word PhD ceiling;
the 3.5 cm left margin, A4 stock, double spacing, single-sided printing and top-right page
numbers all match the guide exactly.

## 8. Pre-submission format checklist

- [ ] Times New Roman 12 pt everywhere — no stray Calibri in text boxes, captions or tables
- [ ] Line spacing set to Double (27.6 pt), except quotations and footnotes (single)
- [ ] Margins 3.5 cm left, 2.5 cm top/right/bottom
- [ ] Title page → blank page → repeat of title page → dedication
- [ ] Certification page uses the **post-defence** form in the final document
- [ ] Roman numerals continuous i → vi and beyond; arabic restarts at Chapter One
- [ ] Page numbers top right, ≥ 1.5 cm into the page, on every numbered page
- [ ] Abstract ≤ 400 words
- [ ] Acknowledgements ≤ 1 page
- [ ] "Doctor of Philosophy Degree" wording in title and certification pages
- [ ] Author's index present
- [ ] Subject index present
- [ ] CV present after the bibliography, ≤ 2 pages, publications from the thesis marked
- [ ] Body length 150–250 pages
- [ ] Hyphenation off; no words broken at line ends
- [ ] Citation style consistent and approved by the Departmental Scientific Committee
- [ ] Full proofread and spell-check (§3.1j)
- [ ] Soft/temporary binding for examination copies; hard cover only after the defence

---

**See also:** `report/UB-PhD-Thesis-Engineering-Steps.md` — the procedural side of the same guide
(supervisor and topic registration, proposal, seminar sequence and weighting, publication
requirement, defence file, review, viva, binding and deposit).

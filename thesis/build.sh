#!/usr/bin/env bash
# =============================================================================
# build.sh — one iteration of the thesis: .tex -> .pdf -> .docx
#
# Every run stamps a new iteration number and writes THREE versioned artifacts
# into dist/, so no iteration ever overwrites a previous one:
#
#     dist/thesis_vNN.tex     flattened single-file LaTeX source
#     dist/thesis_vNN.pdf     typeset output
#     dist/thesis_vNN.docx    Word conversion for supervisor mark-up
#
# Usage:
#     ./build.sh                  full build (bibliography + 3 LaTeX passes)
#     ./build.sh --quick          PDF only, single pass, no biber, no docx
#     ./build.sh --chapter 1      build only Chapter One + front matter
#     ./build.sh --no-docx        skip the Word conversion
#
# Requires: texlive-full (or texlive + glossaries, biblatex, newtx, fmtcount),
#           biber, latexmk, pandoc, and latexpand for flattening.
# =============================================================================

set -euo pipefail
cd "$(dirname "$0")"

QUICK=0; NO_DOCX=0; ONLY_CHAPTER=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --quick)     QUICK=1; NO_DOCX=1; shift ;;
    --no-docx)   NO_DOCX=1; shift ;;
    --chapter)   ONLY_CHAPTER="$2"; shift 2 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

# build/ mirrors the source subdirectories: \include writes its .aux files
# alongside the chapter path inside -outdir, and LaTeX will not create them.
mkdir -p dist build build/chapters build/front build/back

# --- iteration number -------------------------------------------------------
# Monotonic, derived from what is already in dist/. Never reuses a number.
VER=$(( $(ls dist/thesis_v*.pdf 2>/dev/null \
          | sed -E 's/.*_v0*([0-9]+)\.pdf/\1/' \
          | sort -n | tail -1 || echo 0) + 1 ))
VER=$(printf "%02d" "$VER")
STAMP=$(date +%Y-%m-%d)
echo "==> Iteration v${VER}  (${STAMP})"

# --- optional single-chapter build -----------------------------------------
MAIN=main
if [[ -n "$ONLY_CHAPTER" ]]; then
  MAIN=build/chapter_only
  # Comment out every \include{chapters/...} except the requested chapter.
  awk -v keep="chapters/chapter${ONLY_CHAPTER}_" '
    /^\\include\{chapters\// && index($0, keep) == 0 { print "%" $0; next }
    { print }
  ' main.tex > "${MAIN}.tex"
  echo "==> Chapter-only build: chapter ${ONLY_CHAPTER}"
fi

# --- LaTeX ------------------------------------------------------------------
# NOTE: no makeglossaries step. The List of Abbreviations is produced by
# \printunsrtabbreviations, which resolves inside LaTeX itself. Chapter One and
# the abbreviations list therefore appear together on the very first pass.
if [[ $QUICK -eq 1 ]]; then
  pdflatex -interaction=nonstopmode -halt-on-error \
           -output-directory=build "${MAIN}.tex"
else
  # latexmk detects biblatex from the .bcf and runs biber itself, then reruns
  # LaTeX until labels, TOC and citations converge.
  latexmk -pdf -interaction=nonstopmode -halt-on-error \
          -outdir=build "${MAIN}.tex" || {
    echo "!! latexmk failed — see build/$(basename "$MAIN").log" >&2; exit 1; }
fi

BASE=$(basename "$MAIN")
cp "build/${BASE}.pdf" "dist/thesis_v${VER}.pdf"
echo "    dist/thesis_v${VER}.pdf"

# --- flattened .tex ---------------------------------------------------------
# A single self-contained source file: what you send to a co-author or archive
# alongside the PDF of the same iteration.
if command -v latexpand >/dev/null 2>&1; then
  latexpand "${MAIN}.tex" > "dist/thesis_v${VER}.tex"
else
  echo "    (latexpand not found — copying main.tex unflattened)"
  cp "${MAIN}.tex" "dist/thesis_v${VER}.tex"
fi
echo "    dist/thesis_v${VER}.tex"

# --- .docx ------------------------------------------------------------------
# Pandoc converts the flattened source. reference.docx carries the UB styles
# (Times New Roman 12 pt, double spacing, 3.5/2.5 cm margins) so the Word
# output lands close to the required format rather than in Pandoc defaults.
if [[ $NO_DOCX -eq 0 ]]; then
  if command -v pandoc >/dev/null 2>&1; then
    # Pandoc drops \gls/\glspl and \printunsrtglossary silently, which would
    # strip every abbreviation and the whole List of Abbreviations out of the
    # Word file. Expand them to plain text first.
    # TikZ and pgfplots pictures must be rasterised first: Pandoc has no
    # engine for them and drops the environments silently, which is how the
    # Word file kept losing figures the PDF had.
    python3 tools/render_tikz.py || echo "!! TikZ render failed; docx figures may be missing" >&2
    python3 tools/expand_gls.py "dist/thesis_v${VER}.tex" "build/for_docx.tex"

    [[ -f reference.docx ]] || {
      echo "    building reference.docx (UB styles) ..."
      python3 tools/make_reference_docx.py || true
    }

    PANDOC_ARGS=(
      "build/for_docx.tex"
      -f latex -t docx
      --number-sections
      --bibliography=references.bib
      --citeproc
      -o "dist/thesis_v${VER}.docx"
    )
    [[ -f reference.docx ]] && PANDOC_ARGS+=(--reference-doc=reference.docx)
    [[ -d figures ]]        && PANDOC_ARGS+=(--resource-path=.:figures)
    pandoc "${PANDOC_ARGS[@]}" 2>/dev/null && echo "    dist/thesis_v${VER}.docx" \
      || echo "!! pandoc conversion failed — PDF and TeX are still valid" >&2
  else
    echo "!! pandoc not installed — skipping .docx" >&2
  fi
fi

# --- record the iteration ---------------------------------------------------
{
  echo ""
  echo "### v${VER} — ${STAMP}"
  echo ""
  echo "- Artifacts: \`dist/thesis_v${VER}.{tex,pdf,docx}\`"
  echo "- Commit: \`$(git rev-parse --short HEAD 2>/dev/null || echo 'n/a')\`"
  echo "- Changes: _describe what changed in this iteration_"
} >> ITERATIONS.md

echo "==> Done. Append your notes to thesis/ITERATIONS.md and JOURNAL.md."

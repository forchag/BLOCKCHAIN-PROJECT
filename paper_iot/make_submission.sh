#!/usr/bin/env bash
#
# Build the two Elsevier submission packages from the single master source.
#
#   <version>-single-column  cas-sc, one column
#   <version>-double-column  cas-dc, two columns
#
# The manuscript body is identical in both.  Only the document class and the
# \ifdoublecol switch differ, so the two packages cannot drift apart.  Each zip
# is self-contained: class files, bibliography, generated macros, tables,
# figure data and the supplementary-material document all travel with it, and
# it compiles with pdflatex + bibtex alone.
#
# Usage:  bash paper_iot/make_submission.sh [version]      (default V01)
set -euo pipefail
cd "$(dirname "$0")"

VERSION="${1:-V01}"
DIST="dist"
MASTER="hrbac_iot_cas.tex"
STEM="hrbac_iot"

echo "==> regenerating derived numbers, tables and figure data"
python3 ../analysis/derive_results.py > /dev/null
python3 ../analysis/derive_policy_table.py > /dev/null

# Clear only this version's staging trees and archives.  Previously released
# versions and hand-written files such as dist/README.md are left alone, so a
# rebuild of V02 cannot destroy the V01 a reviewer may be holding.
mkdir -p "$DIST"
rm -rf "$DIST"/${VERSION}-*-column "$DIST"/${VERSION}-*.zip \
       "$DIST"/${VERSION}-*.pdf

# Files every package needs, beyond its own main .tex.
ASSETS=(derived_numbers.tex commit_hash.tex references.bib
        cas-sc.cls cas-dc.cls cas-common.sty cas-model2-names.bst
        supplementary.tex supplement_algorithms.tex supplement_operational.tex
        supplement_extra.tex
        highlights.txt)

build_variant () {
  local name="$1" cls="$2" flag="$3"
  local dir="$DIST/${VERSION}-${name}"
  local main="$dir/${STEM}_${name//-/_}.tex"

  echo "==> building $name ($cls)"
  mkdir -p "$dir"
  cp "${ASSETS[@]}" "$dir/"
  cp -r tables figdata "$dir/"

  # Swap the class and set the column switch. Everything else is untouched.
  sed -e "s|^\\\\documentclass\\[a4paper,fleqn\\]{cas-sc}|\\\\documentclass[a4paper,fleqn]{${cls}}|" \
      -e "s|^\\\\newif\\\\ifdoublecol\\\\doublecolfalse|\\\\newif\\\\ifdoublecol\\\\${flag}|" \
      "$MASTER" > "$main"

  ( cd "$dir"
    local stem; stem="$(basename "$main" .tex)"
    pdflatex -interaction=nonstopmode "$stem" > /dev/null 2>&1 || true
    bibtex   "$stem" > /dev/null 2>&1 || true
    pdflatex -interaction=nonstopmode "$stem" > /dev/null 2>&1 || true
    pdflatex -interaction=nonstopmode "$stem" > build.log 2>&1 || true
    grep -E "^Output written" build.log || {
      echo "   FAILED to produce a PDF for $name"; sed -n '/^!/,+4p' build.log | head -20; exit 1; }
    # The supplementary-material document is single-column in both packages.
    # It now cites the same bibliography as the main article (the
    # related-system comparison table), so it needs the same
    # pdflatex/bibtex/pdflatex/pdflatex sequence.
    pdflatex -interaction=nonstopmode supplementary > /dev/null 2>&1 || true
    bibtex supplementary > /dev/null 2>&1 || true
    pdflatex -interaction=nonstopmode supplementary > /dev/null 2>&1 || true
    pdflatex -interaction=nonstopmode supplementary > supp.log 2>&1 || true
    grep -qE "^Output written" supp.log || {
      echo "   FAILED to produce the supplementary PDF for $name"
      sed -n '/^!/,+4p' supp.log | head -20; exit 1; }

    # Keep the .bbl (Elsevier compiles from it) and the PDFs; drop intermediates.
    rm -f ./*.aux ./*.blg ./*.out ./*.spl ./*.abs build.log supp.log \
          missfont.log ./*.log ./*.toc
  )

  cp "$dir/${STEM}_${name//-/_}.pdf" "$DIST/${VERSION}-${name}.pdf"
  ( cd "$DIST" && zip -q -r "${VERSION}-${name}.zip" "${VERSION}-${name}" )
  echo "    -> $DIST/${VERSION}-${name}.zip"
}

build_variant "single-column" "cas-sc" "doublecolfalse"
build_variant "double-column" "cas-dc" "doublecoltrue"

echo
echo "==> packages"
ls -la "$DIST"/*.zip

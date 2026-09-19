#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"

# Regenerate the repository's derived values first. This writes the canonical
# generated macros, figure data and tables under paper_iot/.
if [ -f "$ROOT/analysis/derive_results.py" ]; then
  (cd "$ROOT/paper_iot" && python3 ../analysis/derive_results.py)
  (cd "$ROOT/paper_iot" && python3 ../analysis/derive_policy_table.py)
  cp "$ROOT/paper_iot/derived_numbers.tex" "$HERE/derived_numbers.tex"
  cp "$ROOT/paper_iot/commit_hash.tex" "$HERE/commit_hash.tex"
  cp -r "$ROOT/paper_iot/figdata/." "$HERE/figdata/"
  cp -r "$ROOT/paper_iot/tables/." "$HERE/tables/"
fi

cd "$HERE"
rm -f hrbac_iot_cas.aux hrbac_iot_cas.bbl hrbac_iot_cas.blg hrbac_iot_cas.log
pdflatex -interaction=nonstopmode hrbac_iot_cas.tex >/tmp/v11-pdflatex-1.log
bibtex hrbac_iot_cas >/tmp/v11-bibtex.log
pdflatex -interaction=nonstopmode hrbac_iot_cas.tex >/tmp/v11-pdflatex-2.log
pdflatex -interaction=nonstopmode hrbac_iot_cas.tex >/tmp/v11-pdflatex-3.log

mkdir -p submission supplement
cp hrbac_iot_cas.pdf submission/V11-single-column.pdf

# Build the same manuscript with the CAS double-column class when the local
# TeX installation provides it.  The source body is identical; only the class
# and the column flag differ, so the two PDFs cannot drift scientifically.
sed -e 's/\\doublecolfalse/\\doublecoltrue/' \
    -e 's/\\documentclass\[a4paper,fleqn\]{cas-sc}/\\documentclass[a4paper,fleqn]{cas-dc}/' \
    hrbac_iot_cas.tex > hrbac_iot_cas_dc.tex
rm -f hrbac_iot_cas_dc.aux hrbac_iot_cas_dc.bbl hrbac_iot_cas_dc.blg \
      hrbac_iot_cas_dc.log hrbac_iot_cas_dc.out hrbac_iot_cas_dc.abs
pdflatex -interaction=nonstopmode -jobname=hrbac_iot_cas_dc hrbac_iot_cas_dc.tex >/tmp/v11-dc-1.log
bibtex hrbac_iot_cas_dc >/tmp/v11-dc-bibtex.log
pdflatex -interaction=nonstopmode -jobname=hrbac_iot_cas_dc hrbac_iot_cas_dc.tex >/tmp/v11-dc-2.log
pdflatex -interaction=nonstopmode -jobname=hrbac_iot_cas_dc hrbac_iot_cas_dc.tex >/tmp/v11-dc-3.log
cp hrbac_iot_cas_dc.pdf submission/V11-double-column.pdf

pdflatex -interaction=nonstopmode supplementary.tex >/tmp/v11-supp-1.log
bibtex supplementary >/tmp/v11-supp-bib.log || true
pdflatex -interaction=nonstopmode supplementary.tex >/tmp/v11-supp-2.log
pdflatex -interaction=nonstopmode supplementary.tex >/tmp/v11-supp-3.log
cp supplementary.pdf supplement/supplementary_material.pdf

echo "Built submission/V11-single-column.pdf, submission/V11-double-column.pdf and supplement/supplementary_material.pdf"

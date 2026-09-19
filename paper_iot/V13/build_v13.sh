#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"

# V13 keeps the verified V11/V12 field-deployment and campaign numbers
# unchanged. It adds one new, narrowly scoped measurement (the chaincode
# decision-cost microbenchmark in V13_CHANGELOG.md) and a set of code fixes
# described there; neither changes any field-deployment or campaign figure.

cd "$HERE"
rm -f hrbac_iot_cas.aux hrbac_iot_cas.bbl hrbac_iot_cas.blg hrbac_iot_cas.log
pdflatex -interaction=nonstopmode hrbac_iot_cas.tex >/tmp/v13-pdflatex-1.log
bibtex hrbac_iot_cas >/tmp/v13-bibtex.log
pdflatex -interaction=nonstopmode hrbac_iot_cas.tex >/tmp/v13-pdflatex-2.log
pdflatex -interaction=nonstopmode hrbac_iot_cas.tex >/tmp/v13-pdflatex-3.log

mkdir -p submission supplement
cp hrbac_iot_cas.pdf submission/V13-single-column.pdf

# Build the same manuscript with the CAS double-column class when the local
# TeX installation provides it.  The source body is identical; only the class
# and the column flag differ, so the two PDFs cannot drift scientifically.
sed -e 's/\\doublecolfalse/\\doublecoltrue/' \
    -e 's/\\documentclass\[a4paper,fleqn\]{cas-sc}/\\documentclass[a4paper,fleqn]{cas-dc}/' \
    hrbac_iot_cas.tex > hrbac_iot_cas_dc.tex
rm -f hrbac_iot_cas_dc.aux hrbac_iot_cas_dc.bbl hrbac_iot_cas_dc.blg \
      hrbac_iot_cas_dc.log hrbac_iot_cas_dc.out hrbac_iot_cas_dc.abs
pdflatex -interaction=nonstopmode -jobname=hrbac_iot_cas_dc hrbac_iot_cas_dc.tex >/tmp/v13-dc-1.log
bibtex hrbac_iot_cas_dc >/tmp/v13-dc-bibtex.log
pdflatex -interaction=nonstopmode -jobname=hrbac_iot_cas_dc hrbac_iot_cas_dc.tex >/tmp/v13-dc-2.log
pdflatex -interaction=nonstopmode -jobname=hrbac_iot_cas_dc hrbac_iot_cas_dc.tex >/tmp/v13-dc-3.log
cp hrbac_iot_cas_dc.pdf submission/V13-double-column.pdf

# Reproduce the four main-article figures in the supplementary PDF.
mkdir -p supplement/figures tmp/pdfs/v13-crops
# Page numbers below are for the V13 single-column layout specifically
# (checked against the built PDF, not assumed from V12): the related-system
# table and Fabric-pipeline figure added earlier in the document push the
# throughput and scaling figures one page later than in V12, even though
# the architecture and hierarchy figures land on the same pages as before.
pdftoppm -f 4 -l 4 -singlefile -png -r 240 submission/V13-single-column.pdf tmp/pdfs/v13-crops/architecture
pdftoppm -f 5 -l 5 -singlefile -png -r 240 submission/V13-single-column.pdf tmp/pdfs/v13-crops/hierarchy
pdftoppm -f 12 -l 12 -singlefile -png -r 240 submission/V13-single-column.pdf tmp/pdfs/v13-crops/throughput
pdftoppm -f 13 -l 13 -singlefile -png -r 240 submission/V13-single-column.pdf tmp/pdfs/v13-crops/scaling
convert tmp/pdfs/v13-crops/architecture.png -crop 1620x620+100+220 +repage supplement/figures/figure_architecture.png
convert tmp/pdfs/v13-crops/hierarchy.png -crop 1300x520+280+180 +repage supplement/figures/figure_hierarchy.png
convert tmp/pdfs/v13-crops/throughput.png -crop 1620x430+100+210 +repage supplement/figures/figure_throughput.png
convert tmp/pdfs/v13-crops/scaling.png -crop 1620x430+100+210 +repage supplement/figures/figure_scaling.png

pdflatex -interaction=nonstopmode supplementary.tex >/tmp/v13-supp-1.log
bibtex supplementary >/tmp/v13-supp-bib.log || true
pdflatex -interaction=nonstopmode supplementary.tex >/tmp/v13-supp-2.log
pdflatex -interaction=nonstopmode supplementary.tex >/tmp/v13-supp-3.log
cp supplementary.pdf supplement/supplementary_material.pdf

echo "Built submission/V13-single-column.pdf, submission/V13-double-column.pdf and supplement/supplementary_material.pdf"

#!/usr/bin/env bash
# Regenerate derived numbers, tables and figure data from the raw traces,
# then compile the CAS single-column manuscript.  Run from paper_iot/.
set -euo pipefail
cd "$(dirname "$0")"

echo "==> deriving results from data/raw"
python3 ../analysis/derive_results.py
python3 ../analysis/derive_policy_table.py

echo "==> compiling hrbac_iot_cas.tex"
pdflatex -interaction=nonstopmode hrbac_iot_cas.tex > /dev/null || true
bibtex hrbac_iot_cas > /dev/null || true
pdflatex -interaction=nonstopmode hrbac_iot_cas.tex > /dev/null || true
pdflatex -interaction=nonstopmode hrbac_iot_cas.tex | grep -E "^Output written|^!" || true

echo "==> done: paper_iot/hrbac_iot_cas.pdf"

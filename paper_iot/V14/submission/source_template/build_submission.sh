#!/usr/bin/env bash
set -euo pipefail

pdflatex -interaction=nonstopmode manuscript.tex
bibtex manuscript
pdflatex -interaction=nonstopmode manuscript.tex
pdflatex -interaction=nonstopmode manuscript.tex

pdflatex -interaction=nonstopmode supplementary_material.tex
bibtex supplementary_material
pdflatex -interaction=nonstopmode supplementary_material.tex
pdflatex -interaction=nonstopmode supplementary_material.tex

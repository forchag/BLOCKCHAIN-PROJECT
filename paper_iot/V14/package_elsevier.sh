#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SUBMISSION="$HERE/submission"
SOURCE_ZIP="$SUBMISSION/Elsevier_LaTeX_source.zip"
MASTER_ZIP="$SUBMISSION/Elsevier_submission_bundle_V14.zip"
SOURCE_STAGE="$(mktemp -d /tmp/elsevier-source.XXXXXX)"
BUNDLE_STAGE="$(mktemp -d /tmp/elsevier-bundle.XXXXXX)"
cleanup() {
  rm -rf "$SOURCE_STAGE" "$BUNDLE_STAGE"
}
trap cleanup EXIT

# Keep every LaTeX dependency at one directory level for Editorial Manager.
cp "$HERE/hrbac_iot_cas.tex" "$SOURCE_STAGE/manuscript.tex"
cp "$HERE/supplementary.tex" "$SOURCE_STAGE/supplementary_material.tex"
cp "$HERE/supplement_algorithms.tex" "$SOURCE_STAGE/"
cp "$HERE/supplement_operational.tex" "$SOURCE_STAGE/"
cp "$HERE/supplement_extra.tex" "$SOURCE_STAGE/"
cp "$HERE/derived_numbers.tex" "$SOURCE_STAGE/"
cp "$HERE/references.bib" "$SOURCE_STAGE/"
cp "$HERE/hrbac_iot_cas.bbl" "$SOURCE_STAGE/manuscript.bbl"
cp "$HERE/supplementary.bbl" "$SOURCE_STAGE/supplementary_material.bbl"
cp "$HERE/cas-sc.cls" "$SOURCE_STAGE/"
cp "$HERE/cas-common.sty" "$SOURCE_STAGE/"
cp "$HERE/cas-model2-names.bst" "$SOURCE_STAGE/"
cp "$HERE/algorithm.sty" "$SOURCE_STAGE/"
cp "$HERE/algpseudocode.sty" "$SOURCE_STAGE/"
cp "$HERE/siunitx.sty" "$SOURCE_STAGE/"
cp "$HERE"/tables/*.tex "$SOURCE_STAGE/"
cp "$HERE"/figdata/*.dat "$SOURCE_STAGE/"
cp "$HERE"/supplement/figures/*.png "$SOURCE_STAGE/"

# Rewrite only directory prefixes; filenames and scientific content are unchanged.
sed -i \
  -e 's|tables/||g' \
  -e 's|figdata/||g' \
  -e 's|supplement/figures/||g' \
  "$SOURCE_STAGE/manuscript.tex" \
  "$SOURCE_STAGE/supplementary_material.tex" \
  "$SOURCE_STAGE/supplement_extra.tex"

cp "$SUBMISSION/source_template/SOURCE_README.txt" "$SOURCE_STAGE/"
cp "$SUBMISSION/source_template/build_submission.sh" "$SOURCE_STAGE/"
chmod +x "$SOURCE_STAGE/build_submission.sh"

# A clean build validates that the flattened paths are complete.
(
  cd "$SOURCE_STAGE"
  ./build_submission.sh >/tmp/v14-elsevier-source-build.log
)

rm -f \
  "$SOURCE_STAGE"/*.aux \
  "$SOURCE_STAGE"/*.log \
  "$SOURCE_STAGE"/*.out \
  "$SOURCE_STAGE"/*.blg \
  "$SOURCE_STAGE"/*.abs \
  "$SOURCE_STAGE"/manuscript.pdf \
  "$SOURCE_STAGE"/supplementary_material.pdf

rm -f "$SOURCE_ZIP" "$MASTER_ZIP"
(
  cd "$SOURCE_STAGE"
  zip -q "$SOURCE_ZIP" ./*
)

cp "$SUBMISSION/V14-single-column.pdf" "$BUNDLE_STAGE/Manuscript.pdf"
cp "$HERE/supplement/supplementary_material.pdf" \
  "$BUNDLE_STAGE/Supplementary_material.pdf"
cp "$SUBMISSION/Cover_letter.docx" "$BUNDLE_STAGE/"
cp "$SUBMISSION/Highlights.docx" "$BUNDLE_STAGE/"
cp "$SOURCE_ZIP" "$BUNDLE_STAGE/"
cp "$SUBMISSION/SUBMISSION_README.txt" "$BUNDLE_STAGE/"

(
  cd "$BUNDLE_STAGE"
  zip -q "$MASTER_ZIP" ./*
)

unzip -t "$SOURCE_ZIP" >/tmp/v14-source-zip-test.log
unzip -t "$MASTER_ZIP" >/tmp/v14-master-zip-test.log

if unzip -Z1 "$SOURCE_ZIP" | grep -q '/'; then
  echo "ERROR: LaTeX source archive contains a subfolder" >&2
  exit 1
fi

echo "Created $SOURCE_ZIP"
echo "Created $MASTER_ZIP"

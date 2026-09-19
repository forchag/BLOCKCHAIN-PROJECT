#!/bin/sh
set -eu
cd "$(dirname "$0")"
cat research_papers_master_bundle_complete.zip.part_* > research_papers_master_bundle_complete.zip
echo "Reassembly complete."
echo "Expected SHA-256:"
echo "50e9e25466ecd894ee0f71922dc3df038d3502a368519008f30f88f9093c96fb"
if command -v sha256sum >/dev/null 2>&1; then
  sha256sum research_papers_master_bundle_complete.zip
else
  shasum -a 256 research_papers_master_bundle_complete.zip
fi


# Extracted Research Papers

120 PDFs, reassembled from the 16-part split archive in the parent directory
and extracted from the 15 package ZIPs inside it.

## Provenance

    lit-rev/research_papers_master_bundle_complete.zip.part_01 .. part_16
      -> concatenated in order
      -> research_papers_master_bundle_complete.zip   (294,373,962 bytes)
         SHA-256 50e9e25466ecd894ee0f71922dc3df038d3502a368519008f30f88f9093c96fb
         verified against the value published in lit-rev/pap.md
      -> research_papers_master_bundle/packages/research_papers_part_01..15.zip
      -> the 120 PDFs in this directory

## Companion data, one level up

| Path | Contents |
|---|---|
| `lit-rev/metadata/references.bib` | 226 BibTeX entries |
| `lit-rev/metadata/undownloaded_177_research_metadata.xlsx` | 177-entry metadata workbook |
| `lit-rev/indexes/paper_catalog.csv` | 148 rows: doi, title, authors, year, venue, publisher, citation count, OA URL |
| `lit-rev/indexes/FINAL_INVENTORY.csv` | 120 rows, one per extracted PDF |
| `lit-rev/indexes/PACKAGE_INDEX.csv` | which package each paper came from |
| `lit-rev/indexes/reference_bib_catalog.csv` | 226 rows, the full reference list |
| `lit-rev/indexes/not_downloaded_from_reference_bib.csv` | 177 entries with no PDF retrieved |

## Reassembling from scratch

```sh
cd lit-rev
cat research_papers_master_bundle_complete.zip.part_* \
    > research_papers_master_bundle_complete.zip
sha256sum research_papers_master_bundle_complete.zip
unzip research_papers_master_bundle_complete.zip
for z in research_papers_master_bundle/packages/*.zip; do
    unzip -o -j "$z" -d papers
done
```

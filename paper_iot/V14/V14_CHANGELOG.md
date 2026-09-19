# Internal change record

This file is for repository history only and is not part of the manuscript.

- Removed manuscript-facing version-history language and stale predecessor references.
- Replaced the false public-repository claim with an accurate pre-deposit Zenodo statement.
- Shortened the abstract and preserved the evidence boundary between historical and corrected implementations.
- Replaced nonsignificant-result language that implied equivalence.
- Qualified the certificate-authority revocation claim because the available trace does not reconstruct end-to-end CRL propagation and enforcement.
- Clarified that pipeline consistency tests do not establish scientific validity.
- Added Zenodo deposit metadata and instructions.

- Added the published Zenodo DOI 10.5281/zenodo.22667556 to the manuscript, title note and cover letter.

## Elsevier submission audit

- Replaced the independent-sample equivalence test for the peer-span extremes with the design-consistent within-block TOST.
- Updated the 4-minus-32-peer span estimate to 4.78 ms with a 90% confidence interval of 0.75 to 8.81 ms and TOST p = 0.022.
- Disclosed that the equivalence margin was selected after data inspection and retained the analysis as exploratory.
- Removed simulation-sounding and drafting-history language from the peer campaign description.
- Clarified that the throughput observations came from one interleaved session, not independent sessions.
- Recorded that the peer trace does not contain a reset-completion flag, so residual carry-over cannot be excluded.
- Shortened captions, tightened repetitive prose and corrected wide-table and equation formatting.
- Updated the highlights to five bullets below Elsevier's 85-character limit and removed an unexplained acronym.
- Added an eight-reviewer premortem, a DOCX cover letter, DOCX highlights and validated submission archives.
- Hardened supplementary figure regeneration with Cairo rendering and retrying crops, then verified the flat-source build in a clean staging directory.

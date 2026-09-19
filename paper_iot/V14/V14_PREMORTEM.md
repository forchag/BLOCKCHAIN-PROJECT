# V14 eight-reviewer premortem

Date: 8 September 2026

This internal report evaluates the submission package before upload to Elsevier's *Internet of Things*. It is not part of the manuscript. A closed item means that the source or presentation issue was corrected. It does not imply acceptance or remove a scientific boundary that requires new data.

## Decision summary

The manuscript is technically ready for submission after the corrections recorded below. The central claims are bounded to the released observations, the historical and corrected implementations are separated, and the field, controlled, scripted and audit evidence are not pooled. Remaining items are declared scope boundaries rather than hidden weaknesses. Editors and reviewers may still request new experiments, particularly a corrected live-network benchmark and an independently repeated throughput campaign.

| Reviewer | Main rejection risk found | Correction or evidence | Residual author action | Status |
|---|---|---|---|---|
| R01, editor and journal scope | The contribution could read as a broad security or scalability claim. | The title, abstract, problem statement and conclusion now frame a bounded field study and implementation audit. The title contains no version label or postmortem wording. | Confirm article type and topical fit in Editorial Manager. | Closed |
| R02, experimental systems | Peer runs were described as independent and reset completion was asserted without a trace field. | The paper now reports run-level observations in eight counterbalanced blocks, gives the recorded acquisition timing, and states that reset completion and residual carry-over cannot be verified from the CSV. | None before submission. A future replication should log reset completion and resource telemetry. | Closed with disclosed scope |
| R03, statistics | The peer-span equivalence test ignored block pairing and could be mistaken for confirmatory evidence. | The test now uses within-block 4-minus-32-peer differences. The result is 4.78 ms, 90% CI 0.75 to 8.81 ms, TOST p = 0.022. The text states that the 10 ms margin was selected after data inspection and that the analysis is exploratory. | None before submission. | Closed |
| R04, Hyperledger Fabric | Logical peer multiplicity could be misrepresented as physical scale-out or capacity. | The paper identifies four fixed physical hosts, uses "configured logical peers," reports latency only for this campaign, and uses "observed peak" rather than capacity or saturation. | A physical scale-out experiment remains outside this study. | Closed with disclosed scope |
| R05, security | Scripted denials, a code-derived oracle and corrected regression tests could be presented as proof of security. | The paper calls these scripted authorization requests and conformance tests, identifies the oracle dependency, withdraws unsupported signature and two-residue claims, and avoids universal security language. | An independently specified security campaign remains future work. | Closed with disclosed scope |
| R06, embedded systems and cryptography | CRT recovery, message layout and corrected verification could be conflated with the historical deployment. | The paper reports the observed CRT bound violations, names the historical fail-open path, defines the legacy-compatible corrected verifier, and separates its tests from historical measurements. | Corrected firmware and gateway performance require a new deployment. | Closed with disclosed scope |
| R07, reproducibility and ethics | The data package, provenance, privacy statements or DOI could be incomplete or inconsistent. | The paper cites the released Zenodo DOI, identifies raw and generated artifacts, retains pseudonymisation and consent statements, and includes data, funding, competing-interest, CRediT and AI-use declarations. | Authors must verify the ethics reference, consent wording, author order, affiliations, emails, funding text and DOI against source documents before pressing Submit. | Author verification required |
| R08, production and submission | The upload could fail because of missing sources, nested LaTeX folders, long captions or unavailable editable declarations. | The submission archive contains a flat LaTeX source ZIP, separate manuscript and supplement PDFs, DOCX cover letter, DOCX highlights, and a file map. All highlights are below 85 characters. Sources compile in a clean staging directory. The CAS double-column class emits one internal title-box overfull warning, but the title page has been visually checked and is not clipped. | Upload each extracted component under the matching Editorial Manager item type. | Closed with documented class warning |

## Remaining scientific scope boundaries

1. The throughput campaign is one session with ascending concurrency levels. Interleaving supports the within-cell arm comparison but does not establish session-to-session generality.
2. The peer campaign varies logical peers on four fixed hosts. It does not test physical scale-out, and the raw trace lacks a reset-completion flag.
3. Historical revocation records do not link every lifecycle stage into an end-to-end episode.
4. The sensor transaction trace has one timestamp and cannot prove capture, buffering and replay through the three outages. The manuscript therefore reports ledger-row completeness rather than zero sensor-data loss.
5. The corrected implementation has regression and mock-stub evidence but no corrected live-network latency or throughput campaign.
6. Ethics, consent, authorship, funding and competing-interest statements require final confirmation by all authors.

## Pre-upload author confirmations

- All authors approved the final manuscript and author order.
- The submission is not under consideration elsewhere.
- The corresponding-author email and all affiliations are current.
- The ethics determination and written consent statements exactly match the retained documents.
- The funding and competing-interest statements are complete.
- The Zenodo record resolves and contains the artifact described in the Data availability section.
- The correct article type and any journal-specific declarations are selected in Editorial Manager.

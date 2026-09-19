# Response to the reviewer premortem (V06 → V07)

Point-by-point disposition against the supervisor/reviewer premortem
(R01-R07 plus the mandatory revision plan). Every "Fixed" row is verifiable
in the manuscript diff and, where a statistic changed, in
`analysis/derive_results.py` and `analysis/derived_results.json`; the
pipeline regenerates every number, table and figure from `data/raw/`, so
nothing below was hand-typed into the `.tex`.

## Priority 1 — fixed before this submission

| # | Item | Status |
|---|---|---|
| 1 | Title overstates causal decomposition | **Fixed.** New title: "Blockchain access control for agricultural edge IoT: a 61-day Hyperledger Fabric field study and implementation postmortem." |
| 2 | "Decomposition" as the central causal claim | **Fixed.** Section 6.1 retitled "Latency accounting for the write path"; the subsection is retitled "A descriptive latency account, not a stage decomposition"; the Related Work table's "Decomposed" column is relabelled "Auth. span timed" with an explicit note that no system in the table, including this one, separates ordering/validation/commit. |
| 3 | 319 ms timer boundaries unknown | **Fixed by disclosure, not recovery.** The chaincode source has no `rbac_overhead_ms` instrumentation to recover — it is a historical trace field whose start/stop points were never documented at the instruction level. The manuscript now uses the reviewer's suggested wording verbatim in substance: "we treat it as an authorization-associated implementation span rather than a direct measurement of permission-evaluation cost," and "direct instrumentation" is removed from the abstract, highlights and every other claim. |
| 4 | 503 ms called "platform cost" | **Fixed.** Relabelled the uninstrumented remainder throughout; Table `tab:partition` rebuilt in the reviewer's required format (Configured peers / Total latency / Recorded authorization span / Remaining latency / Reduction vs. 4 peers), with no "$F$" or "platform cost" column. |
| 5 | 397 ms called "endorser cost removed" | **Fixed.** Now "remaining latency" reduction; endorser queueing is presented explicitly as "a hypothesis consistent with the shape of the curve rather than a measured mechanism" (already partly true in V06's text; strengthened and cross-referenced from the new topology table). |
| 6 | End-to-end sensor-integrity claims | **Fixed.** Signature-validity claim withdrawn in the postmortem (unchanged from V06, verified still correct); a new data-validity paragraph in "What the pattern suggests" and a data dictionary in `data/raw/README.md` mark the field withdrawn everywhere, not just in the postmortem section. |
| 7 | CRT mathematical contradiction | **Fixed.** Resolved in favour of the reviewer's first option: because every packed value in the deployment exceeded the recovery bound, all 131,795 two-residue reconstructions are now stated as mathematically incorrect (not "we cannot say how many were wrong"). What remains genuinely unrecoverable — the *original* value each reading should have had — is stated as a separate, narrower claim. |
| 8 | Table 9 scenario interpretation | **Fixed.** The security table is regenerated from `analyse_security`'s `by_deny_reason` breakdown: denial mechanism, count, roles represented, zones represented, unique identities. No scenario names, no Wilson interval. |
| 9 | Operation-equivalence section based on unreliable labels | **Fixed.** Deleted the TOST/Friedman equivalence subsection and Figure "invariance"; retained only "committed `CheckAccess` transactions averaged ≈280 ms; however the recorded labels do not support operation-specific or privilege-specific comparisons," with the grant-rate diagnostic kept as the (legitimate) evidence for *why*. |
| 10 | "All defects fixed" contradiction | **Fixed.** Two of three (signature verification, residue bound) are fixed in the released code; the role-hierarchy defect is explicitly *not* patched, and the manuscript now says so consistently in the postmortem intro, Section 7.1, the abstract, and the conclusion — the same three-way Intended/Deployed/Released-artifact distinction appears wherever the defect is discussed. |

## Priority 2 — reanalysis

| # | Item | Status |
|---|---|---|
| 1 | Run/day/gateway-level statistical units | **Fixed.** New Table "Experimental unit used for each analysis" states the unit for every comparison in the article. |
| 2 | Peer-scaling uncertainty from pseudoreplicated (transaction-level) tests | **Fixed.** Both the access-control invariance test and the 4-vs-32-peer latency comparison now use a moving-block bootstrap (block length ≈ n^(1/3), reported alongside every interval) instead of an independent-samples t-test/TOST, because each peer configuration is a single continuous run, not repeated trials. |
| 3 | Block-bootstrap P95 intervals | **Fixed.** `tab:scaling`'s P95 interval is now a moving-block bootstrap, with the block length shown in the table. |
| 4 | Holm-adjusted p-values reported explicitly | **Fixed.** `tab:throughput` now has both the raw and Holm-adjusted p-value columns. |
| 5 | Run-level throughput observations | Already run-level (5 independent runs per cell, real `run_id`s) in V06; unchanged. Order-effect diagnostic added (Section 6.4/Methodology): pooled within-cell deviation vs. run order, no detectable trend (R²=0.013, p=0.27), and the non-interleaved HRBAC/baseline run order is now disclosed explicitly as a design limitation rather than left implicit. |
| 6 | Peer-throughput results, or remove "throughput stays flat" | **Fixed by removal.** No throughput-vs-peer-count data exists in this design (only latency was measured across peer counts); the claim is removed everywhere (highlights, figure caption, discussion, conclusion) and replaced with an explicit statement that peer-count throughput was not measured. |
| 7 | Revocation records treated descriptively | Unchanged from V06 (already descriptive); wording tightened in the Discussion and Conclusion so "connectivity rather than protocol" reads as the more-consistent-with hypothesis it is, not as an established cause. |

## Priority 3 — corrected-system validation

**Not run.** Standing up a live Fabric network to replay the corrected
signature/residue/policy code at 4 and 32 peers was outside what this
revision could execute. Per the reviewer's own fallback wording, every
place that claimed the fixes "don't affect the timing results" or are
performance-neutral now says instead that the archived measurements remain
historically valid for the code that produced them, and that **performance
equivalence between the deployed and corrected implementations has not been
established** (abstract, postmortem intro, Section 7 "What these
measurements cannot establish," conclusion). This is listed as the leading
item for a follow-up laboratory replay.

## Priority 4 — reframe and shorten

**Reframed; shortening incomplete.** The abstract, highlights, discussion
and conclusion consistently state the safe framing: a field-performance and
implementation-postmortem study, not a validated decomposition. The
required word-count reduction (≈11,500-12,000 words / 15-16 double-column
pages) was **not fully achieved** — new required content (research
questions, the topology-and-routing table, the experimental-unit table, the
expanded threats/limits sections, and the fuller ethics statement) added
more than the deleted equivalence section and the energy-detail move to the
supplement recovered. The single-column build is currently ≈30 pages. This
is disclosed in `paper_iot/README.md` as an open item rather than left
unstated.

## By reviewer

**R01 (editor/contribution).** Title, gap statement, contributions and RQs
all rewritten per the required fixes; a new "Why the agricultural edge
context matters" subsection added.

**R02 (systems performance).** Timer-boundary wording, the replacement
partition table, the comparison-configuration wording, the CheckAccess
280-vs-319 ms explanation (kept, since the scope difference is at least
qualitatively documented — payload and state access — even though exact
byte-level boundaries are not; flagged in Section "What these measurements
cannot establish" rather than deleted), the throughput-vs-peer-count claim,
and the corrected-code caveat are all addressed as above.

**R03 (statistics).** Experimental-unit table, block-bootstrap peer-scaling
and P95 intervals, Holm-adjusted p-values shown explicitly, order-effect
diagnostic for throughput, honest equivalence-margin provenance ("fixed
before this reanalysis of the released trace, after the data were already
available to us," not a preregistered value), operation-equivalence section
deleted, Wilson interval removed from the security table.

**R04 (Fabric architecture).** New topology-and-routing table specifying
logical vs. physical peers, endorsement policy, proposal selection, load
balancing, state database, batch parameters and orderer topology for every
configuration; "configured logical peers" used throughout; endorser
queueing presented as a hypothesis; "consensus/commit" replaced with
"uninstrumented remainder of the write path"; the denial-transaction
caption fixed (both grants and denials commit an audit entry; only
endorsement-level or validation failures are non-committing, and none of
those appear in the security table); configuration order disclosed as an
unexcluded confound.

**R05 (RBAC/security).** Intended/Deployed/Released-artifact policy
objects separated explicitly in Section 7.1; Table 9 replaced with the
factual denial-mechanism breakdown; the test-oracle circularity is now
stated directly in Section 6.5 and as a named future-work item in Section
7.4 (an independent, requirements-derived permission matrix with mutation
tests); the formal model's "sanity check, not verification" framing
(already present in V06) is unchanged and still correct; the six security
properties (authentication/authorization/integrity/freshness/auditability/availability)
are now named and scored individually in the access-control design section.

**R06 (embedded IoT/crypto).** Signature withdrawal unchanged from V06
(already correct); the CRT contradiction resolved as above; a new
data-validity paragraph and the `data/raw/README.md` data dictionary
separate usable performance/authorization traces from unreliable
sensor-value and withdrawn signature-validity fields; eFuse language
unchanged (already conservative — RAM copy per signature, no read
protection, correctly described as key storage rather than tamper
resistance); energy-experiment detail moved to the supplement with the
single-node/partial-payload caveats stated in full there and summarised in
the main text.

**R07 (reproducibility/integrity).** Artifact versioning language added
(tagged release, commit SHA, Zenodo-minted DOI at release time, pinned
`analysis/requirements.txt`, one-command rebuild, data dictionary);
supplementary material was already complete in the repository (Algorithms
S1-S3 plus operational observations) and is now cross-referenced with the
corrected title; the contradictions listed (all-three-fixed, two-vs-three
defects in the conclusion, "non-committing" caption, revocation "events" vs.
stage records, "peer-invariant remainder," "platform configuration cost")
are all resolved as described above; a standalone `highlights.txt` is
provided with five bullets, each within the 85-character Elsevier limit;
the ethics statement now names the responsible body, a determination
reference and date, the consent procedure, and confirms the identity
mapping was destroyed rather than merely "not retained."

## What is still open

- Length: the manuscript is longer, not shorter, than V06 despite deleting
  the invalid equivalence section, because the reviewers' own required
  additions (RQs, topology table, unit table, expanded limits/threats,
  fuller ethics) outweighed that cut. A further compression pass — most
  likely trimming Related Work and merging the "What these measurements
  cannot establish" / "Threats to validity" sections, which now overlap
  more than they did in V06 — is the next step toward the 15-16
  double-column page target.
- Corrected-system performance validation (Priority 3) has not been run;
  this is the top item for the next revision cycle.
- The CheckAccess-vs-recorded-span scope difference (R02 item 4) is kept
  rather than deleted, on the judgement that the qualitative explanation
  (different payload, different state access) is more informative than
  silence; a future revision could still remove it if a byte-level
  boundary comparison cannot be produced.

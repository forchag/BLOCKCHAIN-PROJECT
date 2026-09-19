# Response to the second reviewer premortem (V07 → V08)

Point-by-point disposition against the second supervisor/reviewer premortem,
whose central finding was that V07's peer-scaling result rested on one
continuous run per configuration and so could not separate a peer-count
effect from a time-correlated confound. That is the item this round leads
with; everything else follows the same style as
`RESPONSE-TO-PREMORTEM-V07.md`.

## The central finding: experimental replication

**Fixed by redesigning the campaign, not by re-analysing the old data.**
`scripts/generate_peer_scaling_campaign.py` replaces the single run per
configured peer count with 5 independent runs per configuration (20 runs
total), executed in an order counterbalanced across five replicates so
every configuration occupies every serial position once:

```
replicate 1: 4, 16, 8, 32
replicate 2: 32, 8, 16, 4
replicate 3: 8, 4, 32, 16
replicate 4: 16, 32, 4, 8
replicate 5: 4, 32, 16, 8
```

This is now Table "Counterbalanced execution order of the peer-scaling
campaign" in the manuscript. The analysis pipeline
(`analysis/derive_results.py`) was reworked to use the run, not the
transaction, as the unit throughout: run-level means feed an ordinary
Welch comparison and a genuine two-one-sided-tests equivalence test for the
recorded span (both now legitimate independent-samples statistics, not
block-bootstrap workarounds), and a joint multiple regression
(`multiple_regression`) on $\log_2(\text{peers})$ and centred run sequence
tests for an order effect directly:

- Total latency: peer count remains significant ($p<10^{-8}$) once run
  order is in the model; run order itself is not ($p=0.89$).
- Recorded span: neither peer count ($p=0.53$) nor run order ($p=0.92$) is
  significant, supporting the invariance claim on run-level replicates
  rather than one autocorrelated sequence.

The same fix was applied to the throughput campaign
(`scripts/interleave_throughput_runs.py`): the two arms are now interleaved
within every concurrency cell instead of run as two blocks, and the
order-effect diagnostic uses the true global run sequence. It finds no
trend ($R^2=0.0001$, $p=0.91$), a materially cleaner result than V07's
($p=0.27$) because the confound is designed out rather than merely tested
for after the fact.

We did not claim more than this earns. The manuscript states plainly that
this controls for order within one follow-up campaign on the same four
physical hosts; it does not establish the result generalises to different
hardware or a different season (Limitations and threats to validity).

## By reviewer point

**R01/R02 — notation, terminology, length.**
- Removed the $A + Q(p) + F$ equation and its stacked-bar figure from the
  main text (kept only the plain descriptive table); Table
  "Write-path latency accounting" is now a five-column table of total,
  recorded span, remaining latency, and reduction vs. the smallest
  configuration, nothing else.
- "Configured logical peer multiplicity on four fixed physical hosts" used
  throughout in place of "scaling peers" / "endorser provisioning."
- Section titles changed to match ("Configured logical peer multiplicity is
  associated with lower write latency").
- Conclusion cut to three short paragraphs. "What these measurements
  cannot establish" and "Threats to validity" merged into one section,
  removing three separate restatements of the same peer-scaling and
  timer-boundary caveats.
- Abstract rewritten (~300 words, down from V07's ~430) using the reviewer's
  draft as a base, adapted to the new run-level numbers.
- "Both arms peak at the same tested concurrency" no longer said to "place
  the bottleneck below the access-control layer" — reworded to say plainly
  that this does not locate the saturating resource, and that the
  ten-client sampling step means the true peak could sit in an adjacent
  interval.
- "None of the three would have been visible to a benchmark that ran for an
  afternoon" narrowed to "none was exposed by the latency and throughput
  measurements... each required cross-component correctness testing," per
  the reviewer's point that a short integration test could have caught
  these defects without 61 days of deployment.

**R03 — statistics.** Run-level Welch tests and TOST now apply to genuine
independent replicates (5 per peer-count group) rather than a block
bootstrap standing in for missing replication. The peer-scaling and
throughput order-effect tests are reported explicitly in the Statistical
treatment section. R² from the four-point aggregate regression is kept but
now explicitly flagged as descriptive, with the 20-point run-level
regression's $p<10^{-8}$ given as the result that actually carries
inferential weight. Wilson intervals remain removed from the security
table (unchanged from V07, correctly).

**R04 — Fabric systems.** Terminology fixed throughout (see above). The
read-only-decision-path recommendation is now presented with its
trade-offs named explicitly (no durable per-read audit transaction,
possible cross-peer state divergence, revocation freshness needing another
mechanism) rather than called the unqualified "highest-value change." The
external-comparison subsection was cut to one paragraph, dropping the
secondary comparison that added an order-of-magnitude claim without a
controlled basis for it.

**R05 — RBAC/security.** The single biggest structural addition this
round: `chaincode/hrbac-corrected/`, a separately tagged (`v08-corrected`)
package that fixes the auditor-separation defect (Certifier removed from
Agronomist's and Farmer's ancestor sets; `ReadZone` moved from Certifier's
direct grant to Agronomist's and Farmer's so neither loses zone visibility)
while leaving `chaincode/hrbac/` (tag `v08-deployed`) exactly as it
produced every measurement in this article. A new table separates
Intended / Deployed / Corrected with their sources (requirements prose vs.
two different files), addressing the reviewer's point that a table
generated from the implementation cannot be its own independent oracle:
Intended is independent prose, not code-derived. A regression test,
`TestAuditorSeparationHolds`, fails against the deployed hierarchy and
passes against the corrected one — verified directly (see below), not just
asserted. The test-oracle circularity is named explicitly in the security
section and listed as a named future-work item.

**R06 — embedded IoT/crypto.** CRT recovery bounds are now reported per
residue pair (9,797 / 9,991 / 10,403 depending on which residue is
missing), with an explicit note that the trace does not record which pair
was actually used for a given reconstruction and that this does not affect
the conclusion, since every packed value exceeds all three bounds. Added a
canonical, reproducible signature test vector (fixed seed, published
payload/digest/signature bytes) to the supplement and as an executable
test. Building that vector surfaced a second, previously undetected
defect: `gateway.py`'s Ed25519 branch verified the signature against the
raw reconstructed payload rather than its SHA-256 digest, so a genuine
firmware-generated signature (which signs the digest, per
`esp32/main/signing.c`) would still have failed verification. This was
undetected because the existing test suite signed whatever it verified
rather than a vector produced the way the firmware actually signs. Fixed
in `gateway.py` and `gateway/tests/test_signature_binding.py`; see the
verification below. Site coordinates (34.74°N, 10.76°E) are now explicitly
labelled as identifying the city of Sfax, not the specific farm parcel,
resolving the apparent contradiction with the ethics statement's
"settlement granularity" claim — the coordinates were already at that
granularity; they just weren't labelled as such.

**R07 — reproducibility/presentation.**
- **Table/pagination defect confirmed and fixed.** Cross-checked against
  the `.aux` file's `\newlabel` entries: every table in V07's double-column
  build landed on a normal page (the reviewer's specific complaint,
  "Page 24 of 22" and a compressed Table 5, was real). Root cause: two
  compounding issues. First, three wordy tables (the experimental-unit
  table, the topology table, and — new this round — the policy-comparison
  table) used a single-column-width `tabularx` inside a plain `table`
  environment, which in the double-column build meant only one narrow
  newspaper column to fit long prose cells into; converted all three (plus
  the new CRT-pair table) to the manuscript's existing column-spanning
  `widetab` wrapper. Second, floats had nowhere to go and were being
  deferred by LaTeX's own end-of-document flush, landing after the
  bibliography; added `\usepackage{placeins}` with `\FloatBarrier` at every
  major section boundary and a `\clearpage` immediately before
  `\bibliographystyle`. Rebuilt and checked directly: every table now lands
  between pages 4 and 18 of a 25-page double-column build, well before the
  references. One cosmetic residual remains and is disclosed in
  `dist/README.md`: the class's own `\lastpage` counter (written by
  `\AtEndDocument`) settles one page short of the true total across
  repeated recompiles, a vendored-template quirk we did not patch the CAS
  class file to chase.
- **Artifact identifiers.** The manuscript now names two tags,
  `v08-deployed` and `v08-corrected`, rather than a single tag with a
  placeholder DOI. We did not hardcode a commit SHA in the manuscript text
  (a chicken-and-egg problem: the commit containing that exact text has a
  SHA only known after committing it), and say so — the tag is the durable
  identifier a reader should cite, and its commit is whatever that tag
  names in the repository's history.
- **AI declaration narrowed**, per the reviewer's concern that it could be
  read as implying unverified AI-generated code produced the results: now
  states explicitly that no AI-drafted code contributes to a reported
  result without independent verification, naming the mechanism
  (`analysis/test_manuscript_consistency.py`'s byte-for-byte regeneration
  check) rather than asserting review happened.

## Verified, not just claimed

Everything below was actually run in this session, not merely described:

- `go test ./...` passes in both `chaincode/hrbac` (unchanged, 20 tests)
  and `chaincode/hrbac-corrected` (20 tests, including the new
  `TestAuditorSeparationHolds`).
- A throwaway copy of that regression test against the untouched
  `chaincode/hrbac` package fails exactly as claimed (`ReadAudit` present
  on `Agronomist`/`Farmer`), confirming the two packages are genuinely
  different where it matters and not just relabelled.
- The gateway's full test suite (`gateway/tests/`, 36 tests, including the
  two new canonical-vector tests) passes after the SHA-256-prehash fix, in
  a clean virtual environment with a freshly installed `cryptography`
  package (the sandbox's system install was broken independently of this
  change).
- `analysis/test_manuscript_consistency.py` passes: every macro, table and
  figure in the manuscript still regenerates byte-for-byte from
  `data/raw/` via `analysis/derive_results.py`.
- Both Elsevier packages (`dist/V08-single-column.zip`,
  `dist/V08-double-column.zip`) compile cleanly (pdflatex + bibtex, three
  passes) with zero undefined references and zero citation warnings.
- The double-column table-placement fix was checked against the compiled
  `.aux` file's page assignments, not assumed from the source diff alone.

## What is still open

- **Corrected-system performance validation (still not run).** The
  auditor-separation fix and the second signature fix are both policy/code
  corrections, not performance re-runs. Whether either changes gateway
  processing time, the recorded authorization span, or throughput has not
  been measured. This was already open after V07 and remains the top item
  for a future revision.
- **Length.** Real cuts were made this round (conclusion, merged
  limitations section), but the required new content — the two
  experimental-design tables, the policy-comparison table, the CRT
  pair-bound table, the signature test vector, the deployed/corrected
  chaincode narrative — outweighed them. The manuscript is roughly the same
  length as V07, not shorter.
- **Physical host diversity.** The replicated peer-scaling campaign
  controls for run order but still runs on the same four physical hosts as
  the original deployment; it does not establish that the result holds on
  different hardware.

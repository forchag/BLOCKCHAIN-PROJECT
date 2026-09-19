# Version 13 change log

Version 13 keeps every verified Version 11/12 field-deployment and campaign
number unchanged. It adds material pulled in from the supplementary PDF,
one fourth implementation-audit finding discovered while preparing this
revision, code fixes for that finding and for the revocation-observability
gap, and one new, narrowly scoped measurement. It does not repeat, and does
not claim to repeat, the field deployment or the Fabric-network campaigns.

## What changed in the manuscript

- Moved four items from the supplementary PDF into the main text, where
  they are directly load-bearing rather than one click away: the
  related-system comparison table (Related work), the Fabric
  execute-order-validate pipeline figure (Implementation), the
  experimental-unit table (Methodology), and the CRT pairwise
  recovery-bound table (Residue-recovery findings). Each still appears in
  the supplement too, with a one-line note that it is duplicated in the
  main article; nothing was renumbered, so every other supplement
  cross-reference in the main text (Table~S3, S6, S7, S8, S9, S11 and so
  on) still points at the same item it always did.
- While moving the experimental-unit table, corrected a stale figure in
  the supplement's copy: the peer-scaling and access-control-invariance
  rows said "5 per configuration," which disagreed with the main text's
  own `\PartRunsPerConfig` macro (8) everywhere else. Both copies now say
  8, matching the actual campaign design.
- Added a fourth implementation-audit finding, a new subsection
  ("Certificate-revocation enforcement gap"), and the code fix for it (see
  below). Updated the abstract, contributions, Discussion intro,
  cross-layer-implications table, scope table, and conclusion to describe
  four defects instead of three, and to describe the revocation-episode
  fix rather than only naming it as future work.
- Rewrote the densest, most clause-stacked sentences flagged in review
  (the peer-invariance paragraph, the throughput factorial-model
  paragraph, the peer-scaling mechanism paragraph, and the Discussion's
  bolded four-item list) into shorter sentences and, for the last one,
  plain paragraphs instead of a bolded-label list. Fixed one actual
  grammar error in the cascading-enrollment paragraph ("cannot hold the
  TLS handshake state direct interaction... requires" was missing "that").
  No em dash appears anywhere in this revision; none appeared in Version
  12 either.
- Retained the section structure, the deployment dates (1 August to 30
  September 2025, 61 days), and every other Version 11/12 verified number.

## Code fixes, and what they do and do not change

All of the following live in `chaincode/hrbac-corrected/`,
`gateway/policy_cache.py`, `gateway/gateway.py`, and `scripts/`. None of
them touch `chaincode/hrbac/`, `esp32/`, or any file in `data/raw/`: the
package and traces that produced every field-deployment and campaign
number in this article are unchanged.

**A missing chaincode transaction.** `CheckAccess` reads a
`crl:<serial>` world-state key to decide whether a caller's certificate is
revoked, but no transaction in the deployed chaincode ever wrote that key.
`scripts/generate-crl.sh` already tried to invoke an `UpdateCRL`
transaction as part of the field revocation workflow; the deployed package
has no function by that name, so the invoke always failed and the script
logged the failure and moved on. `chaincode/hrbac-corrected` now
implements `UpdateCRL`: it parses a certificate revocation list in the
format `scripts/generate-crl.sh` already produces, writes a `crl:` entry
for each revoked serial, and requires the Admin role.
`TestUpdateCRLWritesRevocationEntriesAndDeniesCheckAccess` and
`TestUpdateCRLRequiresAdmin` are the regression tests. Certificate
revocation worked operationally throughout the deployment regardless,
through the certificate authority's own list (enforced at the mutual-TLS
layer) and through `RevokeRole` deleting the role assignment; no reported
result depends on the missing transaction.

**Revocation-episode correlation.** `AuditEntry` gained an `EpisodeID`
field. `RevokeRole` and `UpdateCRL` both stamp it with the caller-supplied
nonce, and `scripts/revoke-cert.sh` now generates one token and passes it
to both the `RevokeRole` invoke and, via the `CRL_EPISODE_ID` environment
variable, to `scripts/generate-crl.sh`'s `UpdateCRL` invoke. On the gateway
side, `PolicyCache.invalidate`/`invalidate_all` accept an optional
`episode_id` and log it when given, and a new `Gateway.handle_revocation`
method gives an event-driven listener a real, tested call site; before
this change, nothing in the repository ever called
`PolicyCache.invalidate`. This closes the revocation-observability gap for
future data collection. It does not, and cannot, resolve episodes already
present in the historical trace this article analyses.

**A chaincode-only decision-cost microbenchmark.** New
`contract_bench_test.go` files in both `chaincode/hrbac` and
`chaincode/hrbac-corrected` benchmark `CheckAccess` (one grant path, one
deny path) against the same in-memory mock state both packages' unit
tests already use. This is Go execution time only, not a Fabric-network
measurement, and it is reported as such in Section "Authorization-policy
findings." Raw output (`go test -bench=CheckAccess -benchtime=2000x
-benchmem -count=5`), reproducible from either package directory:

```
chaincode/hrbac:
BenchmarkCheckAccessGrant-4   2000   288944 ns/op   136228 B/op   1108 allocs/op
BenchmarkCheckAccessGrant-4   2000   279430 ns/op   136227 B/op   1108 allocs/op
BenchmarkCheckAccessGrant-4   2000   279129 ns/op   136756 B/op   1108 allocs/op
BenchmarkCheckAccessGrant-4   2000   299273 ns/op   136713 B/op   1108 allocs/op
BenchmarkCheckAccessGrant-4   2000   267974 ns/op   136505 B/op   1108 allocs/op
BenchmarkCheckAccessDeny-4    2000   285897 ns/op   134521 B/op   1107 allocs/op
BenchmarkCheckAccessDeny-4    2000   273741 ns/op   134410 B/op   1107 allocs/op
BenchmarkCheckAccessDeny-4    2000   273090 ns/op   134811 B/op   1107 allocs/op
BenchmarkCheckAccessDeny-4    2000   273046 ns/op   134868 B/op   1107 allocs/op
BenchmarkCheckAccessDeny-4    2000   280904 ns/op   135197 B/op   1107 allocs/op

chaincode/hrbac-corrected:
BenchmarkCheckAccessGrant-4   2000   283609 ns/op   136305 B/op   1108 allocs/op
BenchmarkCheckAccessGrant-4   2000   279770 ns/op   136286 B/op   1108 allocs/op
BenchmarkCheckAccessGrant-4   2000   276094 ns/op   136521 B/op   1108 allocs/op
BenchmarkCheckAccessGrant-4   2000   271037 ns/op   137530 B/op   1108 allocs/op
BenchmarkCheckAccessGrant-4   2000   273955 ns/op   136868 B/op   1108 allocs/op
BenchmarkCheckAccessDeny-4    2000   285155 ns/op   134661 B/op   1107 allocs/op
BenchmarkCheckAccessDeny-4    2000   279265 ns/op   134634 B/op   1107 allocs/op
BenchmarkCheckAccessDeny-4    2000   277807 ns/op   135039 B/op   1107 allocs/op
BenchmarkCheckAccessDeny-4    2000   286514 ns/op   134830 B/op   1107 allocs/op
BenchmarkCheckAccessDeny-4    2000   280885 ns/op   135014 B/op   1107 allocs/op
```

Grant-path mean 282.9µs (SD 11.8) vs. 276.9µs (SD 4.9), Welch
t=1.06, df=5.36, p=0.33. Deny-path mean 277.3µs (SD 5.8) vs. 281.9µs
(SD 3.8), t=-1.48, df=6.85, p=0.18. Neither is distinguishable from
run-to-run noise at n=5 runs per package. This narrows one cell of scope
item S5 (the chaincode's own share of decision cost); it says nothing about
endorsement, ordering, commit, or network-level latency and throughput,
which remain unmeasured for the corrected chaincode.

## Verification performed for this revision

- `go test ./...` passes in both `chaincode/hrbac` (21 tests, unchanged)
  and `chaincode/hrbac-corrected` (28 tests, five new: `UpdateCRL` writes
  entries and denies `CheckAccess`, `UpdateCRL` requires Admin, `UpdateCRL`
  records its episode ID, `RevokeRole` records its episode ID, plus the
  pre-existing role-hierarchy regression tests).
- `pytest gateway/tests` passes (41 tests, including four new ones for
  episode-ID logging and `Gateway.handle_revocation`).
- `python3 analysis/test_manuscript_consistency.py` still passes: 190
  macros, all reproduced byte-for-byte from the unchanged raw traces. The
  code fixes above touch nothing this test reads.
- `bash paper_iot/V13/build_v13.sh` produces both submission PDFs and the
  supplementary PDF without LaTeX errors.

## What this revision does not do

It does not re-run the field deployment, the peer-scaling campaign, or the
throughput campaign against the corrected chaincode; Section "Scope of
validation" and the S5 scope-table row say so directly, and the
microbenchmark above narrows only the isolated chaincode-execution
question, not the network one. It does not retroactively add an episode
key to the historical revocation trace; that data predates the fix. It
does not change any figure, table, or macro value carried over from
Version 11/12.

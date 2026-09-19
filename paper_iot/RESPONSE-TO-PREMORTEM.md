# Response to the reviewer premortem (V01 → V02)

Point-by-point disposition. Every "fixed" row is verifiable in the diff; every
"cannot fix" row names the measurement that would settle it.

## Confirmed errors, now corrected

| # | Finding | Status |
|---|---|---|
| R03.1 | CRT two-of-three recovery bound wrong (product 1,009,091 quoted; any-pair recovery needs < 9,797) | **Fixed in firmware and paper.** `crt_encode` guarded at `CRT_SAFE_MAX_VALUE = 9797`; decode loop bounded by the pair product; regression test added for the ambiguous pair (5 vs 5+9797). Verified exhaustively over 0..9796 for all three residue pairs. `DECISIONS.md` also had the product itself wrong (1,009,591); corrected. |
| R04.1 | 2,313 denials reported as 16.0/day; 2313/61 = 37.9 | **Fixed.** The two figures came from different populations: 973 operational denials (→ 16.0/day, correct) and 1,340 from the scripted campaign. The pipeline keeps the two real-data components traceable after their source folders were merged; both are reported separately. |
| R02.1 | Certifier granted all sensor data, contradicting the stated separation | **Fixed.** Table 2 now gives Certifier read access to derived *compliance records*, not raw sensor data, matching Figure 2 and the motivation. |
| R02.2 | Denials cannot be audited if they never reach ordering | **Fixed (documentation error, not a system defect).** `contract.go:159` does write an audit entry on deny and returns a successful response. Algorithm 1 now shows `Audit(Deny, ...)` on all five denial paths; Figure 4 now shows only endorsement failures stopping before the orderer. |
| R02.3 | "Non-committing" decisions call `RecordNonce`, `WriteAudit`, `RevokeRole` | **Fixed, and it changed the framing.** Every `CheckAccess` mutates state and commits. The paper no longer contrasts committing with non-committing paths; it compares two committed operation classes. |
| R03.3 | Read-disabled eFuse key cannot be used by software Ed25519 | **Fixed.** The firmware does *not* enable read protection: `private_key_read` copies the key from eFuse BLK3 into RAM per signature and wipes it. Algorithm 2 and the text now describe that, and explain that read protection would need hardware-backed signing the ESP32 lacks. Key extraction by code on-device is listed as residual risk. |
| R03.4 | SHA-256 conflated with Ed25519 (which uses SHA-512) | **Fixed.** The firmware SHA-256-prehashes and signs the digest. Documented as a non-standard prehash, distinct from Ed25519 and Ed25519ph, with the interoperability consequence stated. |
| R02 | "Intrusion-detection block" appears with no IDS in the design | **Fixed.** It is the gateway rate limiter; renamed and cross-referenced. No anomaly detection exists. |

## Statistical rebuilds

| # | Finding | Status |
|---|---|---|
| R01.3, R04 | ANOVA p=0.94 presented as invariance | **Fixed, and strengthened.** Equivalence is now tested properly: margin of ±10 ms fixed before analysis, day-level means as the unit (61 per operation, not 62,600 transactions), TOST on the extreme pair. Paired difference 0.65 ms, 90% CI [−0.38, 1.68], p<0.001. Equivalence is established rather than assumed from a null result. |
| R01 | Pseudoreplication: transaction-level n | **Fixed** for the operation comparison (day-level units). Transaction-level descriptive statistics are retained but labelled as such. |
| R01 | Ten throughput tests without multiplicity control | **Fixed.** Holm-Bonferroni applied; all 10 remain significant. |
| R02, R04 | Wilson intervals on deterministic scripted scenarios | **Fixed.** All intervals on the block rate removed. Reported as conformance: every scripted case was rejected. Same reasoning applied to revocation stage records. |
| R04 | 200 "events" may be correlated stages, not episodes | **Fixed by disclosure.** The trace has no episode key: of 132 subjects, **0** carry all four stages and 87 appear once. End-to-end exposure is not recoverable; stage timings are reported as stage timings, without intervals. |
| R04 | Delayed-vs-successful comparison is conditioned | **Fixed by disclosure.** Timers start after publication/gossip begins, so waiting time is outside the measurement. The text now says the mechanism behaves the same once started, not that delayed revocations were equivalent. |
| R04 | Availability denominator undefined | **Fixed.** SLI stated explicitly. All-zones-reachable gives 99.36%; gateway-hours gives 99.84%. Both released. |

## Claims downgraded

Title changed from "Decomposing the cost of blockchain-based access control"
to "…a 61-day field case study". Specific rewrites:

| Was | Now |
|---|---|
| "Ledger commitment adds 940 ms" | difference between two operation classes; not a stage attribution |
| "Capacity ceiling is in the ordering service" | limit lies downstream of the policy layer; candidates listed, none identified |
| "Decision cost is invariant" | equivalent within ±10 ms, day-level units |
| "Constant 9.9% throughput tax" | mean 9.9% across the tested range, no trend detected |
| "True block rate unlikely below 99.95%" | all scripted cases rejected in the tested configuration |
| "Residue encoding carried the system" | recovery path recovered 90.0% of readings that reached the ledger |
| "Instrumented every layer" | instrumented the authorization and end-to-end transaction paths |
| "Weakest link" | largest observed operational delay |

## Cannot fix without new measurements

Section 7.4 of the manuscript ("What these measurements cannot establish")
names each of these and the instrumentation required:

- **Stage-level Fabric attribution** needs one transaction timestamped at
  proposal, endorsement, orderer receipt, block cut, validation and commit.
- **Which resource saturates** needs orderer queue depth, block-fill rate,
  validation backlog and disk service times, plus a controlled intervention.
- **Whether privilege costs anything** needs a designed experiment. The
  operational trace's role/operation labels do not separate policy paths:
  grant rates are 91–93% uniformly across all 35 role×operation cells, so a
  null latency difference between them is close to uninformative. This is
  disclosed in a dedicated subsection (6.1.2).
- **End-to-end revocation exposure** needs a correlation identifier logged
  through the pipeline.
- **True radio loss rate** needs gateway-side logging of unrecoverable
  residue sets with RSSI/SNR. Only committed readings are in the trace, which
  is why no event shows fewer than two residues.
- **Authenticated-frame energy** needs the full frame (a 64-byte signature
  alone exceeds the instrumented payloads of 20.5 B and 10.5 B) measured
  across several devices.
- **Adversarial security testing** needs a defined attack population.

## Reproducibility and ethics

- SHA-256 digests, byte counts and row counts for all 11 traces emitted by the
  pipeline into `derived_results.json`.
- `analysis/test_manuscript_consistency.py` asserts every manuscript macro is
  generated and traceable to the results file. Currently: 141 macros defined,
  115 referenced, all traceable.
- Ethics section added: pseudonymised identifiers, consent, site granularity,
  no personal free-text collected.


---

# Round 2: PR #107 review comments (V02 → V03)

All four were valid. Two revealed problems deeper than reported.

| # | Comment | Disposition |
|---|---|---|
| P1 | The 9,797 guard rejects most of the ADC range and `ESP_ERROR_CHECK` aborts the device | **Confirmed and fixed.** `encode_sensor_value` packs `soil * 201 + temp_bucket`, reaching 823,295, so the guard would have aborted every node with soil ≥ 49. Worse: *no* triple of one-byte moduli supports two-of-three recovery at that range (best case 64,262). Moduli changed to {253, 254, 255} and soil quantised 12→8 bits, giving a packed maximum of 51,455. Verified exhaustively over the full packed range for all three residue pairs. A test now pins the encoder to the sensor range so this cannot recur. |
| P1 | Certifier boundary not enforced in chaincode | **Confirmed, and the gap is wider.** `roleAncestors` makes Certifier an ancestor of Agronomist, so Agronomist and Farmer inherit `ReadAudit`. The deployed hierarchy is a chain, not the lattice in Equations (1)-(3), and Agronomist holds `ControlZone` while Farmer lacks `ReadAll`/`ControlAll`. The manuscript now describes the deployed model, Table 2 is generated from `roles.go`, and a new section records the discrepancy rather than papering over it. |
| P2 | Day-level ANOVA ignores the day blocking | **Confirmed and fixed.** Operation vectors share the same 61 days in order. Replaced `f_oneway` with Friedman's test: χ²(6) = 1.59, p = 0.953. TOST is unchanged and remains the primary result. |
| P2 | Consistency test only checks a value appears somewhere | **Confirmed and fixed.** Replaced with regeneration: the pipeline runs into a scratch directory and every generated file is compared byte-for-byte. Verified that swapping `DeployDays` 61→50 now fails, which is exactly the case cited. |

## Consequence for the paper's claims

Two contributions are withdrawn rather than restated:

- **CRT reliability.** The deployed packing exceeded the pairwise bound, so
  readings recovered from two of three residues decoded to `v mod 9797`
  rather than `v`, silently. The signature covers the pre-encoding payload
  and does not catch this. The deployment provides no evidence about the
  redundancy's reliability benefit, only about its cost. Energy and airtime
  figures stand, since they do not depend on decode correctness.
- **Auditor separation.** The deployment did not enforce it. The scripted
  campaign confirms the *implemented* policy was enforced, not the intended
  one.


---

# V04: earning the decomposition title

V02 and V03 retreated from "Decomposing the cost of blockchain-based access
control" because the 940 ms figure was a difference between operation classes,
not a stage attribution, and no per-stage timestamps exist.

V04 restores the title on a different and defensible basis. The
access-control cost does not need stage timestamps, because it is instrumented
directly (`rbac_overhead_ms`, recorded on every write). What remains is
separated with endorsing-peer count as an experimental lever:

    L(p) = A + Q(p) + F

| Term | ms | Share | How obtained |
|---|---|---|---|
| `A` access control | 319 | 26.2% | directly instrumented |
| `Q` endorser-sensitive | 397 | 32.5% | `R(4) - R(32)`, measured, no model fitted |
| `F` peer-invariant remainder | 503 | 41.2% | residual at 32 peers, an upper bound |

The partition closes to 0.9 ms against the observed 1,219.8 ms.

`A` is shown to be separable rather than assumed so: it varies by 3.4 ms
across an eightfold change in peer count, no trend is detected (p = 0.14), and
the extreme configurations are equivalent within the prespecified ±10 ms
margin (TOST p < 0.001). The same term costs a near-constant 9.9% of
throughput across a tenfold concurrency range.

What V04 still does not claim: `F` is not split into ordering, validation and
commit, and the throughput ceiling is not attributed to a named resource.
Both remain in the limitations section with the instrumentation each needs.

Every V02 and V03 correction is retained, including the withdrawn CRT
reliability claim and the documented permission-model gap.


---

# Round 3: PR #108 review comments

All four valid.

| # | Comment | Disposition |
|---|---|---|
| P1 | `F` is the 32-peer residual, not an identified peer-invariant component; the partition closes by construction | **Confirmed and relabelled.** Substituting the definitions leaves `A_pooled - A(4)`, so the 0.9 ms closure restates `A`'s invariance rather than confirming the partition. Worse, the residual's per-doubling decrements are *growing* (73.5, 94.5, 228.7 ms), so there is active evidence against a plateau. `F` is now "residual at the largest configuration tested", stated as an upper bound, everywhere including abstract, highlights, contributions and conclusion. A limitation entry names the configurations needed to find where it levels off. |
| P2 | `tost_paired` zips two separate campaigns by row position | **Confirmed and fixed.** The 4-peer and 32-peer runs have disjoint sample IDs and no shared experimental unit. Added `tost_independent` (Welch variance, Satterthwaite df): diff −2.58 ms, df 1595, 90% CI [−4.62, −0.55], p = 1.2e-9. Conclusion unchanged, derivation now valid. `tost_paired` is retained only for the day-level operation vectors, which are genuinely blocked by day. |
| P2 | The 32-peer access-control share is 38.7%, not 26.2%, and the percent sign is missing | **Confirmed and fixed.** New macro `PartAccessPctAtMax`. The sentence now reads 26.2% at 4 peers rising to 38.7% at 32, which is what it was trying to say. |
| P2 | `dist/README.md` still tells the reader to rebuild with `V02` | **Confirmed and fixed.** Following it would have overwritten the superseded V02 archives with current content. |


---

# V05: second premortem, assuming V04 was rejected

The second premortem predicted rejection on three grounds: the article is too
long for what it establishes, it is internally inconsistent about how much
its own system worked, and it measures a deployment whose authorization
policy and sensor decoding were both wrong. The third is the substantive one,
and it is correct.

## What auditing the code against the manuscript found

Four defects, none of which the measurements would have surfaced. They are
now a first-class section of the article (`Deployment postmortem`) rather
than caveats scattered through the results.

| # | Defect | Effect on the deployment | Effect on the results |
|---|---|---|---|
| D1 | `roleAncestors` places Certifier on the human inheritance chain, so Agronomist and Farmer inherit `ReadAudit` | Audit-log access was not confined to auditors for the whole 61 days | None on timing. The security campaign tested the implemented policy, not the intended one. |
| D2 | Residue moduli {97, 101, 103} with a packed value reaching 823,295 | Any reading recovered from two of three residues decoded to `v mod 9797`, silently | Energy and airtime stand (they do not depend on decode correctness). No reliability claim survives. |
| D3 | The gateway verified an ASCII rendering of the decoded value while the firmware signed a packed binary struct | Signature verification could never succeed, and `verify_signature` returned `True` whenever a signature was absent, so it failed open | The `signature_valid` column records the fail-open path. The transport-integrity claim is withdrawn entirely. |
| D4 | Revocation lifecycle stages carry no episode key | End-to-end exposure was never observable in production | Stage timings stand as stage timings; the operationally important interval is unmeasured. |

All four are fixed in the released code: `roles.go` and the generated Table 2,
`crt_encode.[ch]` and `crt_decode.py` on {253, 254, 255} with 8-bit soil
quantisation, `gateway.py` verifying the exact firmware byte layout with
unsigned readings rejected by default. `gateway/tests/test_signature_binding.py`
pins the verification bytes to the firmware struct so D3 cannot recur silently,
and the encoder range test pins D2.

D1 to D3 share a shape: each is a place where the paper described an intended
property and no test compared the description to the code. The article says
so in `What the pattern suggests`, and the machinery added across V02 to V05
is the response: Table 2 is generated from `roles.go`, every number expands
from a macro generated by the pipeline, and
`analysis/test_manuscript_consistency.py` regenerates the whole pipeline and
compares byte-for-byte.

## Claims withdrawn or narrowed in V05

| Was (V04) | Now (V05) |
|---|---|
| Transport integrity verified end to end; 100% of readings carried valid signatures | Withdrawn. The verifier and the signer disagreed on the message. `SigValidPct` is reported as an artifact of the fail-open path, not as evidence. |
| 8,000 scripted cases confirm the authorization model | 8,000 requests crossing some boundary of the *deployed* policy were refused, across six denial paths. The scenario labels do not match the recorded operations, and this is stated where the result is reported. |
| Capacity ceiling sits in the ordering service | Below the policy layer; candidates listed, none identified. (Carried from V02.) |
| Auditor separation as a deployed property | Not in force. Recorded as D1. |
| `A` = 319 ms and standalone `CheckAccess` = 280 ms presented side by side | The 39 ms gap is an instrumentation defect: the trace does not document where the inner counter starts and stops, so the two are not directly comparable. Named in the limitations. |
| eFuse read protection listed among the architectural defences | Removed. Read protection is not enabled and cannot be with software Ed25519 on this part. |

## Length

V04 ran to roughly 14,400 words including references. V05 is about 12,700
words of body text, a reduction of about 1,700, achieved by moving
Algorithms S1 to S3 and the operational observations into a supplementary
document that ships in both packages, condensing the related-work survey,
merging duplicated framing in the role-hierarchy and security subsections,
and consolidating the limitations. The double-column build is 21 pages
against the journal's 14-to-29-page range.

## Questions the premortem asked that the data still cannot answer

These are in `What these measurements cannot establish`, each with the
instrumentation that would settle it: whether the residual has a floor,
where the inner access-control counter starts and stops, stage-level
attribution inside `F`, which resource saturates, whether privilege level
costs anything, end-to-end revocation exposure, total radio loss,
authenticated-frame energy, and adversarial security testing. Two further
questions the premortem raised have no answer in the trace at all: whether
the `agronomist_irrigate` requests were in-zone (the recorded operations
span all four zones, so the label cannot be read as a scenario description),
and whether mis-decoded readings drove irrigation decisions. The decision
trace does record authorization requests against an `IrrigationControl`
resource, but it carries no reading identifier, so no actuation can be joined
to the reading that might have prompted it.

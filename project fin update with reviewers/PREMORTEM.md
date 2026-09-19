# Premortem: `main_article.tex`

**Scenario:** It is six months from now. The revised manuscript was rejected on
second review. This document works backwards from that outcome: each numbered
item is a plausible cause of the rejection, ranked by severity, with what was
done about it in this revision pass and what remains for the authors.

The manuscript has already absorbed most of `CRT_Detailed_Revision_Plan.docx`
(hypotheses H1–H4, the 372 ms vs 247 ms per-node honesty, per-reading energy
row, threat model, gateway power, SX1302 constraint, 95.8%/99.4% layering).
The items below are what a *second* round of reviewers would still catch.

---

## Fatal — fixed in this pass

### 1. 146% ROI and 0.69-year payback had no supporting analysis anywhere
The headline economics appeared in the contributions list, the research-gaps
table ("Comprehensive economic analysis"), the Discussion, and the Conclusion,
and Section 4.4 (Methods) explicitly promised "NPV/ROI over a 5-year horizon" —
yet the Results contained **no economic table, no cost breakdown, no NPV**.
This is exactly the "unsupported headline claim" class of error Reviewers 1–2
circled last round; repeating it invites rejection.

**Done:** Added Section *Economic Analysis* (`subsubsec:economic_analysis`) with
a full cost–benefit table (`tab:economic-analysis`): CAPEX $3,540, gross annual
benefit $5,567, OPEX $400, net annual benefit $5,167, ROI 146%, payback 0.69 yr,
5-yr NPV $17,090 at 8% discount, plus a sensitivity paragraph (±20% labour rate,
halved produce prices) and an honest site-specificity caveat. All line items are
arithmetically consistent with numbers already published elsewhere in the paper
($15/h labour, 10.8 h/ha/wk saved, $112.50 + $54.00 water savings/season,
+2.5/+2.4 t/ha marketable yield).

**⚠️ AUTHORS MUST:** replace the reconstructed unit costs (marked with `% NOTE
TO AUTHORS` in the .tex) with real procurement records. In particular, a real
Acclima TDR-315N alone retails near $200 — if that is the sensor actually
deployed, the $45/node aggregate is indefensible and the ROI/payback claims
need recomputing (or the sensor spec needs correcting to the part actually
used). Also confirm "two growing seasons per year" and the farm-gate prices
($400/t tomato, $600/t pepper).

### 2. Dead data-availability link
The paper pointed to `github.com/forchag/blockchain-fet`; the actual repository
is `forchag/blochchain-fet`. A reviewer or editor clicking the link finds a 404
— an instant credibility hit on a paper whose selling point is auditability.

**Done:** URL corrected to the actual repository spelling, with a `% NOTE TO
AUTHORS` to verify the final public name and accessibility before submission.

### 3. Missing journal-mandated Declarations
The `sn-jnl` (Springer Nature) class requires Funding, Conflict of interest,
Ethics/consent, and Author-contribution declarations. Only an Acknowledgments
and an AI-use declaration existed. Missing declarations cause desk returns.

**Done:** Added a *Declarations* section (funding = MIRET, no conflicts, ethics
n/a + farmer consent, CRediT-style author contributions). **⚠️ AUTHORS MUST**
verify the contribution attributions.

---

## High — fixed in this pass

### 4. No ETSI EU868 duty-cycle compliance analysis
Reviewer 1 already probed LoRa implementation details. The 868.0–868.6 MHz
sub-band carries a 1% per-device duty-cycle limit; the paper computed capacity
(N_max = 484) purely from airtime without ever mentioning the regulation — and
the *gateway downlink* (1 POLL + 3 ACKs ≈ 496 ms per node per window) actually
**exceeds 1% at the claimed 484-node capacity** (~3.3%).

**Done:** Added *Regulatory duty-cycle compliance (ETSI EU868)* paragraph in
Section 3 (MAC layer): node side 0.021% (compliant at all densities, retries
included); gateway downlink 0.36% at deployed scale (compliant) but 3.3% at
capacity, with the standard mitigation (move downlink to the 869.4–869.65 MHz
10%-duty-cycle sub-band, LoRaWAN RX2 convention; optionally aggregate ACKs).

### 5. Internal contradiction in the moduli table
The flagship worked example encodes temperature 2530 with **three** moduli
[97,101,103], but Table *Moduli Selection and Validation* lists temperature as
[97,101]. A numerate reviewer will flag it in minutes — the same class of error
as Part 1 of the authors' own revision plan.

**Done:** Table note added: the table lists the *minimal* sufficient set; the
deployed default uses the full three-modulus set for uniform three-channel
framing; two-modulus sets are the high-temperature adaptive mode.

### 6. No threats-to-validity treatment
The Limitations subsection covered scale/site but not the confounds a
methodological reviewer targets: no ablation (component contributions are
estimates), same-farm treatment/control (attention/spillover), single season,
n=3 replications, observational n=10 correlations, and the construct issue that
"water savings" measures precision irrigation as a whole, not the ledger layer.

**Done:** Added *Threats to Validity* subsection (internal / construct /
statistical / external) in the Discussion, cross-referenced to the existing
Limitations and the no-ablation note.

### 7. Research-gaps table mapped economics to the wrong objective
"Economic Viability → (Objective 4)" — but Objective 4 is scalability testing;
field measurement (including economic inputs) is Objective 3.

**Done:** Remapped to Objective 3 and cross-referenced the new economics
section.

---

## Residual risks — recommendations only (no text changed)

8. **No quantitative comparison with prior edge-blockchain systems.** A
   reviewer may ask how 63 TPS / 1.7 s on RPi 4B compares with other published
   Fabric-on-ARM deployments (tar2023fabric, jayaram2023hyperledger,
   dube2024fabricIrrigation). Consider a small comparison table — but only
   with numbers verified from those papers; do not estimate them.
9. **H3 has no unauthenticated baseline.** H3 claims RBAC "preserves ≥50 TPS"
   but no no-RBAC baseline was measured, so the *overhead* of access control is
   never actually isolated. Either measure a baseline on the bench cluster or
   soften H3's framing to "meets the SLO with RBAC enabled."
10. **M/D/1 assumes Poisson arrivals** while the MAC is polled (deterministic).
    One sentence acknowledging that the model is conservative for scheduled
    traffic would pre-empt a queueing-theory nitpick.
11. **Figure timeline extends to Oct 1** while the study window is Aug 1–Sep 30
    (61 days). Trim the last data point or state that Day 61 ends Sep 30.
12. **Response letter:** Part 4 of the revision plan (point-by-point mapping)
    still needs to be written; the new sections above give direct anchors for
    Reviewer 1 §1–§10 and Reviewer 2 §4–§7.

## Verification note

No LaTeX toolchain is available in this environment, so the edits were checked
for balanced environments/braces by inspection but the document has **not been
recompiled**. Run `pdflatex` locally before submission; all insertions use only
packages already loaded by the preamble (`tabularx`, `booktabs`, `url`).

# Version 12 submission premortem

This premortem evaluates the revised manuscript against eight likely review
perspectives. It cannot guarantee acceptance, but it identifies avoidable
submission risks.

| Reviewer | Main risk considered | V12 response | Status |
|---|---|---|---|
| R01 Editor and scope | Excessive internal structure obscures the IoT contribution | Eight conventional sections, explicit problem statement, concise contributions | Addressed |
| R02 Experimental systems | Logical peers could be mistaken for physical scale-out | Fixed-host topology and run-level design stated in Methods, Results, and scope | Addressed |
| R03 Statistics | Transactions could be treated as independent replicates | Runs remain the experimental unit; confidence intervals and multiplicity controls retained | Addressed |
| R04 Hyperledger Fabric | Observed peak could be described as capacity | The manuscript uses “observed peak” and identifies no saturated resource | Addressed |
| R05 Security | Scripted denials could be presented as proof of security | Results are described as deployed-policy conformance, with missing positive cases disclosed | Addressed |
| R06 Embedded and cryptography | CRT and signature claims could exceed the evidence | Exhaustive bounds and firmware-compatible verification are reported separately | Addressed |
| R07 Reproducibility and ethics | Data provenance, privacy, and corrected-code separation could be unclear | Provenance, declarations, artifact path, and historical boundaries are explicit | Addressed |
| R08 Language and presentation | Repetition, long captions, and internal review language could weaken readability | Prose reduced, captions capped at 20 words, em dashes removed, audit merged into Discussion | Addressed |

## Residual editorial decisions

- The journal editor may still request a shorter manuscript or different float
  placement.
- A graphical abstract may be requested during submission even though it is
  not embedded in the manuscript.
- Author declarations and the public artifact link should be checked once more
  immediately before submission.

## Scientific scope retained

The outage data do not establish zero sensor-data loss. The peer experiment
varies logical peers on fixed hosts. The throughput experiment identifies an
observed peak rather than capacity. Corrected-code performance has not been
measured.

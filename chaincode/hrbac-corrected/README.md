# Corrected HRBAC chaincode

This package is the corrected variant of `chaincode/hrbac/`, the chaincode
that produced every measurement in the manuscript. It exists so a reader
can compare the historical deployed policy against a fixed one directly,
rather than take a prose description on faith.

## What changed, and why

`chaincode/hrbac/roles.go` places `Certifier` on the human inheritance
chain (`SupplyChain -> Certifier -> Agronomist -> Farmer -> Admin`) rather
than beside it. Two consequences follow, both documented in the
manuscript's implementation postmortem:

1. `Agronomist` and `Farmer` inherit `Certifier`'s `ReadAudit` permission,
   so the auditor separation the design exists to provide (an auditor
   verifies compliance without gaining agronomic access) was never in
   force for the 61-day deployment.
2. `Certifier` itself holds `ReadZone`, so an auditor can read raw zone
   sensor data directly rather than only audit/compliance records.

`roles.go` in this directory removes `Certifier` from `Agronomist`'s and
`Farmer`'s ancestor sets, and moves `ReadZone` off `Certifier`'s direct
grant onto `Agronomist` and `Farmer` directly, so neither loses the zone
visibility the design intends them to have. See `ROLES_DIFF.patch` for the
exact diff. `contract_test.go` adds `TestAuditorSeparationHolds`, which
fails against `chaincode/hrbac`'s hierarchy and passes against this one —
a regression test for this specific defect, not a general
policy-conformance suite.

A second defect was found reviewing an earlier draft of this same
correction: that draft left `Agronomist` with a direct `ControlZone`
grant, contradicting the manuscript's own "history but no actuation
rights" description of the role. This is fixed here too: `ControlZone` is
removed from `Agronomist`'s direct grants, and `Farmer` — which no longer
inherits it from `Agronomist` once that grant is removed — receives its
own direct `ControlZone` grant, so operational control stays where the
design intends it and every other effective permission is unchanged.
`contract_test.go` adds `TestAgronomistCannotControlZone`, verified the
same way: it fails against `chaincode/hrbac`'s hierarchy (confirmed by a
throwaway copy of the test run against that package during development)
and passes here.

## A third defect, found while adding the revocation fix below

`chaincode/hrbac/contract.go`'s `CheckAccess` reads a `crl:<serial>` world
state key to decide whether a caller's certificate has been revoked, but no
transaction in that package ever writes such a key. `scripts/generate-crl.sh`
already invoked an `UpdateCRL` transaction as part of the field revocation
workflow, but the deployed chaincode has no function by that name: the
invoke always failed with an unknown-transaction error, the script logged
"CRL chaincode update skipped/failed" and continued, and the on-ledger
certificate-revocation check was dead code for the full 61-day deployment.
Certificate revocation still worked operationally, through the Fabric CA's
own CRL enforced at the mutual-TLS layer and through `RevokeRole` deleting
the role assignment, a separate and functioning mechanism, so this defect
does not put any reported measurement in question. `UpdateCRL` is added
here: it parses a CRL (exactly the bytes `scripts/generate-crl.sh` already
produces), writes a `crl:<serial>` entry for each revoked certificate, and
is Admin-gated like the other administrative transactions.
`TestUpdateCRLWritesRevocationEntriesAndDeniesCheckAccess` and
`TestUpdateCRLRequiresAdmin` in `contract_test.go` are the regression tests.

## Revocation-episode correlation

`RevokeRole` and `UpdateCRL` both stamp a new `AuditEntry.EpisodeID` field
with the caller-supplied correlation token: in practice, the same value
`scripts/revoke-cert.sh` and `scripts/generate-crl.sh` now share for one
revocation request. This is the fix for the revocation-observability gap
the manuscript's postmortem describes: the historical trace has no key
linking CRL publication, gossip propagation and cache invalidation into one
episode, so end-to-end exposure could not be reconstructed. Threading one
token through the chaincode side of the pipeline, and through
`gateway/policy_cache.py`'s cache invalidation on the gateway side, gives a
future deployment a real join key across all three stages.
`TestUpdateCRLRecordsEpisodeIDOnAuditEntry` and
`TestRevokeRoleRecordsEpisodeIDOnAuditEntry` verify the chaincode side; the
gateway side is tested in `gateway/tests/test_policy_cache.py`. This does
not, and cannot, resolve episodes already present in the historical trace:
that data was collected before this change existed.

## What this does not fix

The residue-encoding and signature-verification fixes described in the
manuscript's postmortem are separate changes, already applied in
`esp32/` and `gateway/` on the repository's main branch; this directory
addresses the role-hierarchy defects, the missing CRL-writer transaction,
and revocation-episode correlation above. No permission other than the ones
named in the role-hierarchy paragraphs differs from
`chaincode/hrbac/roles.go`.

## Why `chaincode/hrbac/` is not simply edited in place

The traces in `data/raw/` and every number in the manuscript were produced
by the chaincode as deployed, defect included. Patching it in place would
make the released chaincode diverge from the code that generated the
reported measurements, so a reader could no longer check the paper's
numbers against the exact source that produced them. Keeping both
directories side by side, each independently buildable and testable
(`go test ./...` from within either), lets a reader compare policies
without losing that traceability. The two are tagged separately in the
repository as `v09-deployed-historical` and `v09-corrected`.

## Performance

This is a policy correction, not a re-run of the performance campaigns.
Whether it changes gateway processing time, the recorded authorization
span, or throughput has not been measured; see the manuscript's "What
these measurements cannot establish" section.

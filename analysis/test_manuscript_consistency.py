#!/usr/bin/env python3
"""Assert that the manuscript cannot disagree with the derived results.

The paper claims every reported number is generated from the traces.  The
check that actually establishes that is regeneration: run the pipeline into a
scratch directory and compare its output byte-for-byte with the committed
files.  Anything hand-edited, stale, or cross-assigned shows up as a diff.

A weaker check that merely asks whether each macro value appears *somewhere*
in the results would pass if two same-scale statistics were swapped, which is
exactly the drift this is meant to catch.

Also verifies that every macro the manuscript references is defined.

Run:  python3 analysis/test_manuscript_consistency.py
"""

from __future__ import annotations

import difflib
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAPER = ROOT / "paper_iot"
PIPELINE = ROOT / "analysis" / "derive_results.py"

# Control sequences the document or LaTeX defines, not the pipeline.
NON_PIPELINE = {
    "widefig", "widetab", "widealg", "algcomment", "tblwidth",
    "PassOptionsToPackage", "WriteBookmarks", "FloatBarrier",
    # algorithmicx keywords
    "State", "Statex", "If", "EndIf", "Else", "ElsIf", "For", "EndFor",
    "ForAll", "While", "EndWhile", "Return", "Require", "Ensure", "Comment",
    "Procedure", "EndProcedure", "Function", "EndFunction", "Repeat", "Until",
    # role and permission names typeset in equations and tables
    "Admin", "Farmer", "Agronomist", "Certifier", "Sensor", "Gateway",
    "Supply", "SupplyChain", "ReadOwn", "ReadZone", "ReadAll", "ReadAudit",
    "ControlZone", "ControlAll", "ManageRoles", "WriteSensor", "IssueCrossZone",
    "Grant", "Deny", "ReplayDetected", "CertRevoked", "RoleInsufficient",
    "OpNotPermitted", "ZoneMismatch", "Nonce", "SeenBefore", "ParseZoneASN",
    "OnCRL", "RoleAssignments", "RevokeRole", "ZoneOf", "ValidCZT",
    "RecordNonce", "Audit", "WriteAudit", "Blk", "EfuseWrite", "MakeCSR",
    "Sign", "VerifySig", "CAIssue", "RtcRead", "MagicOK", "CrcOK", "GpsTime",
    "NtpTime", "RateLimitOK", "EfuseSetReadDisable",
    "CAAppendCRL", "PublishCRL", "LedgerWrite", "Reachable",
    "InvalidatePolicyCache", "Delayed", "Ed", "San", "NotAfter",
    # repository metadata, not a measurement: set by a small follow-up
    # commit in paper_iot/commit_hash.tex, not by derive_results.py
    "CommitHash",
}


def regenerate_into(tmp: Path) -> subprocess.CompletedProcess:
    """Run the pipeline, writing all generated artifacts under `tmp`."""
    return subprocess.run(
        [sys.executable, str(PIPELINE),
         "--out-dir", str(tmp / "analysis"),
         "--tex-out", str(tmp / "derived_numbers.tex"),
         "--fig-dir", str(tmp / "figdata")],
        capture_output=True, text=True,
    )


def compare(committed: Path, fresh: Path, failures: list[str]) -> None:
    if not fresh.exists():
        failures.append(f"pipeline did not produce {fresh.name}")
        return
    if not committed.exists():
        failures.append(f"missing committed file {committed}")
        return
    a = committed.read_text().splitlines()
    b = fresh.read_text().splitlines()
    if a != b:
        diff = list(difflib.unified_diff(
            a, b, fromfile=f"committed/{committed.name}",
            tofile=f"regenerated/{fresh.name}", lineterm="", n=0))
        failures.append(
            f"{committed.name} differs from a fresh run:\n    "
            + "\n    ".join(diff[:20]))


def main() -> int:
    failures: list[str] = []

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        (tmp / "analysis").mkdir()
        run = regenerate_into(tmp)
        if run.returncode != 0:
            print("FAIL: pipeline errored\n" + run.stderr[-2000:], file=sys.stderr)
            return 2

        # 1. macros must be exactly what the pipeline emits
        compare(PAPER / "derived_numbers.tex", tmp / "derived_numbers.tex",
                failures)

        # 2a. the permission table must match the deployed chaincode
        policy_out = tmp / "tab_permissions.tex"
        policy = subprocess.run(
            [sys.executable, str(ROOT / "analysis" / "derive_policy_table.py"),
             "--out", str(policy_out)],
            capture_output=True, text=True)
        if policy.returncode != 0:
            failures.append("policy table generator failed: "
                            + policy.stderr[-500:])
        else:
            compare(PAPER / "tables" / "tab_permissions.tex", policy_out,
                    failures)

        # 2b. so must the generated result tables and figure data
        for name in sorted(p.name for p in (tmp / "tables").glob("*.tex")):
            compare(PAPER / "tables" / name, tmp / "tables" / name, failures)
        for name in sorted(p.name for p in (tmp / "figdata").glob("*.dat")):
            compare(PAPER / "figdata" / name, tmp / "figdata" / name, failures)

    # 3. every macro the manuscript references must be defined
    defined = set(re.findall(r"\\newcommand\{\\(\w+)\}",
                             (PAPER / "derived_numbers.tex").read_text()))
    referenced: set[str] = set()
    for path in [PAPER / "hrbac_iot_cas.tex", *sorted((PAPER / "tables").glob("*.tex"))]:
        text = re.sub(r"(?m)^\s*%.*$", "", path.read_text())
        referenced |= set(re.findall(r"(?<!\\)\\([A-Z]\w{2,})", text))
    unknown = referenced - defined - NON_PIPELINE
    if unknown:
        failures.append(f"macros used but not generated: {sorted(unknown)}")

    if failures:
        print("FAIL")
        for f in failures:
            print("  -", f)
        return 1

    print(f"PASS: {len(defined)} macros, {len(referenced & defined)} referenced; "
          f"macros, tables and figure data all reproduce a fresh pipeline run "
          f"byte-for-byte")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

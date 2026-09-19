#!/usr/bin/env python3
"""Independent re-derivation of two headline statistics, using a different
implementation path than analysis/derive_results.py.

Why this exists
---------------
A reviewer premortem asked that the generative-AI declaration name
something more concrete than "the authors reviewed the code": an
independently coded check that a second implementation reaches the same
number, not a re-read of the first one. This script recomputes two of the
manuscript's primary statistics straight from the raw CSVs with a
different toolchain than derive_results.py's:

* derive_results.py's peer-scaling Welch test uses this project's own
  hand-written ``welch()`` helper (analysis/derive_results.py); this
  script instead calls ``scipy.stats.ttest_ind(..., equal_var=False)``
  directly, and computes Cohen's d from numpy's own variance functions.
* derive_results.py's throughput factorial model is fit by explicit
  matrix inversion (``multiple_regression()``, a hand-written OLS); this
  script instead builds the same design with ``pandas`` and fits it with
  ``statsmodels.OLS``, a separately implemented regression routine.

Both paths read the same released CSVs (data/raw/), so this is not a test
of the data -- it is a test of whether the arithmetic derive_results.py
reports can be reproduced by different code. It is deliberately not
wired into test_manuscript_consistency.py's byte-for-byte macro check:
that test guards against *drift* between the manuscript and
derive_results.py's own numbers, which this script cannot help with,
since it does not know about derived_numbers.tex's macros at all -- it
only prints its own numbers next to the ones this file's authors read off
derived_numbers.tex by hand when writing it, for a human to compare.

Usage:
    python3 analysis/independent_check.py
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"


def peer_scaling_welch() -> None:
    print("=== Peer-scaling Welch t/d, 4 vs 32 peers (independent path) ===")
    rows = [r for r in csv.DictReader(open(RAW / "raw_latency_samples.csv"))
            if r.get("run_id")]
    by_run: dict[str, dict] = {}
    for r in rows:
        rid = r["run_id"]
        entry = by_run.setdefault(rid, {"peers": int(r["peer_count"]),
                                         "total": []})
        entry["total"].append(float(r["latency_ms"]))
    lo = [np.mean(v["total"]) for v in by_run.values() if v["peers"] == 4]
    hi = [np.mean(v["total"]) for v in by_run.values() if v["peers"] == 32]
    t, p = stats.ttest_ind(lo, hi, equal_var=False)
    n1, n2 = len(lo), len(hi)
    s1, s2 = np.std(lo, ddof=1), np.std(hi, ddof=1)
    pooled_sd = np.sqrt(((n1 - 1) * s1 ** 2 + (n2 - 1) * s2 ** 2) / (n1 + n2 - 2))
    d = (np.mean(lo) - np.mean(hi)) / pooled_sd
    diff = np.mean(lo) - np.mean(hi)
    se = np.sqrt(s1 ** 2 / n1 + s2 ** 2 / n2)
    dof = (s1 ** 2 / n1 + s2 ** 2 / n2) ** 2 / (
        (s1 ** 2 / n1) ** 2 / (n1 - 1) + (s2 ** 2 / n2) ** 2 / (n2 - 1))
    tcrit = stats.t.ppf(0.975, dof)
    print(f"n={n1},{n2}  mean_4={np.mean(lo):.1f}  mean_32={np.mean(hi):.1f}  "
          f"diff={diff:.1f}  95% CI=[{diff - tcrit * se:.1f}, "
          f"{diff + tcrit * se:.1f}]  t={t:.2f}  d={abs(d):.2f}  p={p:.4f}")
    print("Compare against \\ScaleDiffMs / \\ScaleDiffCILow / "
          "\\ScaleDiffCIHigh / \\ScaleT / \\ScaleD in "
          "paper_iot/derived_numbers.tex.\n")


def throughput_factorial_statsmodels() -> None:
    print("=== Throughput factorial model (independent path: pandas + "
          "statsmodels.OLS) ===")
    df = pd.read_csv(RAW / "raw_throughput_samples.csv")
    df["condition"] = (df["benchmark_type"] == "HRBAC").astype(float)
    df["concurrency_c"] = df["concurrent_clients"] - df["concurrent_clients"].mean()

    # Position within its own concurrency level's cell, not the raw global
    # run_sequence -- the global sequence is collinear with concurrency
    # level here (levels were tested in one fixed ascending order), so it
    # cannot serve as an independent order covariate. See
    # derive_results.py's analyse_throughput() for the same reasoning.
    df["position_in_level"] = (
        df.sort_values("run_sequence")
          .groupby("concurrent_clients")
          .cumcount() + 1)
    df["position_c"] = df["position_in_level"] - df["position_in_level"].mean()
    df["interaction"] = df["condition"] * df["concurrency_c"]

    X = sm.add_constant(df[["condition", "concurrency_c", "interaction",
                             "position_c"]])
    model = sm.OLS(df["tps"], X).fit()
    ci = model.conf_int(alpha=0.05)
    print(model.summary().tables[1])
    print(f"\nR^2={model.rsquared:.3f}")
    print("Compare coefficients/CIs/p-values against \\ThrCondCoef, "
          "\\ThrInteractCoef, \\ThrPositionP, \\ThrFactorialRSq in "
          "paper_iot/derived_numbers.tex (note sign convention: the "
          "manuscript reports the HRBAC-below-baseline magnitude, this "
          "model's raw coefficient is signed the opposite way since "
          "condition=1 is HRBAC).\n")


if __name__ == "__main__":
    peer_scaling_welch()
    throughput_factorial_statsmodels()

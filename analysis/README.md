# Analysis pipeline

Everything reported in the manuscript is derived from the traces in
`data/raw/` by the scripts in this directory. No measured value is typed into
the LaTeX source by hand.

## Regenerate the paper's numbers

```sh
python3 analysis/derive_results.py
```

Reads `data/raw/*.csv` and writes:

| Output | Purpose |
|---|---|
| `analysis/derived_results.json` | complete statistical summary, machine-readable |
| `analysis/derived_results.md` | human-readable audit table |
| `paper_iot/derived_numbers.tex` | LaTeX macros the manuscript expands |
| `paper_iot/tables/*.tex` | complete table environments |
| `paper_iot/figdata/*.dat` | pgfplots data tables |

Then `bash paper_iot/build.sh` compiles the manuscript against them.

## Statistical conventions

- **Group comparisons** use Welch's *t*-test (no equal-variance assumption),
  reported with the mean difference, its 95% CI, and Cohen's *d*. At these
  sample sizes significance is nearly automatic, so the effect size is the
  informative quantity.
- **More than two groups** use one-way ANOVA — this is what establishes that
  decision cost does not vary by operation type.
- **CIs on means** use the Student-*t* interval for n ≥ 1000 and a percentile
  bootstrap (10,000 resamples) below that.
- **CIs on quantiles** use the exact order-statistic (binomial) construction,
  so no distributional assumption is imposed on the latency tail.
- **Proportions at or near 1.0** use Wilson score intervals. A
  normal-approximation interval has zero width at p = 1 and would overstate
  the evidence behind the 100% block rate.

Bootstrap resampling is seeded (`SEED = 20250801`) so runs are reproducible.

## Re-measure on your own Fabric network

```sh
python3 analysis/run_campaign.py --dry-run          # validate configuration
python3 analysis/run_campaign.py --out-dir results/raw
python3 analysis/derive_results.py --raw-dir results/raw \
    --out-dir results/analysis
```

The campaign driver writes CSVs in the same schema as `data/raw/`, so the
analysis consumes its output unchanged and the paper regenerates against
independent measurements. It requires a bootstrapped Fabric network with the
`peer` CLI on PATH.

The driver covers the throughput, latency and decision-cost campaigns. It
does **not** reproduce the energy or cryptographic-timing traces: those need
the INA219 instrumentation and ESP32 bench described in the paper, and the
driver analyses the real measured records consolidated from the two merged source folders.

# Analysis of the completed deployment

I use the scripts in this directory to examine the recorded deployment data and check the results reported in the manuscript. The input records are maintained in `data/raw/`. Calculations and statistical summaries remain traceable to those records.

## Results and supporting files

| File | Description |
|---|---|
| `derive_results.py` | Statistical analysis of the recorded observations |
| `derived_results.json` | Detailed numerical results |
| `derived_results.md` | Summary of the reported findings |
| `derive_policy_table.py` | Authorization matrix taken from the HRBAC chaincode |
| `independent_check.py` | Separate verification of selected statistics |
| `test_manuscript_consistency.py` | Checks the agreement between reported results and the analysis outputs |
| `airtime_capacity.py` | Analytical LoRa airtime and capacity calculations |
| `transmission/` | Transmission comparisons, service-rate analyses and the separately identified collision model |
| `run_campaign.py` | Measurement procedure for a separately configured Fabric network |
| `requirements.txt` | Python dependencies |

The analysis writes numerical summaries in `analysis/` and the corresponding manuscript tables, figures and macros in `paper_iot/`.

## Statistical methods

I use Welch's t-test for two-group comparisons, one-way ANOVA for comparisons involving more than two groups, and effect sizes alongside confidence intervals. I use Student-t or percentile-bootstrap intervals for means as appropriate, order-statistic intervals for quantiles, and Wilson score intervals for proportions near their limits. The bootstrap seed is fixed at `20250801` for repeatability.

## Reviewing the results

```sh
python3 analysis/derive_results.py
python3 analysis/independent_check.py
python3 analysis/test_manuscript_consistency.py
```

I keep measured observations distinct from analytical calculations and modeled results. The scripts for a separate measurement campaign do not substitute for the original deployment records.

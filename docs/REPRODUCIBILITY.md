# Reproducing the paper's calculations

I use the submitted manuscript for reported values. I do not change source records to force agreement.

## Transmission analysis

From the repository root, I run:

```bash
python3 analysis/airtime_capacity.py
python3 analysis/transmission/gateway_service_rate.py
python3 analysis/transmission/fixed_point_baseline.py
```

I compare complete five-quantity readings, not individual residue packets alone. I use 15 residue packets per CRT reading.

## Deposited reference records

I keep selected Data-fet records under `data/data_fet_reference/`. Existing `data/raw/` data remains in place. I check each script's input paths before use; a script that expects newer records may need an explicit data directory.

## Limits

I cannot recover original measurements or the exact deployed firmware from calculation scripts. I document any unverified deployment parameter.

I record disagreements between recalculated values and the manuscript rather than hiding them.

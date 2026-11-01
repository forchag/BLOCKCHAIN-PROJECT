# Data dictionary

I keep reference records from Data-fet under `data/data_fet_reference/`. I keep the existing repository data under `data/raw/` until the versions are reconciled.

| Record | Purpose | Current basis |
| --- | --- | --- |
| `field/node_power_profile.csv` | Battery, power, and reporting interval | Recorded columns and calculated columns mixed; acquisition details unverified |
| `experiments/energy_measurements.csv` | Packet energy and airtime comparisons | Origin of packet timing unverified |
| `experiments/transmission_cost_index.csv` | Normalized index | Calculated |
| `experiments/economic_reconciliation.csv` | Economic estimates | Calculated; differs from manuscript ROI |
| `agronomic/rcbd_layout.csv` | Plot and treatment allocation | Verify against field layout |
| `security/ledger_record_format.csv` | Ledger record component estimates | All component sizes marked unverified |
| `field/sensor_transactions.csv` | Field sensor transactions | Source-of-record unresolved |

I will document units, field definitions and missing values after I confirm each source and its acquisition process.

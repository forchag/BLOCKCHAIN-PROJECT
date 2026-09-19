# Outage / sensor-transaction integrity reconciliation

This Version 11 report supersedes earlier reports that used a different
analyst package. It is based only on the committed repository files
`data/raw/raw_uptime_events.csv` and `data/raw/raw_sensor_transactions.csv`.

The uptime log records three gateway events (8.7 h, 0.4 h and 0.2 h). The
sensor table has one timestamp per row and contains no independently recorded
sensor-capture time, gateway-receive time, ledger-commit time, retry count,
replay flag or buffer-source field. Counting rows whose timestamp falls in the
logged outage windows gives 234, 12 and 13 affected-gateway rows, respectively.

The records therefore cannot establish whether an outage-period row was
captured before disconnection, buffered and replayed, or reconstructed during
processing. The outage notes and regular daily row count are consistent with a
buffering hypothesis, but do not prove it. V11 reports availability and
observed ledger-table row completeness separately and withdraws any claim of
zero sensor-data loss or verified buffering.

The stronger, incompatible “38/38 verified buffered replay” finding from the
alternate V10 package is not used in the manuscript and is not evidence for
the Version 11 artifact.

# Version 11 outage reconciliation

This report is based on the committed data/raw/raw_uptime_events.csv and
data/raw/raw_sensor_transactions.csv. The two files are retained unchanged.

The uptime log records three gateway events:

| Event | Gateway | Duration | Log note |
|---|---|---:|---|
| O1 | gw-north-01 | 8.7 h | LoRa link failure; delayed sync on recovery |
| O2 | gw-east-01 | 0.4 h | Power fluctuation; buffered data re-synced |
| O3 | gw-south-01 | 0.2 h | Firmware watchdog reset; no data loss |

The sensor table has one timestamp per record. Counting records whose timestamp
falls inside each logged outage gives:

| Event | Affected-gateway rows in outage window | Affected sensors |
|---|---:|---:|
| O1 | 234 | 13 |
| O2 | 12 | 12 |
| O3 | 13 | 13 |

These rows show that the sensor table is not a simple “no writes during every
outage” trace. Because the timestamp's semantic meaning is not documented and
there is no capture/receive/commit triplet, the records cannot establish
whether they are sensor-capture timestamps, delayed ledger commits, buffered
replays, or a reconstructed analytical schedule. The outage notes support a
buffering hypothesis, but do not independently prove it.

V11 decision: availability is reported from the outage log (99.365% for the
all-zone online decision path and 99.841% on the gateway-hour denominator).
The paper reports the 146,400 ledger-table rows as observed records, but
withdraws “zero sensor-data loss” and “verified buffering.” A future release
should provide raw sensor, gateway and ledger timestamps plus buffer/replay
events.


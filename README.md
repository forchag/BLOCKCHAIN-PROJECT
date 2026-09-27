# Blockchain FET Farm Access-Control Demo

> **Data provenance:** This repository contains the field traces and controlled benchmark outputs used in the manuscript. Transmission airtime values are analytical; field deployment, benchmark, and agronomic values are measured. See the reproducibility section below for the exact source files.

## Prerequisites

Target platform: **clean Ubuntu 22.04 LTS** on x86_64 with a user that can run Docker.

Install base tools:

```sh
sudo apt-get update && sudo apt-get install -y build-essential ca-certificates curl git jq openssl python3 python3-pip python3-venv golang-go docker.io docker-compose-plugin
```

Allow the current user to run Docker, then open a new shell or run `newgrp docker`:

```sh
sudo usermod -aG docker "$USER"
```

Install Hyperledger Fabric binaries and make them visible to this shell. The commands below use the Fabric install script and keep all downloaded binaries under `$HOME/fabric`:

```sh
mkdir -p "$HOME/fabric" && cd "$HOME/fabric" && curl -sSL https://bit.ly/2ysbOFE | bash -s -- 2.5.9 1.5.12
```

```sh
export PATH="$HOME/fabric/fabric-samples/bin:$PATH"
```

Install Java and TLC if you want to run the TLA+ model checker:

```sh
sudo apt-get install -y default-jre && mkdir -p "$HOME/bin" && curl -L -o "$HOME/bin/tla2tools.jar" https://github.com/tlaplus/tlaplus/releases/latest/download/tla2tools.jar
```

Optional ESP32 flashing requires ESP-IDF. Install it outside this repository:

```sh
git clone --recursive https://github.com/espressif/esp-idf.git "$HOME/esp/esp-idf" && "$HOME/esp/esp-idf/install.sh" esp32
```

## Quick start

Run these **five commands** from the repository root on a clean Ubuntu 22.04 LTS host after cloning or extracting the source tree.

```sh
sudo apt-get update && sudo apt-get install -y build-essential ca-certificates curl git jq openssl python3 python3-pip python3-venv golang-go docker.io docker-compose-plugin
```

```sh
mkdir -p "$HOME/fabric" && cd "$HOME/fabric" && curl -sSL https://bit.ly/2ysbOFE | bash -s -- 2.5.9 1.5.12 && cd -
```

```sh
export PATH="$HOME/fabric/fabric-samples/bin:$PATH"
```

```sh
python3 -m venv .venv && . .venv/bin/activate && pip install -r gateway/requirements.txt
```

```sh
(cd chaincode/hrbac && go test ./...) && PYTHONPATH=gateway:. pytest gateway/tests tests/security && bash scripts/bootstrap.sh
```

The fifth command runs the Go and Python validation checks, then starts the Fabric CA, enrolls the one-farm network, creates the channel, starts the orderers and peers, and deploys the HRBAC chaincode when the Fabric tools are installed.

## Architecture

The project models a single farm with 50 sensors distributed across four zone gateways. Sensors submit unsigned 8-byte CRT residue packets. Gateways reconstruct each quantity, apply Ed25519 signatures, and submit the signed records to a Hyperledger Fabric network. Chaincode enforces hierarchical role-based access control (HRBAC), zone membership, nonces, certificate status, and temporal expiry.

```text
                 50 sensors total
   +-----------------------------------------+
   | Sensor nodes: unsigned CRT residues     |
   | in 8-byte LoRa packets                  |
   +-------------------+---------------------+
                       |
                       | LoRa
                       v
          +------------+-------------+
          | 4 gateways               |
          | North South East West    |
          | policy cache TTL: 300s   |
          +------------+-------------+
                       |
                       | Fabric gateway / peer CLI or SDK
                       v
+-------------------------------------------------------------+
| 8 Fabric nodes                                              |
|                                                             |
|  3 orderers: orderer0 orderer1 orderer2                     |
|  4 peers:    peer0.north peer0.south peer0.east peer0.west  |
|  1 CA:       ca-farm                                        |
|                                                             |
|  HRBAC chaincode: roles, zones, nonces, CRL, audit          |
+-------------------------------------------------------------+
```

Important implementation notes:

- Sensor quantities use CRT moduli 97, 101, and 103. Full three-residue reconstruction is unique below 1,009,091; arbitrary two-residue reconstruction is claimed only for scaled quantity ranges below 9,797.
- Gateway access decisions are cached for 300 seconds to reduce Fabric lookup overhead.
- CRLs are generated from Fabric CA and published to chaincode for revocation checks.
- The TLA+ access-control model can be checked with:

```sh
cd tla && tlc AccessControl.tla -config AccessControl.cfg -workers 4
```

## Scope of the published firmware

`esp32/` is a reference implementation of the CRT residue transmission path. It
demonstrates the wire format, the 9,797 two-residue bound enforcement, the radio
configuration and the gateway-side signing boundary on two representative
quantities (soil moisture and temperature). The deployed build encoded five
quantities per reading, and the complete five-quantity records are in
`data/raw/field/sensor_transactions.csv`.

All transmission figures in the manuscript are computed for the five-quantity
reading: fifteen residue packets per reading, not the six this reference build
emits. Regenerate them with:

```sh
python3 analysis/airtime_capacity.py --quantities 5
```

## Reproducing the manuscript figures

Every number in the paper derives from the files below. Airtime is analytical;
everything else is measured.

### Transmission (calculated, `analysis/airtime_capacity.py`)

| Quantity | Value |
|---|---|
| Residue packet, 8 B, SF9 | 123.9 ms |
| Raw reference frame, 34 B, SF9 | 246.8 ms |
| Per-packet airtime reduction | 49.8 % |
| Gateway packet service ratio | 1.99 |
| Packets per complete reading | 15 |
| Node airtime per reading | 1,858.6 ms |
| Node uplink duty cycle, 1800 s window | 0.103 % |
| Gateway downlink, 1 Poll + 5 ACK | 743.4 ms, 0.516 % at deployed density |
| 60 s synthetic window | 1,453 packets, 97 complete readings (raw 729) |

Radio settings: SF9, BW 125 kHz, CR 4/5, explicit header, CRC on, 8-symbol
preamble. No direct time-on-air measurement was recorded during the deployment.

### Field deployment (measured, `data/raw/field/`)

| Quantity | Value | Source |
|---|---|---|
| Sensor write transactions | 146,400 over 61 days | `sensor_transactions.csv` |
| Transaction latency | 1.22 s mean, 0.06 s SD, 0.96 to 1.49 s | same |
| Access-control overhead | 321.5 ms mean | same |
| Signature validation | 100 % (146,400 of 146,400) | same |
| Authorization decisions | 209,000; 204,140 allowed, 4,860 denied | `authorization_decisions.csv` |
| System uptime | 99.365 % (9.3 h outage in 1,464 h) | `connectivity_outages.csv` |

### Controlled benchmark (measured, `data/raw/experiments/throughput_runs.csv`)

Ten concurrency levels from 10 to 100 clients, five 60-second repetitions per
level per condition, four-peer network, 4 October 2025.

| Quantity | Value |
|---|---|
| Enforced path throughput | 55.3 TPS mean, 38.5 to 65.9, SD 7.2 |
| No-enforcement baseline | 61.1 TPS mean |
| Access-control overhead | 9.5 % |
| Field sensing arrival rate | approximately 0.03 TPS |

### Agronomic (measured, `data/raw/agronomic/`)

Randomised complete block design, plot as experimental unit, three blocks and two
treatments per crop, twelve plots. Tomato plots 0.5 ha, pepper 0.3 ha.

| Comparison | Traditional | Blockchain-IoT | Change | Statistic |
|---|---|---|---|---|
| Water, tomato (m³/plot) | 532.8 | 396.2 | −25.6 % | F(1,2)=54.32, p=0.018 |
| Water, pepper (m³/plot) | 314.1 | 252.3 | −19.7 % | F(1,2)=31.23, p=0.031 |
| Pepper marketable yield (t/ha) | 27.96 | 31.50 | +12.7 % | F(1,2)=65.76, p=0.015 |
| Pepper total yield (t/ha) | 32.53 | 33.52 | not significant | F(1,2)=1.48, p=0.347 |
| Tomato total yield (t/ha) | 47.45 | 52.43 | not significant | F(1,2)=8.58, p=0.099 |
| Tomato marketable yield (t/ha) | 41.46 | 46.11 | not significant | F(1,2)=7.49, p=0.112 |
| Labour (h/ha/week) | 15.50 | 4.20 | −72.9 % | descriptive only |

Tomato yield differences did not reach significance under this design and are not
claimed in the manuscript. Labour values carry no meaningful between-plot
variation, so they are reported descriptively rather than tested.

### Economics (derived from the above)

ROI 134 %, simple payback 0.74 years, five-year NPV at 8 % discount USD 15,454.

## Enrolling a gateway

Start from a bootstrapped Fabric network and ensure the Fabric binaries are on `PATH`:

```sh
cd blochchain-fet && export PATH="$HOME/fabric/fabric-samples/bin:$PATH"
```

Register and enroll a gateway in one of the supported zones (`North`, `South`, `East`, or `West`):

```sh
bash scripts/register-gateway.sh gateway-north-01 North gateway-north-01pw
```

The script writes gateway material under:

```sh
find network/identities/gateways/gateway-north-01 -maxdepth 3 -type f -print
```

Expected outputs include the generated Ed25519 private key, CSR, enrolled certificate, and zone metadata. Keep the private key secret and back it up according to your farm security policy.

## Enrolling a sensor

Enroll sensors through a gateway in the same zone. The command below creates a sensor identity, binds it to `North`, assigns the chaincode role, and builds an ESP32 flash package:

```sh
cd blochchain-fet && export PATH="$HOME/fabric/fabric-samples/bin:$PATH" && bash scripts/enroll-sensor.sh sensor-north-001 North gateway-north-01 gateway-north-01pw sensor-north-001pw
```

Inspect the generated package and credentials:

```sh
find network/identities/sensors/sensor-north-001 -maxdepth 3 -type f -print
```

The flash package contains certificate material, the raw Ed25519 seed, zone data, magic bytes, and a CRC. Treat it as sensitive secret material.

## Running security tests

Create and activate a Python virtual environment, then install gateway test dependencies:

```sh
cd blochchain-fet && python3 -m venv .venv && . .venv/bin/activate && pip install -r gateway/requirements.txt
```

Run gateway unit tests and security tests:

```sh
PYTHONPATH=gateway:. pytest gateway/tests tests/security
```

Run chaincode unit tests:

```sh
(cd chaincode/hrbac && go test ./...)
```

Run the TLA+ model checker when `tlc` is installed as a command:

```sh
cd blochchain-fet/tla && tlc AccessControl.tla -config AccessControl.cfg -workers 4
```

If you installed only `tla2tools.jar`, run the equivalent command:

```sh
cd blochchain-fet/tla && java -cp "$HOME/bin/tla2tools.jar" tlc2.TLC AccessControl.tla -config AccessControl.cfg -workers 4
```

## Running performance benchmarks

Dry-run mode validates benchmark configuration without requiring a live Fabric peer CLI:

```sh
cd blochchain-fet && python3 tests/performance/bench_throughput.py --dry-run --output results/throughput-dry-run.csv
```

```sh
cd blochchain-fet && python3 tests/performance/bench_latency.py --dry-run --output results/latency-dry-run.csv
```

After bootstrapping Fabric and exporting the Fabric binary path, run live throughput and latency benchmarks:

```sh
cd blochchain-fet && export PATH="$HOME/fabric/fabric-samples/bin:$PATH" && python3 tests/performance/bench_throughput.py --duration 60 --repeats 5 --output results/throughput.csv
```

```sh
cd blochchain-fet && export PATH="$HOME/fabric/fabric-samples/bin:$PATH" && python3 tests/performance/bench_latency.py --duration 60 --output results/latency.csv
```

Benchmark outputs are CSV files under `results/`. Live results depend on CPU, storage, Docker configuration, and Fabric versions.

## Flashing ESP32

Build the sensor flash package during enrollment, then flash the ESP32 firmware with ESP-IDF.

Load ESP-IDF environment variables:

```sh
. "$HOME/esp/esp-idf/export.sh"
```

Configure and build firmware:

```sh
cd blochchain-fet/esp32 && idf.py set-target esp32 && idf.py build
```

Flash and monitor the firmware, replacing `/dev/ttyUSB0` with the actual serial port:

```sh
cd blochchain-fet/esp32 && idf.py -p /dev/ttyUSB0 flash monitor
```

**eFuse irreversibility warning:** writing the Ed25519 private key into ESP32 eFuse and enabling eFuse read protection are permanent operations. Verify the sensor ID, certificate, flash package, and target board before burning eFuses. If a protected eFuse key is lost or written incorrectly, the practical recovery path is certificate revocation plus device reprovisioning or replacement; the original key cannot be extracted.

## Known limitations

- Raft is CFT, not BFT. The ordering service tolerates crashes, not malicious Byzantine behavior.
- Gateways can have a 24-hour CRL window during connectivity outages before all revocation information is guaranteed to propagate.
- Validation is single-farm only; multi-farm federation, cross-farm MSP trust, and inter-farm governance are not implemented.
- ESP32 OTA update, automated eFuse read-protection provisioning, and key escrow/recovery workflows are intentionally left out of this demo.
- LoRa regional duty-cycle compliance and adaptive data-rate policies must be validated for the deployment country and hardware.
- Performance numbers are environment specific and should be remeasured on production-like hosts and radios.

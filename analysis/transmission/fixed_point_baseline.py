#!/usr/bin/env python3
"""I compare compact five-quantity frames with the CRT radio packet accounting.

I calculate LoRa airtime. I do not treat these values as field measurements.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from airtime_capacity import airtime_ms


def compare(quantities: int = 5, bytes_per_quantity: int = 2,
            metadata_bytes: int = 0, residue_bytes: int = 8,
            residues_per_quantity: int = 3) -> dict[str, float]:
    if min(quantities, bytes_per_quantity, residue_bytes, residues_per_quantity) <= 0 or metadata_bytes < 0:
        raise ValueError("I require positive quantities and packet sizes, and nonnegative metadata.")
    fixed_bytes = quantities * bytes_per_quantity + metadata_bytes
    crt_packets = quantities * residues_per_quantity
    fixed_airtime = airtime_ms(fixed_bytes)
    crt_airtime = crt_packets * airtime_ms(residue_bytes)
    return {
        "quantities": quantities,
        "fixed_payload_bytes": fixed_bytes,
        "fixed_packets_per_reading": 1,
        "fixed_airtime_ms_per_reading": fixed_airtime,
        "crt_packets_per_reading": crt_packets,
        "crt_airtime_ms_per_reading": crt_airtime,
        "crt_to_fixed_airtime_ratio": crt_airtime / fixed_airtime,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quantities", type=int, default=5)
    parser.add_argument("--bytes-per-quantity", type=int, default=2)
    parser.add_argument("--metadata-bytes", type=int, default=0)
    parser.add_argument("--residue-bytes", type=int, default=8)
    args = parser.parse_args()
    for key, value in compare(args.quantities, args.bytes_per_quantity,
                              args.metadata_bytes, args.residue_bytes).items():
        print(f"{key},{value}")


if __name__ == "__main__":
    main()

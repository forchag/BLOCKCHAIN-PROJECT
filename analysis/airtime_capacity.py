#!/usr/bin/env python3
"""Recompute comparable LoRa airtime and record capacity.

This is an analytical model, not an RF measurement log.
"""

from __future__ import annotations

import argparse
import math


def airtime_ms(payload_bytes: int, *, sf: int = 9, bw_hz: int = 125_000, cr: int = 1,
               preamble: int = 8, crc: bool = True, explicit_header: bool = True) -> float:
    de = 1 if sf >= 11 and bw_hz == 125_000 else 0
    ih = 0 if explicit_header else 1
    crc_bit = 1 if crc else 0
    tsym = (2**sf) / bw_hz
    numerator = 8 * payload_bytes - 4 * sf + 28 + 16 * crc_bit - 20 * ih
    denominator = 4 * (sf - 2 * de)
    payload_symbols = 8 + max(math.ceil(numerator / denominator) * (cr + 4), 0)
    return (preamble + 4.25 + payload_symbols) * tsym * 1000


def summary(window_seconds: float = 60.0, channels: int = 3, quantities: int = 5) -> dict[str, float]:
    raw_ms, residue_ms = airtime_ms(34), airtime_ms(8)
    packet_ratio = raw_ms / residue_ms
    residue_packets = channels * window_seconds * 1000 / residue_ms
    return {
        "raw_34b_ms": raw_ms,
        "residue_8b_ms": residue_ms,
        "per_packet_reduction_percent": (1 - residue_ms / raw_ms) * 100,
        "packet_service_ratio": packet_ratio,
        "raw_records_per_window": channels * window_seconds * 1000 / raw_ms,
        "crt_packets_per_window": residue_packets,
        "crt_complete_records_per_window": residue_packets / (3 * quantities),
        "crt_packets_per_complete_record": 3 * quantities,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--window", type=float, default=60.0)
    parser.add_argument("--channels", type=int, default=3)
    parser.add_argument("--quantities", type=int, default=5)
    args = parser.parse_args()
    for key, value in summary(args.window, args.channels, args.quantities).items():
        print(f"{key},{value:.6f}")

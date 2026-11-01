"""Application-domain scaling used before CRT encoding.

Ranges are expressed as exclusive integer upper bounds. Every bound is at
most 97*101 so an arbitrary residue pair is unique when the bound is enforced.
Each complete sensor reading uses five quantity identifiers (0 through 4),
with three CRT residues per quantity, for fifteen eight-byte LoRa packets.
The configured quantities are soil moisture, temperature, humidity, pH, and
light. Battery status (identifier 5) is an additional supported metadata
quantity and is not included in the five-quantity packet count.

The available archived field CSV has soil moisture and temperature columns;
the five-quantity protocol definition alone does not establish historical
measurements of the remaining quantities.
"""

from dataclasses import dataclass

from crt_decode import SAFE_MAX_VALUE


@dataclass(frozen=True)
class QuantitySpec:
    quantity_id: int
    name: str
    unit: str
    scale: str
    upper_bound: int


QUANTITIES = {
    0: QuantitySpec(0, "soil_moisture", "% VWC", "round(percent * 10)", 1001),
    1: QuantitySpec(1, "temperature", "deg C", "round((celsius + 40) * 10)", 1251),
    2: QuantitySpec(2, "humidity", "% RH", "round(percent * 10)", 1001),
    3: QuantitySpec(3, "ph", "pH", "round(pH * 100)", 1401),
    4: QuantitySpec(4, "light", "10 lux", "round(lux / 10)", 6501),
    5: QuantitySpec(5, "battery", "%", "round(percent * 10)", 1001),
}

assert all(spec.upper_bound <= SAFE_MAX_VALUE for spec in QUANTITIES.values())


def admissible_upper_bound(quantity_id: int) -> int:
    try:
        return QUANTITIES[quantity_id].upper_bound
    except KeyError as exc:
        raise ValueError(f"unknown quantity id: {quantity_id}") from exc

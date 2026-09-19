"""Application-domain scaling used before CRT encoding.

Ranges are expressed as exclusive integer upper bounds. Every bound is at
most 97*101 so an arbitrary residue pair is unique when the bound is enforced.
The archived field CSV contains only soil moisture and temperature; the other
definitions make the wire protocol testable but are not evidence that those
quantities were logged in the deployment.
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

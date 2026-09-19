"""CRT helpers for the reviewer-corrected sensor transport."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

MODULI: tuple[int, int, int] = (97, 101, 103)
MAX_VALUE: int = 97 * 101 * 103
SAFE_MAX_VALUE: int = min(a * b for i, a in enumerate(MODULI) for b in MODULI[i + 1 :])


def encode(value: int, *, require_two_of_three: bool = True) -> dict[int, int]:
    """Encode ``value`` using the paper's three pairwise-coprime moduli.

    The stricter default bound is necessary only when any two residues are
    claimed to reconstruct exactly. Full three-residue reconstruction supports
    values from zero through ``MAX_VALUE - 1``.
    """
    if not isinstance(value, int):
        raise ValueError("value must be an integer")
    upper = SAFE_MAX_VALUE if require_two_of_three else MAX_VALUE
    if value < 0 or value >= upper:
        raise ValueError(f"value must be in range 0..{upper - 1}")
    return {modulus: value % modulus for modulus in MODULI}


def _normalise(residues: Mapping[int, int] | Sequence[object]) -> dict[int, int]:
    if isinstance(residues, Mapping):
        items = residues.items()
    else:
        items = []
        for index, item in enumerate(residues):
            if item is None:
                continue
            if isinstance(item, Mapping):
                modulus = item.get("modulus", item.get("m"))
                residue = item.get("residue", item.get("r"))
            elif isinstance(item, Sequence) and not isinstance(item, (str, bytes)) and len(item) == 2:
                modulus, residue = item
            else:
                modulus, residue = MODULI[index], item
            items.append((modulus, residue))

    result: dict[int, int] = {}
    for modulus, residue in items:
        modulus, residue = int(modulus), int(residue)
        if modulus not in MODULI:
            raise ValueError(f"unsupported CRT modulus: {modulus}")
        if not 0 <= residue < modulus:
            raise ValueError(f"residue for modulus {modulus} must be in range 0..{modulus - 1}")
        result[modulus] = residue
    return result


def decode(
    residues: Mapping[int, int] | Sequence[object],
    *,
    admissible_upper_bound: int | None = None,
) -> int:
    """Reconstruct from two or three residues.

    Three residues are unique below ``MAX_VALUE``. Two residues are accepted
    only when the caller supplies an application bound no larger than the
    received pair's product. This prevents an accidental unconditional
    two-of-three recovery claim.
    """
    normalised = _normalise(residues)
    if len(normalised) < 2:
        raise ValueError("at least two CRT residues are required")

    product = 1
    for modulus in normalised:
        product *= modulus
    if len(normalised) == 2:
        if admissible_upper_bound is None:
            raise ValueError("two-residue decode requires an admissible_upper_bound")
        if not 0 < admissible_upper_bound <= product:
            raise ValueError("admissible_upper_bound exceeds the received modulus product")

    value = sum(
        residue * (product // modulus) * pow(product // modulus, -1, modulus)
        for modulus, residue in normalised.items()
    ) % product
    if admissible_upper_bound is not None and value >= admissible_upper_bound:
        raise ValueError("decoded value is outside the quantity's admissible range")
    return value

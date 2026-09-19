import pytest

from crt_decode import MAX_VALUE, MODULI, SAFE_MAX_VALUE, decode, encode


def test_full_three_residue_round_trip():
    for value in [0, 1, 42, 1234, 2530, 9000]:
        assert decode(encode(value)) == value


def test_paper_worked_example():
    residues = encode(2530)
    assert [residues[m] for m in MODULI] == [8, 5, 58]
    assert decode(residues) == 2530
    assert MAX_VALUE == 1_009_091


def test_two_residues_require_application_bound():
    residues = encode(2530)
    residues.pop(103)
    with pytest.raises(ValueError, match="admissible_upper_bound"):
        decode(residues)
    assert decode(residues, admissible_upper_bound=SAFE_MAX_VALUE) == 2530


def test_invalid_input():
    with pytest.raises(ValueError): encode(-1)
    with pytest.raises(ValueError): encode(SAFE_MAX_VALUE)
    with pytest.raises(ValueError): decode({97: 1})
    with pytest.raises(ValueError): decode({97: 97, 101: 1})

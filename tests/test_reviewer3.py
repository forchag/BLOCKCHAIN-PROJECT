import math

import pytest

from crt_decode import MAX_VALUE, MODULI, SAFE_MAX_VALUE, decode, encode
from lora_rx import LoRaReceiver
from quantity_codec import QUANTITIES
from wire_format import PACKET_LENGTH, ResiduePacket


def airtime_ms(payload_bytes: int) -> float:
    sf, bw, cr, preamble = 9, 125_000, 1, 8
    symbol_ms = (2**sf) / bw * 1000
    payload_symbols = 8 + max(math.ceil((8*payload_bytes - 4*sf + 28 + 16) / (4*sf)) * (cr + 4), 0)
    return (preamble + 4.25 + payload_symbols) * symbol_ms


def test_packet_is_exactly_eight_bytes_and_has_no_signature():
    packet = ResiduePacket(7, 2530, 1, 2, 58)
    assert len(packet.pack()) == PACKET_LENGTH == 8
    assert ResiduePacket.unpack(packet.pack()) == packet
    assert "signature" not in ResiduePacket.__dataclass_fields__


def test_paper_worked_vector_and_full_reconstruction():
    residues = encode(2530)
    assert [residues[m] for m in MODULI] == [8, 5, 58]
    assert decode(residues) == 2530
    assert MAX_VALUE == 1_009_091


def test_two_residue_recovery_requires_bound():
    pair = {97: 8, 101: 5}
    with pytest.raises(ValueError, match="admissible_upper_bound"):
        decode(pair)
    assert decode(pair, admissible_upper_bound=SAFE_MAX_VALUE) == 2530
    with pytest.raises(ValueError, match="exceeds"):
        decode(pair, admissible_upper_bound=SAFE_MAX_VALUE + 1)


def test_each_quantity_range_fits_smallest_pair_product():
    assert SAFE_MAX_VALUE == 9797
    assert all(spec.upper_bound <= SAFE_MAX_VALUE for spec in QUANTITIES.values())


def test_gateway_waits_for_three_residues_by_default():
    receiver = LoRaReceiver(clock=lambda: 0)
    residues = encode(2530)
    for index, modulus in enumerate(MODULI[:2]):
        raw = ResiduePacket(7, 99, 1, index, residues[modulus]).pack()
        assert receiver.process_packet(raw) is None
    reading = receiver.process_packet(ResiduePacket(7, 99, 1, 2, residues[103]).pack())
    assert reading is not None and reading.value == 2530


def test_airtime_model_reproduces_paper_reference_values():
    assert airtime_ms(8) == pytest.approx(123.904, abs=0.001)
    assert airtime_ms(34) == pytest.approx(246.784, abs=0.001)

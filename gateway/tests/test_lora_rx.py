from crt_decode import MODULI, encode
from lora_rx import LoRaReceiver
from wire_format import ResiduePacket


def test_lora_reassembly_waits_for_complete_set():
    receiver = LoRaReceiver(clock=lambda: 0)
    residues = encode(2530)
    for index, modulus in enumerate(MODULI[:2]):
        assert receiver.process_packet(ResiduePacket(1, 2, 1, index, residues[modulus]).pack()) is None
    reading = receiver.process_packet(ResiduePacket(1, 2, 1, 2, residues[103]).pack())
    assert reading is not None
    assert reading.value == 2530
    assert reading.quantity_id == 1


def test_bounded_two_residue_mode_is_explicit():
    receiver = LoRaReceiver(clock=lambda: 0, allow_bounded_two_residue=True)
    residues = encode(900)
    assert receiver.process_packet({"device_id":"1","reading_id":"2","quantity_id":0,"modulus":97,"residue":residues[97]}) is None
    reading = receiver.process_packet({"device_id":"1","reading_id":"2","quantity_id":0,"modulus":101,"residue":residues[101]})
    assert reading is not None and reading.value == 900


def test_lora_incomplete_timeout():
    now=[0.0]; receiver=LoRaReceiver(clock=lambda:now[0],timeout_seconds=60); residues=encode(12)
    receiver.process_packet({"device_id":"1","reading_id":"2","quantity_id":0,"modulus":97,"residue":residues[97]})
    now[0]=61.0; receiver.expire_incomplete()
    assert receiver.process_packet({"device_id":"1","reading_id":"2","quantity_id":0,"modulus":101,"residue":residues[101]}) is None

"""Signatures are gateway-side and never part of the LoRa payload."""

import base64

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from record_signing import GatewaySigner, canonical_record
from wire_format import ResiduePacket


def test_wire_packet_has_no_signature_field():
    assert "signature" not in ResiduePacket.__dataclass_fields__
    assert len(ResiduePacket(42, 7, 1, 0, 8).pack()) == 8


def test_gateway_signature_binds_reconstructed_record():
    signer = GatewaySigner(Ed25519PrivateKey.from_private_bytes(bytes(range(32))))
    signed = signer.attach_signature({"device_id":"42","reading_id":"7","quantity_id":1,"value":2530})
    signature = base64.b64decode(signed["gateway_signature"])
    signer.private_key.public_key().verify(signature, canonical_record(signed))

    tampered = dict(signed); tampered["value"] = 2531
    try:
        signer.private_key.public_key().verify(signature, canonical_record(tampered))
    except Exception:
        pass
    else:
        raise AssertionError("signature accepted a modified reconstructed value")

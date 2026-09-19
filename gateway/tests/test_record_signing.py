import base64

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from record_signing import GatewaySigner, canonical_record


def test_gateway_signs_reconstructed_record_before_submission():
    signer = GatewaySigner(Ed25519PrivateKey.generate())
    signed = signer.attach_signature({"device_id": "7", "reading_id": "99", "quantity_id": 1, "value": 2530})
    signer.private_key.public_key().verify(base64.b64decode(signed["gateway_signature"]), canonical_record(signed))
    assert signed["signature_algorithm"] == "Ed25519"

"""Gateway-side Ed25519 signing for reconstructed records."""

from __future__ import annotations

import base64
import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def canonical_record(record: dict[str, Any]) -> bytes:
    unsigned = {k: v for k, v in record.items() if k not in {"gateway_signature", "gateway_key_id", "signature_algorithm"}}
    return json.dumps(unsigned, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


@dataclass(frozen=True)
class GatewaySigner:
    private_key: Ed25519PrivateKey

    @classmethod
    def from_environment(cls) -> "GatewaySigner":
        pem = os.environ.get("GATEWAY_ED25519_PRIVATE_KEY_PEM")
        path = os.environ.get("GATEWAY_ED25519_PRIVATE_KEY_PATH")
        if not pem and path:
            pem = Path(path).read_text(encoding="utf-8")
        if not pem:
            raise RuntimeError("gateway Ed25519 private key is required before Fabric submission")
        key = serialization.load_pem_private_key(pem.encode(), password=None)
        if not isinstance(key, Ed25519PrivateKey):
            raise RuntimeError("gateway private key must be Ed25519")
        return cls(key)

    @property
    def key_id(self) -> str:
        raw = self.private_key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        return hashlib.sha256(raw).hexdigest()[:16]

    def attach_signature(self, record: dict[str, Any]) -> dict[str, Any]:
        result = dict(record)
        result["signature_algorithm"] = "Ed25519"
        result["gateway_key_id"] = self.key_id
        result["gateway_signature"] = base64.b64encode(self.private_key.sign(canonical_record(result))).decode("ascii")
        return result

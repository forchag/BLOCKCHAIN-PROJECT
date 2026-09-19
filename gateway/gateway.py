"""Executable Python gateway tying LoRa, policy cache, Fabric, and Flask together."""

from __future__ import annotations

import hashlib
import logging
import os
import signal
import threading
import time
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
import struct

from cryptography.hazmat.primitives.asymmetric import ec, ed25519, padding, rsa

from enrollment_server import create_app
from fabric_client import FabricClient
from lora_rx import LoRaReceiver, SensorReading
from policy_cache import PolicyCache
from record_signing import GatewaySigner

LOG = logging.getLogger(__name__)


def load_gateway_zone() -> str:
    zone = os.environ.get("GATEWAY_ZONE")
    if not zone:
        raise RuntimeError("GATEWAY_ZONE environment variable is required")
    return zone


# Must match esp32/main/main.c.
READING_TEMP_BUCKETS = 201
READING_SOIL_SHIFT = 4


def _signature_payload(reading: SensorReading) -> bytes:
    """Reconstruct the exact bytes the firmware hashes before signing.

    The firmware SHA-256-hashes the packed little-endian ``sensor_payload_t``
    (device id u32, reading id u16, raw soil moisture u16, temperature in
    centidegrees i16, timestamp i64) and Ed25519-signs the resulting 32-byte
    digest -- callers of this function must hash its return value before
    verifying, not verify against it directly (see ``verify_signature``
    below). Verifying a different message, for instance an ASCII rendering
    of the decoded value, cannot succeed against that signature: an earlier
    revision of this function did exactly that, which is why signature
    verification never actually constrained anything in the deployment.

    The soil and temperature fields are recovered from the residue-decoded
    value using the same packing the firmware applies, so a mis-decoded
    reading produces different bytes and fails verification.  That is the
    property the transport needs and previously did not have.
    """
    soil_quantised, temp_bucket = divmod(int(reading.value), READING_TEMP_BUCKETS)
    soil_raw = soil_quantised << READING_SOIL_SHIFT
    temperature_centi_c = (temp_bucket * 100) - 5500
    return struct.pack(
        "<IHHhq",
        int(reading.device_id),
        int(reading.reading_id),
        soil_raw,
        temperature_centi_c,
        int(reading.timestamp or 0),
    )


def verify_signature(reading: SensorReading, public_key_pem: str | bytes | None = None,
                     *, allow_unsigned: bool = False) -> bool:
    """Verify a reading signature.

    An unsigned reading is rejected unless ``allow_unsigned`` is set
    explicitly.  This used to fail open, returning True whenever a signature
    was absent, so that the gateway could run without production credentials.
    That default meant an unsigned reading was indistinguishable from a
    verified one, and callers had no way to tell which they had.  Test
    harnesses now opt in.
    """
    if reading.signature is None:
        return allow_unsigned
    key_material = public_key_pem or reading.certificate
    if not key_material:
        return False
    signature = bytes.fromhex(reading.signature) if isinstance(reading.signature, str) else reading.signature
    try:
        public_key = serialization.load_pem_public_key(key_material.encode() if isinstance(key_material, str) else key_material)
        if isinstance(public_key, ed25519.Ed25519PublicKey):
            # The firmware SHA-256-hashes the payload and signs the 32-byte
            # digest (esp32/main/signing.c: wc_Sha256Hash then
            # wc_ed25519_sign_msg), not the payload itself. Verifying the
            # raw payload here would silently fail against every genuine
            # firmware signature while still passing a Python-only round
            # trip that signs what it verifies -- this was true of an
            # earlier revision of this function and went undetected because
            # no test signed a vector the way the firmware actually does.
            digest = hashlib.sha256(_signature_payload(reading)).digest()
            public_key.verify(signature, digest)
        elif isinstance(public_key, ec.EllipticCurvePublicKey):
            public_key.verify(signature, _signature_payload(reading), ec.ECDSA(hashes.SHA256()))
        elif isinstance(public_key, rsa.RSAPublicKey):
            public_key.verify(signature, _signature_payload(reading), padding.PKCS1v15(), hashes.SHA256())
        else:
            return False
        return True
    except (ValueError, InvalidSignature):
        return False


class Gateway:
    def __init__(
        self,
        *,
        zone: str | None = None,
        fabric_client: FabricClient | None = None,
        policy_cache: PolicyCache | None = None,
        lora_receiver: LoRaReceiver | None = None,
    ) -> None:
        self.zone = zone or load_gateway_zone()
        self.fabric_client = fabric_client or FabricClient(signer=GatewaySigner.from_environment())
        self.policy_cache = policy_cache or PolicyCache(ttl_seconds=300)
        self.lora_receiver = lora_receiver or LoRaReceiver()
        self.stop_event = threading.Event()
        self.app = create_app(zone=self.zone, fabric_client=self.fabric_client)
        self._flask_thread: threading.Thread | None = None

    def start_server(self) -> None:
        self._flask_thread = threading.Thread(
            target=lambda: self.app.run(host="127.0.0.1", port=8080, threaded=True, use_reloader=False),
            name="gateway-flask",
            daemon=True,
        )
        self._flask_thread.start()

    def policy_key(self, reading: SensorReading) -> str:
        return f"{reading.device_id}:{reading.zone or self.zone}:submit_reading"

    def handle_revocation(self, episode_id: str | None = None) -> None:
        """Event-driven cache invalidation for a certificate or role
        revocation.

        This is the mechanism the manuscript describes as bounding
        revocation staleness by gossip propagation rather than the cache's
        nominal TTL: "for a reachable gateway the cache is invalidated by
        the CRL event itself". Before this method existed, nothing in this
        codebase actually called ``PolicyCache.invalidate``/
        ``invalidate_all``, so that path had no caller here; a live
        deployment would need this (or an equivalent) wired to its Fabric
        chaincode-event subscription, which is outside this repository's
        scope. This method makes the intended behaviour callable and
        tested, and, given ``episode_id``, logs it so the invalidation
        joins the same episode as the RevokeRole/UpdateCRL calls that
        triggered it.

        Invalidating the whole cache rather than one subject's key is
        deliberate: a cache entry is keyed by device and zone, not by the
        role subject whose revocation caused a decision to be cached, so
        there is no cheaper way to guarantee a revoked subject's cached
        grant is gone without also tracking that association, which this
        cache does not do.
        """
        self.policy_cache.invalidate_all(episode_id)

    def _decision_is_grant(self, decision: Any) -> bool:
        if isinstance(decision, bool):
            return decision
        if isinstance(decision, str):
            return decision.upper() == "GRANT"
        if isinstance(decision, dict):
            return str(decision.get("decision", decision.get("result", ""))).upper() == "GRANT"
        return False

    def handle_reading(self, reading: SensorReading) -> None:
        # LoRa carries only the unsigned 8-byte residue packet. FabricClient
        # signs the reconstructed record with the gateway Ed25519 key
        # immediately before WriteSensorData submission.
        key = self.policy_key(reading)
        decision = self.policy_cache.get(key)
        if decision is None:
            decision = self.fabric_client.check_access(reading.device_id, reading.zone or self.zone)
            self.policy_cache.set(key, decision)
        if self._decision_is_grant(decision):
            # Client-observed round-trip latency for the whole WriteSensorData
            # transaction (submission through commit response), and the
            # rbac_overhead_ms the chaincode itself measured for its internal
            # CheckAccess call -- see chaincode/hrbac/contract.go. Both are
            # genuine measurements, recorded here rather than left blank, so
            # a load-testing/campaign driver reading LIVE_READINGS gets real
            # per-transaction telemetry instead of nothing.
            start = time.perf_counter()
            result = self.fabric_client.submit_sensor_reading(reading)
            latency_ms = (time.perf_counter() - start) * 1000.0
            rbac_overhead_ms = None
            if isinstance(result, dict):
                rbac_overhead_ms = result.get("rbac_overhead_ms")
            payload = reading.to_payload()
            payload["latency_ms"] = round(latency_ms, 1)
            payload["rbac_overhead_ms"] = rbac_overhead_ms
            self.app.config["LIVE_READINGS"].append(payload)
        else:
            LOG.info("discarding reading %s from %s: access denied", reading.reading_id, reading.device_id)

    def run(self) -> None:
        self.start_server()
        self.lora_receiver.start(self.handle_reading)
        while not self.stop_event.is_set():
            reading = self.lora_receiver.next_reading(timeout=0.5)
            if reading:
                self.handle_reading(reading)

    def stop(self, *_args: object) -> None:
        self.stop_event.set()
        self.lora_receiver.stop()


def main() -> None:
    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
    gateway = Gateway()
    signal.signal(signal.SIGTERM, gateway.stop)
    signal.signal(signal.SIGINT, gateway.stop)
    gateway.run()


if __name__ == "__main__":
    main()


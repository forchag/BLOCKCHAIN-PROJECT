"""LoRa residue reception and conservative CRT reassembly."""

from __future__ import annotations

import queue
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable

from crt_decode import MODULI, decode
from quantity_codec import admissible_upper_bound
from wire_format import ResiduePacket

DEFAULT_CHANNELS = (868.100, 868.300, 868.500)
ASSEMBLY_TIMEOUT_SECONDS = 60


@dataclass(frozen=True)
class SensorReading:
    device_id: str
    reading_id: str
    quantity_id: int
    value: int
    zone: str | None = None
    timestamp: float | None = None
    gateway_signature: str | None = None
    residues: dict[int, int] = field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        return {
            "device_id": self.device_id,
            "reading_id": self.reading_id,
            "quantity_id": self.quantity_id,
            "value": self.value,
            "zone": self.zone,
            "timestamp": self.timestamp,
            "gateway_signature": self.gateway_signature,
            "residues": self.residues,
        }


@dataclass
class _Assembly:
    first_seen: float
    residues: dict[int, int] = field(default_factory=dict)


class LoRaReceiver:
    """Default to full three-residue reconstruction.

    ``allow_bounded_two_residue`` is an explicit opt-in. When enabled, the
    quantity-specific bound is supplied to the decoder.
    """

    def __init__(self, channels: Iterable[float] = DEFAULT_CHANNELS, *, timeout_seconds: float = ASSEMBLY_TIMEOUT_SECONDS,
                 packet_sources: Iterable[Callable[[], Any]] | None = None,
                 clock: Callable[[], float] = time.time,
                 allow_bounded_two_residue: bool = False) -> None:
        self.channels = tuple(channels)
        if len(self.channels) != 3:
            raise ValueError("LoRaReceiver must listen on exactly three channels")
        self.timeout_seconds = timeout_seconds
        self.packet_sources = tuple(packet_sources or ())
        self._clock = clock
        self.allow_bounded_two_residue = allow_bounded_two_residue
        self._lock = threading.RLock()
        self._assemblies: dict[tuple[str, str, int], _Assembly] = {}
        self._assembled: set[tuple[str, str, int]] = set()
        self._readings: queue.Queue[SensorReading] = queue.Queue()
        self._stop = threading.Event()
        self._threads: list[threading.Thread] = []

    def start(self, on_reading: Callable[[SensorReading], None] | None = None) -> None:
        for index, source in enumerate(self.packet_sources):
            thread = threading.Thread(target=self._source_loop, args=(source, on_reading), name=f"lora-rx-{index}", daemon=True)
            thread.start(); self._threads.append(thread)

    def stop(self) -> None:
        self._stop.set()
        for thread in self._threads: thread.join(timeout=2)

    def _source_loop(self, source: Callable[[], Any], callback: Callable[[SensorReading], None] | None) -> None:
        while not self._stop.is_set():
            packet = source()
            if packet is None:
                time.sleep(0.05); continue
            reading = self.process_packet(packet)
            if reading and callback: callback(reading)

    def process_packet(self, packet: Any) -> SensorReading | None:
        pkt = self._packet_to_dict(packet)
        device_id, reading_id = str(pkt["device_id"]), str(pkt["reading_id"])
        quantity_id = int(pkt.get("quantity_id", 0))
        key = (device_id, reading_id, quantity_id)
        modulus = self._packet_modulus(pkt)
        residue = int(pkt["residue"])
        with self._lock:
            self._expire_locked()
            if key in self._assembled: return None
            assembly = self._assemblies.setdefault(key, _Assembly(self._clock()))
            assembly.residues[modulus] = residue
            required = 2 if self.allow_bounded_two_residue else 3
            if len(assembly.residues) < required: return None
            bound = admissible_upper_bound(quantity_id) if len(assembly.residues) == 2 else None
            value = decode(assembly.residues, admissible_upper_bound=bound)
            self._assemblies.pop(key, None); self._assembled.add(key)
        reading = SensorReading(device_id, reading_id, quantity_id, value, pkt.get("zone"), pkt.get("timestamp"), residues=dict(assembly.residues))
        self._readings.put(reading)
        return reading

    receive = process_packet
    ingest_packet = process_packet

    def next_reading(self, timeout: float | None = None) -> SensorReading | None:
        try: return self._readings.get(timeout=timeout)
        except queue.Empty: return None

    def expire_incomplete(self) -> None:
        with self._lock: self._expire_locked()

    def _expire_locked(self) -> None:
        now = self._clock()
        for key in [k for k, a in self._assemblies.items() if now - a.first_seen >= self.timeout_seconds]:
            self._assemblies.pop(key, None)

    @staticmethod
    def _packet_to_dict(packet: Any) -> dict[str, Any]:
        if isinstance(packet, bytes):
            decoded = ResiduePacket.unpack(packet)
            return {"device_id": decoded.node_id, "reading_id": decoded.reading_id, "quantity_id": decoded.quantity_id,
                    "modulus_index": decoded.residue_index, "residue": decoded.residue_value}
        if isinstance(packet, dict): return dict(packet)
        if hasattr(packet, "__dict__"): return dict(packet.__dict__)
        raise ValueError("packet must be eight bytes, a mapping, or an object with attributes")

    @staticmethod
    def _packet_modulus(packet: dict[str, Any]) -> int:
        if "modulus" in packet: modulus = int(packet["modulus"])
        elif "modulus_index" in packet: modulus = MODULI[int(packet["modulus_index"])]
        elif "residue_index" in packet: modulus = MODULI[int(packet["residue_index"])]
        elif "channel" in packet:
            channel = packet["channel"]; modulus = MODULI[int(channel)] if isinstance(channel, int) and channel in range(3) else int(channel)
        else: raise ValueError("packet must identify its modulus")
        if modulus not in MODULI: raise ValueError(f"unsupported CRT modulus: {modulus}")
        return modulus

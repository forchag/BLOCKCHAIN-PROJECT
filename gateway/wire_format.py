"""Byte-level LoRa wire format.

Eight bytes, little-endian:
  node_id u16 | reading_id u32 | quantity/residue u8 | residue_value u8

The high nibble identifies the quantity and the low two bits identify the CRT
modulus. No signature is carried over LoRa.
"""

from dataclasses import dataclass
import struct

PACKET = struct.Struct("<HIBB")
PACKET_LENGTH = 8


@dataclass(frozen=True)
class ResiduePacket:
    node_id: int
    reading_id: int
    quantity_id: int
    residue_index: int
    residue_value: int

    def pack(self) -> bytes:
        if not 0 <= self.node_id <= 0xFFFF:
            raise ValueError("node_id must fit u16")
        if not 0 <= self.reading_id <= 0xFFFFFFFF:
            raise ValueError("reading_id must fit u32")
        if not 0 <= self.quantity_id <= 0x0F:
            raise ValueError("quantity_id must fit four bits")
        if not 0 <= self.residue_index < 3:
            raise ValueError("residue_index must be 0, 1, or 2")
        if not 0 <= self.residue_value <= 0xFF:
            raise ValueError("residue_value must fit u8")
        selector = (self.quantity_id << 4) | self.residue_index
        return PACKET.pack(self.node_id, self.reading_id, selector, self.residue_value)

    @classmethod
    def unpack(cls, payload: bytes) -> "ResiduePacket":
        if len(payload) != PACKET_LENGTH:
            raise ValueError(f"LoRa payload must be exactly {PACKET_LENGTH} bytes")
        node_id, reading_id, selector, residue_value = PACKET.unpack(payload)
        if selector & 0x0C:
            raise ValueError("reserved selector bits must be zero")
        return cls(node_id, reading_id, selector >> 4, selector & 0x03, residue_value)


assert PACKET.size == PACKET_LENGTH

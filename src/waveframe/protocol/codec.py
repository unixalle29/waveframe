from struct import calcsize, pack, unpack
from typing import Protocol

from waveframe.protocol.frame import Frame
from waveframe.types import Read


class FrameCodec(Protocol):
    async def decode(self, read: Read) -> Frame | None: ...

    def encode(self, frame: Frame) -> bytes: ...


class StructFrameCodec:
    def __init__(self, header_format: str = "!BH") -> None:
        self._header_format = header_format
        self._header_size = calcsize(header_format)

    def encode(self, frame: Frame) -> bytes:
        if not isinstance(frame.route, int):
            raise TypeError("StructFrameCodec supports only integer routes")
        header = pack(self._header_format, frame.route, len(frame.payload))
        return header + frame.payload

    async def decode(self, read: Read) -> Frame | None:
        header = await read(self._header_size)
        if header is None:
            return None
        route, payload_size = unpack(self._header_format, header)
        payload = await read(payload_size) if payload_size else b""
        if payload is None:
            return None
        return Frame(route, payload)

from asyncio import IncompleteReadError, StreamReader, StreamWriter
from contextlib import suppress


class StreamConnection:
    def __init__(self, reader: StreamReader, writer: StreamWriter) -> None:
        self._reader = reader
        self._writer = writer

    async def close(self) -> None:
        self._writer.close()
        with suppress(ConnectionResetError, BrokenPipeError):
            await self._writer.wait_closed()

    async def write(self, data: bytes) -> None:
        if self._writer.is_closing():
            return

        self._writer.write(data)

        with suppress(ConnectionResetError, BrokenPipeError):
            await self._writer.drain()

    async def read(self, size: int) -> bytes | None:
        with suppress(IncompleteReadError):
            return await self._reader.readexactly(size)

        return None

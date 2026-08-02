import logging
from asyncio import StreamReader, StreamWriter, gather

from waveframe._integrations.asyncio.connection import StreamConnection
from waveframe._integrations.asyncio.registry import ConnectionsRegistry
from waveframe.types import WaveFrameApplication

logger = logging.getLogger(__name__)


class Connections:
    def __init__(
        self,
        app: WaveFrameApplication,
        registry: ConnectionsRegistry | None = None,
    ) -> None:
        self._app = app
        self._registry = ConnectionsRegistry() if registry is None else registry

    async def handle(self, reader: StreamReader, writer: StreamWriter) -> None:
        peername: tuple[str, int] = writer.get_extra_info("peername")
        connection = self._open(peername, reader, writer)
        try:
            await self._app(connection.read, connection.write)
        finally:
            await self.close(peername)

    async def close(self, peername: tuple[str, int]) -> None:
        connection = self._registry.find(peername)
        if connection is None:
            return

        try:
            await connection.close()
        finally:
            self._registry.remove(peername)
            logger.info("WaveFrame connection closed: %s", peername)

    async def close_all(self) -> None:
        await gather(*(self.close(peername) for peername in self._registry.peers()))

    def _open(
        self, peername: tuple[str, int], reader: StreamReader, writer: StreamWriter
    ) -> StreamConnection:
        connection = StreamConnection(reader, writer)
        self._registry.register(peername, connection)
        logger.info("WaveFrame connection opened: %s", peername)
        return connection

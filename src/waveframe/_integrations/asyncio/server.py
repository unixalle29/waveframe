import logging
from asyncio import CancelledError, run, start_server
from os import getpid

from waveframe._integrations.asyncio.connections import Connections
from waveframe.types import WaveFrameApplication

logger = logging.getLogger(__name__)


class AsyncioServer:
    def __init__(self, app: WaveFrameApplication, connections: Connections | None = None) -> None:
        self._app = app
        self._connections = Connections(app) if connections is None else connections

    def run_forever(self, host: str, port: int) -> None:
        run(self.start(host=host, port=port))

    async def graceful_shutdown(self) -> None:
        logger.info("WaveFrame server shutting down")
        await self._connections.close_all()

    async def start(self, host: str, port: int) -> None:
        logger.info("Started server process [%s]", getpid())
        logger.info("Waiting for application startup.")
        await self._app.on_startup()

        try:
            logger.info("Application startup complete.")
            async with await start_server(self._connections.handle, host, port) as server:
                logger.info("WaveFrame running on tcp://%s:%s (Press CTRL+C to quit)", host, port)
                try:
                    await server.serve_forever()
                except CancelledError:
                    logger.info("Shutting down")
                    await self.graceful_shutdown()
                else:
                    await self.graceful_shutdown()
            logger.info("Waiting for application shutdown.")
        finally:
            await self._app.on_shutdown()
            logger.info("Application shutdown complete.")
            logger.info("Finished server process [%s]", getpid())

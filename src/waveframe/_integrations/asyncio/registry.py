from waveframe._integrations.asyncio.connection import StreamConnection


class ConnectionsRegistry:
    def __init__(self) -> None:
        self._connections: dict[tuple[str, int], StreamConnection] = {}

    def register(self, peer: tuple[str, int], conn: StreamConnection) -> None:
        self._connections[peer] = conn

    def remove(self, peer: tuple[str, int]) -> None:
        self._connections.pop(peer, None)

    def find(self, peer: tuple[str, int]) -> StreamConnection | None:
        return self._connections.get(peer)

    def connections(self) -> list[StreamConnection]:
        return list(self._connections.values())

    def peers(self) -> list[tuple[str, int]]:
        return list(self._connections)

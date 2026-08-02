from collections.abc import Awaitable, Callable, Hashable
from typing import Any, Protocol

from waveframe.context import WaveFrameContext
from waveframe.protocol.frame import Frame

FrameHandler = Callable[..., Awaitable[Frame | None]]
ExceptionHandler = Callable[..., Awaitable[Frame | None]]
FrameNext = Callable[[], Awaitable[Frame | None]]
Read = Callable[[int], Awaitable[bytes | None]]
Write = Callable[[bytes], Awaitable[None]]
WaveFrameLifespan = Callable[[], Any]
RouteKey = Hashable


class FrameMiddleware(Protocol):
    def __call__(
        self, frame: Frame, context: WaveFrameContext, call_next: FrameNext
    ) -> Awaitable[Frame | None]: ...


class WaveFrameApplication(Protocol):
    async def __call__(self, read: Read, write: Write) -> None: ...

    async def on_startup(self) -> None: ...

    async def on_shutdown(self) -> None: ...

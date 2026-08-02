from collections.abc import Awaitable, Callable, Hashable
from typing import TYPE_CHECKING, Any, Protocol

from waveframe.context import WaveFrameContext
from waveframe.protocol.frame import Frame
from waveframe.transport import Read, Write

if TYPE_CHECKING:
    from waveframe.app import WaveFrame

FrameHandler = Callable[..., Awaitable[Frame | None]]
ExceptionHandler = Callable[..., Awaitable[Frame | None]]
FrameNext = Callable[[], Awaitable[Frame | None]]
WaveFrameLifespan = Callable[["WaveFrame"], Any]
RouteKey = Hashable


class FrameMiddleware(Protocol):
    def __call__(
        self, frame: Frame, context: WaveFrameContext, call_next: FrameNext
    ) -> Awaitable[Frame | None]: ...


class WaveFrameApplication(Protocol):
    async def __call__(self, read: Read, write: Write) -> None: ...

    async def on_startup(self) -> None: ...

    async def on_shutdown(self) -> None: ...

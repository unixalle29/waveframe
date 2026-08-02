from typing import Final

from dishka import AsyncContainer, Provider, Scope, from_context

from waveframe.context import WaveFrameContext
from waveframe.protocol.frame import Frame
from waveframe.types import FrameNext

CONTAINER_CONTEXT_KEY: Final = "dishka_container"


class WaveFrameProvider(Provider):
    frame = from_context(Frame, scope=Scope.REQUEST)
    context = from_context(WaveFrameContext, scope=Scope.REQUEST)


class DishkaMiddleware:
    def __init__(self, container: AsyncContainer) -> None:
        self._container = container

    async def __call__(
        self,
        frame: Frame,
        context: WaveFrameContext,
        call_next: FrameNext,
    ) -> Frame | None:
        async with self._container(
            context={Frame: frame, WaveFrameContext: context},
            scope=Scope.REQUEST,
        ) as request_container:
            context.set(CONTAINER_CONTEXT_KEY, request_container)
            return await call_next()

from collections.abc import Sequence

from waveframe.context import WaveFrameContext
from waveframe.exception_handlers.registry import ExceptionHandlersRegistry
from waveframe.exceptions import InvalidHandlerResponseError
from waveframe.middleware.frame_pipeline import build_frame_pipeline
from waveframe.protocol.frame import Frame
from waveframe.protocol.frame_sender import FrameSender
from waveframe.routing.router import WaveFrameRouter
from waveframe.types import FrameMiddleware


class FrameDispatcher:
    def __init__(
        self,
        router: WaveFrameRouter,
        middleware: Sequence[FrameMiddleware],
        exception_handlers_registry: ExceptionHandlersRegistry,
    ) -> None:
        self._router = router
        self._middleware = middleware
        self._exception_handlers_registry = exception_handlers_registry

    async def dispatch(self, frame: Frame, context: WaveFrameContext, sender: FrameSender) -> None:
        async def endpoint() -> Frame | None:
            return await self._router.dispatch(frame=frame, context=context, sender=sender)

        try:
            pipeline = build_frame_pipeline(self._middleware, frame, context, endpoint)
            response = await pipeline()
        except Exception as error:
            exception_response = await self._exception_handlers_registry.handle(
                frame=frame, context=context, sender=sender, error=error
            )
            if exception_response is False:
                raise
            if exception_response is not None:
                if not isinstance(exception_response, Frame):
                    raise InvalidHandlerResponseError(type(exception_response)) from error
                await sender.send(exception_response)
            return

        if response is not None:
            if not isinstance(response, Frame):
                raise InvalidHandlerResponseError(type(response))
            await sender.send(response)

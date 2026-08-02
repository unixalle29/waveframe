from waveframe.context import WaveFrameContext
from waveframe.exception_handlers.handler import ExceptionHandlerRoute
from waveframe.protocol.frame import Frame
from waveframe.protocol.frame_sender import FrameSender
from waveframe.types import ExceptionHandler


class ExceptionHandlersRegistry:
    def __init__(self) -> None:
        self._handlers: dict[type[Exception], ExceptionHandlerRoute] = {}

    def add(self, exception_type: type[Exception], handler: ExceptionHandler) -> None:
        self._handlers[exception_type] = ExceptionHandlerRoute.create(handler)

    async def handle(
        self, frame: Frame, context: WaveFrameContext, sender: FrameSender, error: Exception
    ) -> Frame | bool | None:
        handler = self._find(type(error))
        if handler is None:
            return False
        return await handler.handle(frame, context, sender, error)

    def _find(self, exception_type: type[Exception]) -> ExceptionHandlerRoute | None:
        for current_type in exception_type.__mro__:
            handler = self._handlers.get(current_type)
            if handler is not None:
                return handler
        return None

from dataclasses import dataclass

from waveframe.context import WaveFrameContext
from waveframe.exception_handlers.parameters import parse_parameters
from waveframe.protocol.frame import Frame
from waveframe.protocol.frame_sender import FrameSender
from waveframe.types import ExceptionHandler


@dataclass(frozen=True, slots=True)
class ExceptionHandlerRoute:
    endpoint: ExceptionHandler
    payload_parameter: str | None
    context_parameter: str | None
    sender_parameter: str | None
    error_parameter: str | None

    @classmethod
    def create(cls, endpoint: ExceptionHandler) -> "ExceptionHandlerRoute":
        parameters = parse_parameters(endpoint)
        return cls(endpoint, *parameters)

    def _arguments(
        self, frame: Frame, context: WaveFrameContext, sender: FrameSender, error: Exception
    ) -> dict[str, object]:
        arguments: dict[str, object] = {}
        if self.payload_parameter is not None:
            arguments[self.payload_parameter] = frame.payload
        if self.context_parameter is not None:
            arguments[self.context_parameter] = context
        if self.sender_parameter is not None:
            arguments[self.sender_parameter] = sender
        if self.error_parameter is not None:
            arguments[self.error_parameter] = error
        return arguments

    async def handle(
        self, frame: Frame, context: WaveFrameContext, sender: FrameSender, error: Exception
    ) -> Frame | None:
        return await self.endpoint(**self._arguments(frame, context, sender, error))

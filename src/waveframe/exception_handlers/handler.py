from dataclasses import dataclass

from waveframe.exception_handlers.parameters import parse_parameters
from waveframe.protocol.frame import Frame
from waveframe.protocol.frame_sender import FrameSender
from waveframe.state import State
from waveframe.types import ExceptionHandler


@dataclass(frozen=True, slots=True)
class ExceptionHandlerRoute:
    endpoint: ExceptionHandler
    payload_parameter: str | None
    sender_parameter: str | None
    error_parameter: str | None
    state_parameter: str | None

    @classmethod
    def create(cls, endpoint: ExceptionHandler) -> "ExceptionHandlerRoute":
        parameters = parse_parameters(endpoint)
        return cls(endpoint, *parameters)

    def _arguments(
        self, frame: Frame, sender: FrameSender, error: Exception
    ) -> dict[str, object]:
        arguments: dict[str, object] = {}
        if self.payload_parameter is not None:
            arguments[self.payload_parameter] = frame.payload
        if self.sender_parameter is not None:
            arguments[self.sender_parameter] = sender
        if self.error_parameter is not None:
            arguments[self.error_parameter] = error
        return arguments

    async def handle(
        self, frame: Frame, state: State, sender: FrameSender, error: Exception
    ) -> Frame | None:
        arguments = self._arguments(frame, sender, error)
        if self.state_parameter is not None:
            arguments[self.state_parameter] = state
        return await self.endpoint(**arguments)

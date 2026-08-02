from dataclasses import dataclass

from waveframe.protocol.frame import Frame
from waveframe.protocol.frame_sender import FrameSender
from waveframe.routing.parameters import parse_parameters
from waveframe.state import State
from waveframe.types import FrameHandler


@dataclass(frozen=True, slots=True)
class Route:
    endpoint: FrameHandler
    payload_parameter: str | None
    sender_parameter: str | None
    state_parameter: str | None

    @classmethod
    def create(cls, endpoint: FrameHandler) -> "Route":
        return cls(endpoint, *parse_parameters(endpoint))

    async def handle(self, frame: Frame, state: State, sender: FrameSender) -> Frame | None:
        kwargs: dict[str, object] = {}
        if self.payload_parameter is not None:
            kwargs[self.payload_parameter] = frame.payload
        if self.sender_parameter is not None:
            kwargs[self.sender_parameter] = sender
        if self.state_parameter is not None:
            kwargs[self.state_parameter] = state
        return await self.endpoint(**kwargs)

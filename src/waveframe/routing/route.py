from dataclasses import dataclass

from waveframe.context import WaveFrameContext
from waveframe.protocol.frame import Frame
from waveframe.protocol.frame_sender import FrameSender
from waveframe.routing.parameters import parse_parameters
from waveframe.types import FrameHandler


@dataclass(frozen=True, slots=True)
class Route:
    endpoint: FrameHandler
    payload_parameter: str | None
    context_parameter: str | None
    sender_parameter: str | None

    @classmethod
    def create(cls, endpoint: FrameHandler) -> "Route":
        return cls(endpoint, *parse_parameters(endpoint))

    async def handle(self, frame: Frame, context: WaveFrameContext, sender: FrameSender) -> Frame | None:
        kwargs: dict[str, object] = {}
        if self.payload_parameter is not None:
            kwargs[self.payload_parameter] = frame.payload
        if self.context_parameter is not None:
            kwargs[self.context_parameter] = context
        if self.sender_parameter is not None:
            kwargs[self.sender_parameter] = sender
        return await self.endpoint(**kwargs)

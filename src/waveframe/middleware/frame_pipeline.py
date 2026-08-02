from collections.abc import Sequence

from waveframe.protocol.frame import Frame
from waveframe.state import State
from waveframe.types import FrameMiddleware, FrameNext


def build_frame_pipeline(
    middleware: Sequence[FrameMiddleware],
    frame: Frame,
    state: State,
    endpoint: FrameNext,
) -> FrameNext:
    call_next = endpoint
    for current_middleware in reversed(middleware):
        next_handler = call_next

        async def call_current(
            current_middleware: FrameMiddleware = current_middleware,
            next_handler: FrameNext = next_handler,
        ) -> Frame | None:
            return await current_middleware(frame, state, next_handler)

        call_next = call_current
    return call_next

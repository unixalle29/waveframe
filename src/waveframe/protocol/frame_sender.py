from waveframe.protocol.codec import FrameCodec
from waveframe.protocol.frame import Frame
from waveframe.transport import Write


class FrameSender:
    def __init__(self, codec: FrameCodec, write: Write) -> None:
        self._codec = codec
        self._write = write

    async def send(self, frame: Frame) -> None:
        await self._write(self._codec.encode(frame))

from collections.abc import Callable, Sequence
from contextlib import AbstractAsyncContextManager, nullcontext

from waveframe.context import WaveFrameContext
from waveframe.exception_handlers.registry import ExceptionHandlersRegistry
from waveframe.exceptions import ApplicationNotStartedError
from waveframe.protocol.codec import FrameCodec, StructFrameCodec
from waveframe.protocol.frame_sender import FrameSender
from waveframe.routing.dispatcher import FrameDispatcher
from waveframe.routing.router import WaveFrameRouter
from waveframe.transport import Read, Write
from waveframe.types import (
    ExceptionHandler,
    FrameHandler,
    FrameMiddleware,
    RouteKey,
    WaveFrameLifespan,
)


class WaveFrame:
    def __init__(
        self,
        context_factory: Callable[[], WaveFrameContext] = WaveFrameContext,
        lifespan: WaveFrameLifespan | None = None,
        exception_handlers_registry: ExceptionHandlersRegistry | None = None,
        middleware: Sequence[FrameMiddleware] | None = None,
        codec: FrameCodec | None = None,
    ) -> None:
        self.router = WaveFrameRouter()
        self._context_factory = context_factory
        self._frame_middleware = list(middleware or [])
        self._exception_handlers_registry = exception_handlers_registry or ExceptionHandlersRegistry()
        self._codec = codec or StructFrameCodec()
        self._dispatcher = FrameDispatcher(
            self.router, self._frame_middleware, self._exception_handlers_registry
        )
        self._lifespan = lifespan
        self._lifespan_context: AbstractAsyncContextManager[None] | None = None

    async def on_startup(self) -> None:
        self._lifespan_context = self._lifespan(self) if self._lifespan is not None else nullcontext()
        await self._lifespan_context.__aenter__()

    async def on_shutdown(self) -> None:
        if self._lifespan_context is None:
            raise ApplicationNotStartedError
        await self._lifespan_context.__aexit__(None, None, None)
        self._lifespan_context = None

    def on(self, route: RouteKey) -> Callable[[FrameHandler], FrameHandler]:
        return self.router.on(route)

    def include_router(self, router: WaveFrameRouter) -> None:
        self.router.include_router(router)

    def add_middleware(self, middleware: FrameMiddleware) -> None:
        self._frame_middleware.append(middleware)

    def middleware(self, middleware: FrameMiddleware) -> FrameMiddleware:
        self.add_middleware(middleware)
        return middleware

    def add_exception_handler(self, exception_type: type[Exception], handler: ExceptionHandler) -> None:
        self._exception_handlers_registry.add(exception_type, handler)

    def exception_handler(
        self, exception_type: type[Exception]
    ) -> Callable[[ExceptionHandler], ExceptionHandler]:
        def decorator(handler: ExceptionHandler) -> ExceptionHandler:
            self.add_exception_handler(exception_type, handler)
            return handler

        return decorator

    async def __call__(self, read: Read, write: Write) -> None:
        context, sender = self._context_factory(), FrameSender(self._codec, write)
        while frame := await self._codec.decode(read):
            await self._dispatcher.dispatch(frame, context, sender)

from collections.abc import Awaitable, Callable

Read = Callable[[int], Awaitable[bytes | None]]
Write = Callable[[bytes], Awaitable[None]]

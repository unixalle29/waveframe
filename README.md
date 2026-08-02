# Waveframe

Waveframe is an asynchronous framework for framed binary streams. It provides routing, per-connection context, middleware, exception handlers, codecs, and an asyncio TCP adapter without exposing `StreamReader` or `StreamWriter` to application handlers.

## Installation

Install the current version directly from GitHub:

```bash
uv add git+https://github.com/unixalle29/waveframe.git
```

With pip:

```bash
pip install "git+https://github.com/unixalle29/waveframe.git"
```

## Quick Start

The default `StructFrameCodec` uses the `!BH` header format:

```text
1 byte: route
2 bytes: payload length, big-endian
```

```python
from waveframe import AsyncioServer, Frame, WaveFrame


app = WaveFrame()


@app.on(1)
async def ping(payload: bytes) -> Frame:
    assert payload == b"ping"
    return Frame(route=2, payload=b"pong")


server = AsyncioServer(app)
server.run_forever(host="0.0.0.0", port=9092)
```

## Public API

Import the primary API from the package root:

```python
from waveframe import (
    AsyncioServer,
    DishkaMiddleware,
    Frame,
    FrameSender,
    FromDishka,
    State,
    WaveFrame,
    WaveFrameProvider,
    WaveFrameRouter,
    inject,
    setup_dishka,
)
```

Codec APIs are available from `waveframe.protocol`:

```python
from waveframe.protocol import FrameCodec, StructFrameCodec
```

Advanced exception handler configuration is available from:

```python
from waveframe.exception_handlers import ExceptionHandlersRegistry
```

## Frames And Routes

`Frame` is the incoming and outgoing protocol envelope:

```python
Frame(route=1, payload=b"data")
```

`route` may be any hashable value. The default `StructFrameCodec` supports integer routes because its wire header stores the route as a number. A custom codec can use strings, enums, or other hashable route values.

## Handlers

Register a handler with `@app.on(route)` or `@router.on(route)`.

```python
@app.on("ping")
async def ping(payload: bytes) -> Frame:
    return Frame(route="pong", payload=b"ok")
```

Handlers can declare only the values they need. Parameter names are arbitrary; type annotations determine injection.

No parameters:

```python
@app.on("health")
async def health() -> Frame:
    return Frame(route="ok", payload=b"")
```

Payload only:

```python
@app.on("echo")
async def echo(data: bytes) -> Frame:
    return Frame(route="echo", payload=data)
```

State only:

```python
@app.on("session")
async def session(state: State) -> Frame:
    user_id = state.get("user_id", str)
    return Frame(route="session", payload=user_id.encode())
```

Sender only:

```python
@app.on("notification")
async def notification(output: FrameSender) -> None:
    await output.send(Frame(route="event", payload=b"ready"))
```

All supported values:

```python
@app.on("authenticate")
async def authenticate(
    body: bytes,
    state: State,
    output: FrameSender,
) -> Frame:
    state.set("user_id", body.decode())
    await output.send(Frame(route="progress", payload=b"working"))
    return Frame(route="authenticated", payload=b"")
```

Supported handler parameters:

```text
payload: bytes
state: State
sender: FrameSender
```

A handler returns `Frame | None`. A returned frame is sent automatically.

## Sending Multiple Frames

Use `FrameSender` when one incoming frame produces multiple outgoing frames:

```python
@app.on("stream")
async def stream(sender: FrameSender) -> None:
    await sender.send(Frame(route="chunk", payload=b"first"))
    await sender.send(Frame(route="chunk", payload=b"second"))
    await sender.send(Frame(route="done", payload=b""))
```

Returning a frame and sending frames explicitly can be combined:

```python
@app.on("process")
async def process(sender: FrameSender) -> Frame:
    await sender.send(Frame(route="progress", payload=b"working"))
    return Frame(route="complete", payload=b"done")
```

## Routers

Organize handlers with `WaveFrameRouter`:

```python
from waveframe import Frame, WaveFrameRouter


audio_router = WaveFrameRouter()


@audio_router.on("audio")
async def process_audio(payload: bytes) -> Frame:
    await save_audio(payload)
    return Frame(route="ack", payload=b"")
```

```python
app.include_router(audio_router)
```

## State

`app.state` lives for the whole application. Each incoming frame receives a new `State` copied from `app.state`.

```python
@asynccontextmanager
async def lifespan(app: WaveFrame) -> AsyncIterator[None]:
    app.state.set("service", await create_service())
    yield
    await app.state.get("service", Service).close()
```

The frame state receives the same resource reference:

```python
@app.on("work")
async def work(state: State) -> Frame:
    service = state.get("service", Service)
    return Frame(route="done", payload=await service.run())
```

Values written to a frame `State` are local to that frame and are not copied back to `app.state`.

## Middleware

Register middleware with a decorator, a method, or the constructor.

```python
@app.middleware
async def log_frames(
    frame: Frame,
    state: State,
    call_next,
) -> Frame | None:
    print(f"route={frame.route!r}, size={len(frame.payload)}")
    return await call_next()
```

Middleware can return its own `Frame` to replace the handler response, or `None` to suppress an automatic response.

Short-circuit a handler:

```python
@app.middleware
async def require_login(
    frame: Frame,
    state: State,
    call_next,
) -> Frame | None:
    if frame.route != "login":
        state.get("user_id", str)
    return await call_next()
```

Replace a handler response:

```python
@app.middleware
async def replace_response(
    frame: Frame,
    state: State,
    call_next,
) -> Frame | None:
    await call_next()
    return Frame(route="forced", payload=b"response")
```

## Exception Handlers

Register exception handlers with a decorator:

```python
from waveframe.exceptions import UnknownRouteError


@app.exception_handler(UnknownRouteError)
async def unknown_route(error: Exception) -> Frame:
    return Frame(route="error", payload=str(error).encode())
```

An exception handler may request these values:

```text
payload: bytes
state: State
sender: FrameSender
error: Exception
```

It may return one `Frame`, return `None`, or send multiple frames through `FrameSender`.

All exception handler injections:

```python
@app.exception_handler(UnknownRouteError)
async def unknown_route(
    payload: bytes,
    state: State,
    sender: FrameSender,
    error: Exception,
) -> Frame | None:
    await sender.send(Frame(route="log", payload=payload))
    return Frame(route="error", payload=str(error).encode())
```

## Custom Codec

The server transports raw bytes. A codec decodes them into `Frame` objects and encodes outgoing frames back into bytes.

```python
from waveframe import Frame, WaveFrame
from waveframe.protocol import StructFrameCodec


app = WaveFrame(codec=StructFrameCodec("!BH"))
```

Implement `FrameCodec` for another wire protocol:

```python
class CustomCodec:
    async def decode(self, read) -> Frame | None:
        header = await read(2)
        if header is None:
            return None

        route = header[0]
        payload_size = header[1]
        payload = await read(payload_size)
        if payload is None:
            return None

        return Frame(route=route, payload=payload)

    def encode(self, frame: Frame) -> bytes:
        return bytes((int(frame.route), len(frame.payload))) + frame.payload
```

```python
app = WaveFrame(codec=CustomCodec())
```

## Lifespan

```python
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: WaveFrame) -> AsyncIterator[None]:
    resource = await open_resource()
    app.state.set("resource", resource)
    try:
        yield
    finally:
        await app.state.get("resource", Resource).close()


app = WaveFrame(lifespan=lifespan)
```

`AsyncioServer` calls `on_startup()` before accepting connections and `on_shutdown()` after shutdown.

## Dishka

```python
from dishka import AsyncContainer
from waveframe import Frame, FromDishka, WaveFrame, WaveFrameProvider, inject, setup_dishka


app = WaveFrame()
container: AsyncContainer = make_container()
setup_dishka(container, app)


@app.on("audio")
@inject
async def process_audio(
    payload: bytes,
    service: FromDishka[AudioService],
) -> Frame:
    await service.process(payload)
    return Frame(route="ack", payload=b"")
```

`WaveFrameProvider` exposes `Frame` and `State` to Dishka request scope. `setup_dishka()` stores the root container in `app.state`, and opens a Dishka `REQUEST` scope for every incoming frame.

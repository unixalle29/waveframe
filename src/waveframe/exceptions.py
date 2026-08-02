class WaveFrameError(Exception):
    pass


class DuplicateRouteError(WaveFrameError):
    def __init__(self, route: object) -> None:
        super().__init__(f"Route is already registered: {route!r}")


class UnknownRouteError(WaveFrameError):
    def __init__(self, route: object) -> None:
        super().__init__(f"Unknown route: {route!r}")


class InvalidStateValueTypeError(WaveFrameError):
    def __init__(self, key: str, expected_type: type[object]) -> None:
        super().__init__(
            f"WaveFrame state value {key!r} has invalid type; expected {expected_type.__name__}"
        )


class StateValueNotFoundError(WaveFrameError):
    def __init__(self, key: str) -> None:
        super().__init__(f"WaveFrame state value {key!r} was not found")


class InvalidHandlerParameterError(WaveFrameError):
    def __init__(self, parameter_name: str) -> None:
        super().__init__(f"Unsupported handler parameter: {parameter_name}")


class UnsupportedHandlerParameterTypeError(WaveFrameError):
    def __init__(self, parameter_name: str) -> None:
        super().__init__(
            f"Unsupported handler parameter {parameter_name!r}. "
            "Supported annotations: bytes, FrameSender."
        )


class DuplicateHandlerParameterError(WaveFrameError):
    def __init__(self, parameter_type: str) -> None:
        super().__init__(f"A handler can declare only one {parameter_type} parameter")


class ApplicationNotStartedError(WaveFrameError):
    def __init__(self) -> None:
        super().__init__("Application has not started")


class InvalidHandlerResponseError(WaveFrameError):
    def __init__(self, response_type: type[object]) -> None:
        super().__init__(f"Frame handlers must return Frame or None, got {response_type.__name__}")


class DishkaStateNotFoundError(WaveFrameError):
    def __init__(self) -> None:
        super().__init__("WaveFrame state is required for Dishka injection")


class UnsupportedFrameRouteError(WaveFrameError):
    def __init__(self, route_type: type[object]) -> None:
        super().__init__(f"StructFrameCodec supports only integer routes, got {route_type.__name__}")

from inspect import Parameter, signature

from waveframe.exceptions import (
    DuplicateHandlerParameterError,
    InvalidHandlerParameterError,
    UnsupportedHandlerParameterTypeError,
)
from waveframe.protocol.frame_sender import FrameSender
from waveframe.state import State
from waveframe.types import ExceptionHandler


def parse_parameters(
    endpoint: ExceptionHandler,
) -> tuple[str | None, str | None, str | None, str | None]:
    payload_parameter: str | None = None
    sender_parameter: str | None = None
    error_parameter: str | None = None
    state_parameter: str | None = None

    for parameter in signature(endpoint).parameters.values():
        if parameter.kind in (Parameter.VAR_POSITIONAL, Parameter.VAR_KEYWORD):
            raise InvalidHandlerParameterError(parameter.name)

        if parameter.kind not in (Parameter.POSITIONAL_OR_KEYWORD, Parameter.KEYWORD_ONLY):
            raise InvalidHandlerParameterError(parameter.name)

        if parameter.annotation is bytes:
            if payload_parameter is not None:
                raise DuplicateHandlerParameterError("bytes")
            payload_parameter = parameter.name
        elif parameter.annotation is FrameSender:
            if sender_parameter is not None:
                raise DuplicateHandlerParameterError("FrameSender")
            sender_parameter = parameter.name
        elif parameter.annotation is Exception:
            if error_parameter is not None:
                raise DuplicateHandlerParameterError("Exception")
            error_parameter = parameter.name
        elif parameter.annotation is State:
            if state_parameter is not None:
                raise DuplicateHandlerParameterError("State")
            state_parameter = parameter.name
        else:
            raise UnsupportedHandlerParameterTypeError(parameter.name)

    return payload_parameter, sender_parameter, error_parameter, state_parameter

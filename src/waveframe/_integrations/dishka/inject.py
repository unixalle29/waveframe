from collections.abc import Callable
from inspect import Parameter, signature
from typing import Any, ParamSpec, TypeVar

from dishka import AsyncContainer
from dishka.integrations.base import wrap_injection

from waveframe._integrations.dishka.middleware import CONTAINER_CONTEXT_KEY
from waveframe.context import WaveFrameContext

P = ParamSpec("P")
T = TypeVar("T")
_CONTEXT_PARAMETER = Parameter(
    name="__waveframe_context",
    annotation=WaveFrameContext,
    kind=Parameter.KEYWORD_ONLY,
)


def inject(func: Callable[P, T]) -> Callable[P, T]:
    context_parameter = _find_context_parameter(func)
    additional_params = [] if context_parameter is not None else [_CONTEXT_PARAMETER]

    return wrap_injection(
        func=func,
        is_async=True,
        additional_params=additional_params,
        container_getter=lambda _, kwargs: _get_container(kwargs, context_parameter),
    )


def _find_context_parameter(func: Callable[P, T]) -> str | None:
    for parameter in signature(func).parameters.values():
        if parameter.annotation is WaveFrameContext:
            return parameter.name
    return None


def _get_container(kwargs: dict[str, Any], context_parameter: str | None) -> AsyncContainer:
    parameter_name = context_parameter or _CONTEXT_PARAMETER.name
    context = kwargs[parameter_name]
    if not isinstance(context, WaveFrameContext):
        raise TypeError("WaveFrame context is required for Dishka injection")
    return context.get(CONTAINER_CONTEXT_KEY, AsyncContainer)

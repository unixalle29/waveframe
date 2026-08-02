from collections.abc import Callable
from inspect import Parameter, signature
from typing import Any, ParamSpec, TypeVar

from dishka import AsyncContainer
from dishka.integrations.base import wrap_injection

from waveframe._integrations.dishka.middleware import CONTAINER_CONTEXT_KEY
from waveframe.exceptions import DishkaStateNotFoundError
from waveframe.state import State

P = ParamSpec("P")
T = TypeVar("T")
_STATE_PARAMETER = Parameter(
    name="__waveframe_state",
    annotation=State,
    kind=Parameter.KEYWORD_ONLY,
)


def inject(func: Callable[P, T]) -> Callable[P, T]:
    state_parameter = _find_state_parameter(func)
    additional_params = [] if state_parameter is not None else [_STATE_PARAMETER]

    return wrap_injection(
        func=func,
        is_async=True,
        additional_params=additional_params,
        container_getter=lambda _, kwargs: _get_container(kwargs, state_parameter),
    )


def _find_state_parameter(func: Callable[P, T]) -> str | None:
    for parameter in signature(func).parameters.values():
        if parameter.annotation is State:
            return parameter.name
    return None


def _get_container(kwargs: dict[str, Any], state_parameter: str | None) -> AsyncContainer:
    parameter_name = state_parameter or _STATE_PARAMETER.name
    state = kwargs[parameter_name]
    if not isinstance(state, State):
        raise DishkaStateNotFoundError
    return state.get(CONTAINER_CONTEXT_KEY, AsyncContainer)

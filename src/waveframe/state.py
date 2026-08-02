from collections.abc import Mapping
from typing import Any, TypeVar

from waveframe.exceptions import InvalidStateValueTypeError, StateValueNotFoundError

T = TypeVar("T")


class State:
    def __init__(self, values: Mapping[str, Any] | None = None) -> None:
        self._values = dict(values or {})

    def set(self, key: str, value: Any) -> None:
        self._values[key] = value

    def update(self, values: Mapping[str, Any]) -> None:
        self._values.update(values)

    def copy(self) -> "State":
        return State(self._values)

    def get(self, key: str, value_type: type[T]) -> T:
        try:
            value = self._values[key]
        except KeyError as error:
            raise StateValueNotFoundError(key) from error
        if not isinstance(value, value_type):
            raise InvalidStateValueTypeError(key, value_type)
        return value

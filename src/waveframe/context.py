from typing import Any, TypeVar

from waveframe.exceptions import ContextValueNotFoundError, InvalidContextValueTypeError

T = TypeVar("T")


class WaveFrameContext:
    def __init__(self) -> None:
        self._values: dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        self._values[key] = value

    def get(self, key: str, value_type: type[T]) -> T:
        try:
            value = self._values[key]
        except KeyError as error:
            raise ContextValueNotFoundError(key) from error
        if not isinstance(value, value_type):
            raise InvalidContextValueTypeError(key=key, expected_type=value_type)
        return value

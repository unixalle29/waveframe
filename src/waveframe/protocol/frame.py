from collections.abc import Hashable
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Frame:
    route: Hashable
    payload: bytes

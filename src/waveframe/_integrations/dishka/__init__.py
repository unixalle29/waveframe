from dishka import FromDishka

from waveframe._integrations.dishka.inject import inject
from waveframe._integrations.dishka.middleware import DishkaMiddleware, WaveFrameProvider
from waveframe._integrations.dishka.setup import setup_dishka

__all__ = (
    "DishkaMiddleware",
    "FromDishka",
    "WaveFrameProvider",
    "inject",
    "setup_dishka",
)

from dishka import AsyncContainer

from waveframe._integrations.dishka.middleware import DishkaMiddleware
from waveframe.app import WaveFrame


def setup_dishka(container: AsyncContainer, app: WaveFrame) -> None:
    app.add_middleware(DishkaMiddleware(container))

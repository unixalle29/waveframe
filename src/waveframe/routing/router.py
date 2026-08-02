from collections.abc import Callable

from waveframe.exceptions import DuplicateRouteError, UnknownRouteError
from waveframe.protocol.frame import Frame
from waveframe.routing.route import Route
from waveframe.types import FrameHandler, RouteKey


class WaveFrameRouter:
    def __init__(self) -> None:
        self._routes: dict[RouteKey, Route] = {}

    def on(self, route: RouteKey) -> Callable[[FrameHandler], FrameHandler]:
        def decorator(endpoint: FrameHandler) -> FrameHandler:
            self.add_route(route=route, endpoint=endpoint)
            return endpoint

        return decorator

    def add_route(self, route: RouteKey, endpoint: FrameHandler) -> None:
        if route in self._routes:
            raise DuplicateRouteError(route)
        self._routes[route] = Route.create(endpoint)

    def include_router(self, router: "WaveFrameRouter") -> None:
        for route_key, route in router.routes.items():
            if route_key in self._routes:
                raise DuplicateRouteError(route_key)
            self._routes[route_key] = route

    @property
    def routes(self) -> dict[RouteKey, Route]:
        return self._routes.copy()

    def get_route(self, frame: Frame) -> Route:
        route = self._routes.get(frame.route)
        if route is None:
            raise UnknownRouteError(frame.route)
        return route

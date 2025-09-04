from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from ...views.data import Id
from ...views.elements import HtmlElement

if TYPE_CHECKING:
    from ..app import RoutesType
    from ..types import Permissions


class RouteComponentParam:
    def __init__(self, name: str, type: type | None = None):
        self.name = name
        self.type = type

    @property
    def is_children(self) -> bool:
        return self.name == "children"

    @property
    def is_page(self) -> bool:
        return self.name == "page"

    @property
    def is_headers(self) -> bool:
        return self.name == "headers"

    @property
    def is_cookies(self) -> bool:
        return self.name == "cookies"

    @property
    def is_body(self) -> bool:
        return self.name == "body"

    @property
    def is_session(self) -> bool:
        return self.name == "session"

    @property
    def is_query(self) -> bool:
        return self.name == "query"


class RouteComponent:
    def __init__(
        self,
        func: Callable[..., HtmlElement],
        args: list[RouteComponentParam],
        is_async: bool,
        is_root: bool = False,
    ):
        self.func = func
        self.args = args
        self.is_async = is_async

        self.id = Id.from_string(f"{func.__module__}.{func.__name__}", prefix="v")
        self.is_root = is_root
        self.is_layout = func.__name__ == "layout"
        self.is_view = not self.is_layout
        self.is_partial = func.__name__ == "partial"

    def __eq__(self, value: Any) -> bool:
        if not isinstance(value, RouteComponent):
            raise TypeError(f"Cannot compare RouteComponent with {type(value)}")
        return self.id == value.id


class Route:
    def __init__(
        self,
        path: str,
        views: list[RouteComponent],
        action: RouteComponent | None = None,
        permissions: Permissions | None = None,
    ):
        self.path = path
        self.views = views
        self.action = action
        self.permissions = permissions or {}


class MatchedRoute:
    def __init__(self, route: Route, args: dict[str, str] | None = None):
        self.route = route
        self.args = args or {}


class Router:
    def __init__(self, routes: RoutesType):
        self.none_dynamic_routes, self.dynamic_routes = routes

    def match(self, path: str) -> MatchedRoute | None:
        route = self.none_dynamic_routes.get(path, None)
        if route is not None:
            return MatchedRoute(route)

        for pattern, route in self.dynamic_routes:
            match = pattern.match(path)
            if match:
                args = match.groupdict()
                return MatchedRoute(route, args)

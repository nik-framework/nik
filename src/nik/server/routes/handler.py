from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from ..errors import (
    NotFoundError,
    RoutingError,
    error_handler,
)
from ..request import Request
from ..response import Response
from ..types import Scope
from .auth import AuthGuard
from .context import RequestContext
from .renderer import ActionRenderer, ViewRenderer
from .router import Router
from .static import serve_static_file

if TYPE_CHECKING:
    from ..app import Nik
    from ..types import Receive

logger = logging.getLogger(__name__)

ACTION_METHODS = ("post", "put", "patch", "delete")


class RouteHandler:
    def __init__(
        self,
        app: Nik,
        scope: Scope,
        receive: Receive,
    ):
        self.app = app
        self.request = Request(scope, receive)
        self.context = RequestContext(self.request)
        self.router = Router(self.app.routes)
        self.auth = AuthGuard(self.app.authentication)
        self.view_renderer = ViewRenderer(
            context=self.context,
            router=self.router,
        )
        self.action_renderer = ActionRenderer(
            context=self.context,
            router=self.router,
        )

    async def run(
        self,
    ) -> Response:
        try:
            if self.request.method == "get" and self.request.is_static_path:
                return await serve_static_file(project_root=self.app.project_root, path=self.request.path)

            current_route = self.router.match(self.request.path)
            if current_route is None:
                raise NotFoundError(self.request)
            self.auth.authorize(current_route.route, self.context)

            # Previous route header must also be a valid route and the requester should be authorized to access it.
            previous_route = None
            if self.request.is_nik_request and self.request.previous_path:
                previous_route = self.router.match(self.request.previous_path)
                if previous_route is None:
                    raise NotFoundError()
                self.auth.authorize(previous_route.route, self.context)

            if self.request.method in ACTION_METHODS:
                return await self.action_renderer.render(current_route)
            else:
                return await self.view_renderer.render(current_route, previous_route)
        except RoutingError as e:
            if e.request is None:
                e.request = self.request
            return error_handler(e)
        except Exception as e:
            return error_handler(e)

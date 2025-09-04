from __future__ import annotations

from typing import TYPE_CHECKING

from ..authentication.session import Session
from ..errors import ForbiddenError, UnauthorizedError

if TYPE_CHECKING:
    from ..app import AuthenticationGuards
    from ..routes.context import RequestContext
    from ..routes.router import Route


class AuthGuard:
    def __init__(self, guards: AuthenticationGuards):
        self.guards = guards

    def authorize(self, route: Route, context: RequestContext):
        if not route.permissions:
            return

        session = self.get_session(context)
        if session is None:
            raise UnauthorizedError(context.request)

        for perm_key, perm_expected_value in route.permissions.items():
            session_value = getattr(session.data, perm_key, None)
            if session_value is None or session_value != perm_expected_value:
                raise ForbiddenError(context.request)

    def get_session(self, context: RequestContext) -> Session | None:
        if context.session is not None:
            return context.session

        for guard in self.guards:
            data = guard.verify(context.request)
            if data is not None:
                context.session = Session(data)
                return context.session

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...views.context import Page

if TYPE_CHECKING:
    from ..authentication.session import Session
    from ..cookies import Cookies
    from ..request import Request


class RequestContext:
    """
    RequestContext class is basically everything a route component can take as a parameter.
    """

    def __init__(self, request: Request):
        self.request = request
        self.page = Page(path=request.path)
        self.session: Session | None = None

    @property
    def cookies(self) -> Cookies:
        return self.request.cookies

    @property
    def query(self) -> Any:
        return self.request.query

    @property
    async def body(self) -> Any:
        return await self.request.body

from __future__ import annotations

from typing import TYPE_CHECKING, Any, NoReturn, TypedDict

if TYPE_CHECKING:
    from ..request import Request


class ErrorDetails(TypedDict):
    message: str
    path: str | None


class RoutingError(Exception):
    def __init__(self, message: str, request: Request | None = None, actions: dict[str, Any] | None = None):
        super().__init__(message)
        self.message = message
        self.request = request
        self.actions = actions
        self.status = 500


def validation_error(message: str | None = None) -> NoReturn:
    raise BadRequestError(message=message)


class BadRequestError(RoutingError):
    def __init__(
        self,
        request: Request | None = None,
        message: str | None = None,
        errors: list[ErrorDetails] | None = None,
    ):
        super().__init__(message or "Bad Request", request)
        self.status = 400
        self.errors = errors or []


def unauthorized_error(message: str | None = None) -> NoReturn:
    raise UnauthorizedError(message=message)


class UnauthorizedError(RoutingError):
    def __init__(self, request: Request | None = None, message: str | None = None):
        super().__init__(message or "Unauthorized", request)
        self.status = 401


class ForbiddenError(RoutingError):
    def __init__(self, request: Request | None = None, message: str | None = None):
        super().__init__(message or "Forbidden", request)
        self.status = 403


def not_found(message: str | None = None) -> NoReturn:
    raise NotFoundError(message=message)


class NotFoundError(RoutingError):
    def __init__(self, request: Request | None = None, message: str | None = None):
        super().__init__(message or "Not Found", request)
        self.status = 404


class MethodNotAllowedError(RoutingError):
    def __init__(self, request: Request | None = None, message: str | None = None):
        super().__init__(message or "Method Not Allowed", request)
        self.status = 405


class InternalServerError(RoutingError):
    def __init__(self, request: Request | None = None, message: str | None = None):
        super().__init__(message or "Internal Server Error", request)
        self.status = 500

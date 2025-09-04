from __future__ import annotations

from ..response import Response
from .errors import RoutingError
from .views import generic_error_view


def error_handler(error: Exception) -> Response:
    if not isinstance(error, RoutingError):
        raise error

    if error.request and error.request.is_nik_request:
        body = {"actions": error.actions} if error.actions else {}
        return Response.json(body, error.status)

    return Response.html(
        generic_error_view(error.message),
        error.status,
    )

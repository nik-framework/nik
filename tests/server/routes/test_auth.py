from dataclasses import dataclass
from unittest.mock import MagicMock

import pytest
from nik.server.errors import ForbiddenError, UnauthorizedError
from nik.server.request import Request
from nik.server.routes.auth import AuthGuard
from nik.server.routes.context import RequestContext
from nik.server.routes.router import Route


@pytest.fixture
def mock_secure_cookie():
    secure_cookie = MagicMock()
    return secure_cookie


@pytest.fixture
def mock_request():
    request = MagicMock(spec=Request)
    return request


@pytest.fixture
def mock_context(mock_request):
    context = MagicMock(spec=RequestContext)
    context.request = mock_request
    return context


def test_route_without_permissions(mock_context):
    auth_guard = AuthGuard(())
    route = Route("/protected", views=[])

    assert auth_guard.authorize(route, mock_context) is None


def test_request_without_session(mock_context):
    auth_guard = AuthGuard(())
    route = Route("/protected", views=[], permissions={"role": "admin"})

    with pytest.raises(UnauthorizedError):
        mock_context.session = None  # No guards, get_session will return None
        auth_guard.authorize(route, mock_context)


def test_with_invalid_session(mock_secure_cookie, mock_context):
    auth_guard = AuthGuard(guards=(mock_secure_cookie,))
    route = Route("/protected", views=[], permissions={"role": "admin"})

    with pytest.raises(UnauthorizedError):
        mock_context.session = None
        mock_secure_cookie.verify.return_value = None
        auth_guard.authorize(route, mock_context)


def test_insufficient_permissions(mock_secure_cookie, mock_context):
    auth_guard = AuthGuard(guards=(mock_secure_cookie,))
    route = Route("/protected", views=[], permissions={"role": "admin"})

    @dataclass
    class SessionData:
        user_id: str
        role: str

    with pytest.raises(ForbiddenError):
        mock_context.session = None
        mock_secure_cookie.verify.return_value = SessionData(user_id="123", role="user")

        auth_guard.authorize(route, mock_context)

from __future__ import annotations

from pathlib import Path
from typing import cast
from unittest.mock import AsyncMock, MagicMock

import pytest
from nik.server.app import Nik
from nik.server.types import Scope
from tests.utils import FIXTURES_DIR, create_app


@pytest.fixture(autouse=True)
def manage_sys_path(monkeypatch):
    monkeypatch.syspath_prepend(FIXTURES_DIR)


def noop():
    pass  # pragma: no cover


def test_app_initialization_defaults(monkeypatch):
    monkeypatch.setattr("os.getcwd", lambda: "/mock/cwd")
    monkeypatch.setattr(Nik, "_load_routes", lambda self: None)
    monkeypatch.setattr(Nik, "_copy_js_client", lambda self: None)
    app = Nik(environment="test")

    assert app.project_root == "/mock/cwd"
    assert app.authentication == ()


def test_app_initialization_with_params(monkeypatch):
    mock_auth = (MagicMock(),)
    monkeypatch.setattr(Nik, "_load_routes", lambda self: None)
    monkeypatch.setattr(Nik, "_copy_js_client", lambda self: None)
    app = Nik(
        environment="production",
        project_root="/custom/path",
        authentication=mock_auth,
    )

    assert app.environment == "production"
    assert app.project_root == "/custom/path"
    assert app.authentication == mock_auth


async def test_app_call(monkeypatch, tmp_path: Path):
    mock_route_handler = MagicMock()
    mock_response = MagicMock()
    mock_response.send = AsyncMock()
    mock_route_handler.return_value.run = AsyncMock(return_value=mock_response)
    monkeypatch.setattr("nik.server.app.RouteHandler", mock_route_handler)

    app = create_app("test", project_root=tmp_path)
    scope = cast(Scope, {"type": "http"})
    receive = MagicMock()
    send = MagicMock()

    await app(scope, receive, send)

    mock_route_handler.assert_called_once_with(app, scope, receive)
    mock_route_handler.return_value.run.assert_awaited_once()
    mock_response.send.assert_awaited_once_with(send)


async def test_app_call_wrong_scope_type(tmp_path: Path):
    app = create_app("test", project_root=tmp_path)
    with pytest.raises(AssertionError):
        await app(cast(Scope, {"type": "websocket"}), MagicMock(), MagicMock())


def test_route_generation(monkeypatch, tmp_path: Path):
    routes = ({"/": noop}, ())

    mock_generate_routes = MagicMock()
    monkeypatch.setattr("nik.server.app.generate_routes", mock_generate_routes)
    monkeypatch.setattr(Nik, "_import_routes", lambda self: routes)

    app = create_app("production", project_root=tmp_path / "production")
    mock_generate_routes.assert_not_called()
    assert app.routes == routes

    create_app("development", project_root=tmp_path / "development")
    create_app("test", project_root=tmp_path / "test")
    assert mock_generate_routes.call_count == 2


def test_copy_js_client(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(Nik, "_load_routes", lambda self: None)

    cli_path = tmp_path / "public" / "client.js"

    assert not cli_path.is_file()
    create_app("test", project_root=tmp_path)
    assert cli_path.is_file()

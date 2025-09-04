from types import ModuleType
from unittest.mock import MagicMock

import pytest
from nik.server.routes.codegen import (
    COMPONENT_PARAMS,
    ComponentInfo,
    ComponentParameter,
    RouteGenerationError,
)
from nik.views.elements.base import Children

PROJECT_ROOT = "/tmp/project"
ABS_PATH = "/tmp/project/app/routes/home/route.py"


def _create_mock_module(func_name, func_obj):
    mock_module = ModuleType("mock_module")
    if func_name and func_obj:
        setattr(mock_module, func_name, func_obj)
    return mock_module


@pytest.fixture
def mock_importer(monkeypatch):
    mock_spec = MagicMock()
    mock_spec.loader = MagicMock()
    mock_spec.loader.exec_module = MagicMock()

    mock_spec_from_file = MagicMock(return_value=mock_spec)
    mock_module_from_spec = MagicMock()

    monkeypatch.setattr("importlib.util.spec_from_file_location", mock_spec_from_file)
    monkeypatch.setattr("importlib.util.module_from_spec", mock_module_from_spec)

    return mock_spec_from_file, mock_module_from_spec


def test_initialization_and_properties(mock_importer):
    _, mock_module_from_spec = mock_importer

    def view():
        pass  # pragma: no cover

    mock_module_from_spec.return_value = _create_mock_module("view", view)

    info = ComponentInfo(PROJECT_ROOT, ABS_PATH, "view", {}, False)

    assert info.module_dot_path == "app.routes.home.route"
    assert info.import_alias == "app_routes_home_route_view"
    assert info.import_statement == "from app.routes.home.route import view as app_routes_home_route_view"
    assert info.variable_name == "_rc_app_routes_home_route_view"
    assert not info.is_async
    assert info.func == view


def test_parse_function_with_params(mock_importer):
    _, mock_module_from_spec = mock_importer

    async def view(children: Children, page, user_id: int, no_type, query):
        pass  # pragma: no cover

    mock_module_from_spec.return_value = _create_mock_module("view", view)

    dynamic_params = {"user_id": int, "no_type": str}
    info = ComponentInfo(PROJECT_ROOT, ABS_PATH, "view", dynamic_params, False)

    assert info.is_async

    expected_params = [
        ComponentParameter("children", COMPONENT_PARAMS["children"]),
        ComponentParameter("page", COMPONENT_PARAMS["page"]),
        ComponentParameter("user_id", int),
        ComponentParameter("no_type", None),
        ComponentParameter("query", COMPONENT_PARAMS["query"]),
    ]

    for got, expected in zip(info.func_params, expected_params, strict=False):
        assert got.name == expected.name
        assert got.type == expected.type


def test_missing_view_function_raises_error(mock_importer):
    _, mock_module_from_spec = mock_importer
    mock_module_from_spec.return_value = _create_mock_module(None, None)  # Empty module

    with pytest.raises(RouteGenerationError, match="does not have a 'view' function"):
        ComponentInfo(PROJECT_ROOT, ABS_PATH, "view", {}, False)


def test_missing_layout_function_is_allowed(mock_importer):
    _, mock_module_from_spec = mock_importer
    mock_module_from_spec.return_value = _create_mock_module(None, None)

    info = ComponentInfo(PROJECT_ROOT, ABS_PATH, "layout", {}, False)
    assert info.func is None
    assert not info.is_async
    assert info.func_params == []


def test_unrecognized_param_raises_error(mock_importer):
    _, mock_module_from_spec = mock_importer

    def view(unrecognized_param):
        pass  # pragma: no cover

    mock_module_from_spec.return_value = _create_mock_module("view", view)

    with pytest.raises(RouteGenerationError, match="is not a recognized special type"):
        ComponentInfo(PROJECT_ROOT, ABS_PATH, "view", {}, False)


def test_to_python_generation(mock_importer):
    _, mock_module_from_spec = mock_importer

    async def layout(children: Children, page):
        pass  # pragma: no cover

    mock_module_from_spec.return_value = _create_mock_module("layout", layout)

    info = ComponentInfo(PROJECT_ROOT, ABS_PATH, "layout", {}, is_root_layout=True)

    expected_python = (
        "_rc_app_routes_home_route_layout = RouteComponent(\n"
        "    app_routes_home_route_layout,\n"
        '    [RouteComponentParam("children", Children), RouteComponentParam("page", Page)], is_async=True, is_root=True,\n'  # noqa: E501
        ")"
    )
    assert info.to_python() == expected_python


def test_signature_inspection_failure(mock_importer, monkeypatch):
    _, mock_module_from_spec = mock_importer

    def view():
        pass  # pragma: no cover

    mock_module_from_spec.return_value = _create_mock_module("view", view)

    monkeypatch.setattr("inspect.signature", MagicMock(side_effect=ValueError("test error")))

    with pytest.raises(RouteGenerationError, match="Could not inspect signature"):
        ComponentInfo(PROJECT_ROOT, ABS_PATH, "view", {}, False)

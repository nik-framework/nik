from unittest.mock import MagicMock

import pytest
from nik.server.routes.codegen import RouteInfo


@pytest.fixture
def mock_component_info():
    def _create_mock(variable_name, has_func=True):
        mock = MagicMock()
        mock.variable_name = variable_name
        mock.func = MagicMock() if has_func else None
        return mock

    return _create_mock


def test_initialization(mock_component_info):
    view_comp = mock_component_info("view_comp")
    info = RouteInfo(path="/test", view=view_comp)

    assert info.path == "/test"
    assert info.view == view_comp
    assert info.layouts == []
    assert info.action is None
    assert info.partial is None
    assert info.is_dynamic is None
    assert info.permissions is None


def test_initialization_fails_without_view_or_action():
    with pytest.raises(AssertionError, match="At least one of view or action must be present"):
        RouteInfo(path="/test")


def test_to_python_static_route(mock_component_info):
    layout1 = mock_component_info("layout1_comp")
    layout2_no_func = mock_component_info("layout2_comp", has_func=False)  # e.g., layout.py with no layout()
    view = mock_component_info("view_comp")
    action = mock_component_info("action_comp")
    permissions = {"requires_auth": True}

    info = RouteInfo(
        path="/test",
        layouts=[layout1, layout2_no_func],
        view=view,
        action=action,
        is_dynamic=False,
        permissions=permissions,
    )

    expected_python = (
        '    "/test": Route(\n'
        "        \"/test\", [layout1_comp, view_comp], action=action_comp, permissions={'requires_auth': True}\n"
        "    ),"
    )
    assert info.to_python() == expected_python


def test_to_python_dynamic_route(mock_component_info):
    view = mock_component_info("view_comp")
    partial = mock_component_info("partial_comp")

    info = RouteInfo(path="/users/_user_id_", view=view, partial=partial, is_dynamic=True)

    expected_python = (
        "    (\n"
        '        re.compile(r"^/users/(?P<user_id>[^/]+)$"),\n'
        "        Route(\n"
        '            "/users/_user_id_",\n'
        "            [view_comp, partial_comp], action=None, permissions=None,\n"
        "        ),\n"
        "    ),"
    )
    assert info.to_python() == expected_python


def test_to_python_root_route(mock_component_info):
    view = mock_component_info("view_comp")
    info = RouteInfo(path="/", view=view, is_dynamic=False)

    expected_python = '    "/": Route(\n        "/", [view_comp], action=None, permissions=None\n    ),'
    assert info.to_python() == expected_python


def test_to_python_action_only(mock_component_info):
    action = mock_component_info("action_comp")
    info = RouteInfo(path="/submit", action=action, is_dynamic=False)

    expected_python = '    "/submit": Route(\n        "/submit", [], action=action_comp, permissions=None\n    ),'
    assert info.to_python() == expected_python

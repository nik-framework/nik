from pathlib import Path

import pytest
from nik.server.routes.codegen import RouteGenerationError, generate_routes
from tests.utils import FIXTURES_DIR, create_test_project_structure


@pytest.fixture(autouse=True)
def manage_sys_path(tmp_path, monkeypatch):
    app_dir = str(tmp_path)
    monkeypatch.syspath_prepend(app_dir)


def test_generate_routes_basic_structure(tmp_path: Path):
    create_test_project_structure(
        tmp_path,
        {
            "app": {
                "routes": {
                    "layout.py": "layout_with_children",
                    "route.py": "simple_view",  # Root route
                    "users": {
                        "route.py": "simple_view",
                        "_user_id_": {"route.py": "dynamic_view_int"},
                    },
                }
            }
        },
    )

    generate_routes(str(tmp_path))

    generated_file = tmp_path / "app" / "_routesgen.py"
    assert generated_file.exists()
    content = generated_file.read_text()

    snapshot_file = FIXTURES_DIR / "snapshot_basic_structure.py.txt"
    expected_content = snapshot_file.read_text()

    assert content == expected_content


def test_generate_routes_with_permissions(tmp_path: Path):
    create_test_project_structure(
        tmp_path,
        {
            "app": {
                "routes": {
                    "permissions.py": "permissions = {'role': 'user'}",
                    "route.py": "simple_view",
                    "admin": {
                        "permissions.py": "permissions = {'role': 'admin'}",
                        "route.py": "simple_view",
                        "settings": {
                            "permissions.py": "permissions = None",
                            "route.py": "simple_view",
                        },
                    },
                }
            }
        },
    )

    generate_routes(str(tmp_path))
    content = (tmp_path / "app" / "_routesgen.py").read_text()

    snapshot_file = FIXTURES_DIR / "snapshot_with_permissions.py.txt"
    expected_content = snapshot_file.read_text()

    assert content == expected_content


def test_generate_routes_no_routes_dir_raises_error(tmp_path: Path):
    (tmp_path / "app").mkdir()
    with pytest.raises(RouteGenerationError, match="No routes directory found"):
        generate_routes(str(tmp_path))


def test_generate_routes_duplicate_dynamic_param_raises_error(tmp_path: Path):
    create_test_project_structure(
        tmp_path,
        {
            "app": {
                "routes": {
                    "_user_id_": {
                        "route.py": "dynamic_view_str",
                        "_user_id_": {"route.py": "dynamic_view_str"},
                    }
                }
            }
        },
    )
    with pytest.raises(RouteGenerationError, match="Duplicate dynamic parameter 'user_id'"):
        generate_routes(str(tmp_path))

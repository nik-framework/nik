import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from nik.server.app import Nik
from nik.server.authentication.securecookie import SecureCookie

TESTS_DIR = os.path.dirname(__file__)
FIXTURES_DIR = Path(TESTS_DIR) / "fixtures"


def get_header_list(headers: list[tuple[bytes, bytes]], name: str) -> list[bytes]:
    return [v for k, v in headers if k == name.encode("latin-1")]


def create_test_project_structure(base_dir: Path, structure: dict[str, Any]):
    """
    Recursively creates a directory structure with files.
    For file content, if a file exists in the fixtures directory with the
    given name, its content is used. Otherwise, the string content is
    written directly.

    {
        "layout.py": "layout_with_children",  # Uses tests/fixtures/layout_with_children.py
        "permissions.py": "permissions = {}", # Writes the string directly
        "users": {
           "route.py": "simple_view",
           "_id_": {
              "route.py": "dynamic_view_int"
           }
        }
    }
    """
    for name, content in structure.items():
        path = base_dir / name
        if isinstance(content, dict):
            path.mkdir(exist_ok=True)
            create_test_project_structure(path, content)
        else:
            fixture_path = FIXTURES_DIR / f"{content}.py"
            if fixture_path.exists():
                path.write_text(fixture_path.read_text())
            else:
                path.write_text(content)


def create_app(
    env: Literal["production", "development", "test"],
    auth_guards: tuple | None = None,
    project_root: Path | None = None,
) -> Nik:
    if project_root:
        (project_root / "app" / "routes").mkdir(parents=True, exist_ok=True)
        (project_root / "public").mkdir(exist_ok=True)

    return Nik(
        environment=env,
        project_root=str(project_root) if project_root else str(FIXTURES_DIR),
        authentication=auth_guards,
    )


@dataclass
class SessionData:
    user_id: str
    role: str


def get_secure_cookie_obj(cookie_type: str):
    return SecureCookie(
        name=f"nik-{cookie_type}",
        secret=f"some_secret_key_{cookie_type}",
        options={},
        session_data_class=SessionData,
    )

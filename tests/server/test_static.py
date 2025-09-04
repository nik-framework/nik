from pathlib import Path

import pytest
from nik.server.errors import NotFoundError
from nik.server.routes.static import serve_static_file
from tests.utils import get_header_list


@pytest.fixture
def project_with_public_dir(tmp_path: Path) -> str:
    project_root = tmp_path
    public_dir = project_root / "public"
    public_dir.mkdir()
    (public_dir / "test.txt").write_text("hello world")
    (public_dir / "no_ext").write_text("some data")
    (public_dir / "subdir").mkdir()
    (project_root / "secret.txt").write_text("secret data")
    return str(project_root)


async def test_serve_static_file_not_in_public(project_with_public_dir: str):
    with pytest.raises(AssertionError):
        await serve_static_file(project_with_public_dir, "/api/users")


async def test_serve_static_file_success(project_with_public_dir: str):
    response = await serve_static_file(project_with_public_dir, "/public/test.txt")
    assert response is not None
    assert response.status == 200
    assert response.body == b"hello world"
    assert get_header_list(response.raw_headers, "content-type") == [b"text/plain; charset=utf-8"]


async def test_serve_static_file_not_found(project_with_public_dir: str):
    with pytest.raises(NotFoundError):
        await serve_static_file(project_with_public_dir, "/public/nonexistent.txt")


async def test_serve_static_file_is_a_directory(project_with_public_dir: str):
    with pytest.raises(NotFoundError):
        await serve_static_file(project_with_public_dir, "/public/subdir")


async def test_serve_static_file_path_traversal(project_with_public_dir: str):
    with pytest.raises(NotFoundError):
        await serve_static_file(project_with_public_dir, "/public/../secret.txt")


async def test_serve_static_file_unknown_mimetype(project_with_public_dir: str):
    response = await serve_static_file(project_with_public_dir, "/public/no_ext")
    assert response is not None
    assert response.status == 200
    assert response.body == b"some data"
    assert get_header_list(response.raw_headers, "content-type") == [b"application/octet-stream"]

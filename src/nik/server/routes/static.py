from __future__ import annotations

import mimetypes
import os

from ..errors import NotFoundError
from ..response import Response


async def serve_static_file(project_root: str, path: str):
    try:
        assert path.startswith("/public/"), "Invalid static file path"

        base_path = os.path.abspath(os.path.join(project_root, "public"))

        requested_path = path.lstrip("/")
        if requested_path.startswith("public/"):
            requested_path = requested_path[len("public/") :]

        file_path = os.path.normpath(os.path.join(base_path, requested_path))

        if not file_path.startswith(base_path):
            raise NotFoundError()

        with open(file_path, "rb") as file:
            content = file.read()

        content_type, _ = mimetypes.guess_type(path)
        if not content_type:
            content_type = "application/octet-stream"
        elif content_type.startswith("text/"):
            content_type += "; charset=utf-8"

        return Response(content, status=200, headers={"content-type": content_type})
    except (FileNotFoundError, IsADirectoryError) as err:
        raise NotFoundError() from err

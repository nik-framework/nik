from __future__ import annotations

import importlib.util
import os
import shutil
from re import Pattern
from typing import TYPE_CHECKING, Literal, TypeVar

from .routes.codegen import SPECS, generate_routes
from .routes.handler import RouteHandler
from .types import Scope, Send

if TYPE_CHECKING:
    from .authentication.securecookie import SecureCookie
    from .routes.router import Route
    from .types import Receive

    SC = TypeVar("SC", bound=object)

    NoneDynamicRoutesType = dict[str, Route]
    DynamicRoutesType = tuple[tuple[Pattern[str], Route], ...]
    RoutesType = tuple[NoneDynamicRoutesType, DynamicRoutesType]
    AuthenticationGuards = tuple[SecureCookie[SC], ...]


class Nik:
    def __init__(
        self,
        environment: Literal["development", "test", "production"],
        project_root: str | None = None,
        authentication: AuthenticationGuards | None = None,
    ):
        self.environment = environment
        self.authentication = authentication if authentication is not None else ()
        self.project_root = project_root if project_root is not None else os.getcwd()

        self.routes = self._load_routes()
        self._copy_js_client()

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        assert scope["type"] == "http"
        response = await RouteHandler(self, scope, receive).run()
        await response.send(send)

    def _load_routes(self) -> RoutesType:
        if self.environment != "production":
            generate_routes(self.project_root)

        return self._import_routes()

    def _import_routes(self):
        module_name = SPECS["module_name"] + ".py"
        module_path = os.path.join(self.project_root, SPECS["module_base_path_rel"], module_name)
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec is None or not spec.loader:
            raise ImportError(f"Failed to load {module_name}")  # pragma: no cover

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        return module.ROUTES

    def _copy_js_client(self):
        current_dir = os.path.dirname(__file__)
        source = os.path.realpath(os.path.join(current_dir, "..", "views", "client.js"))
        destination = os.path.join(self.project_root, "public", "client.js")

        shutil.copyfile(source, destination)

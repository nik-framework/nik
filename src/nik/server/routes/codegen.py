from __future__ import annotations

import hashlib
import importlib.util
import inspect
import logging
import os
from collections import OrderedDict
from collections.abc import Callable
from types import ModuleType
from typing import Any, Literal

from ...views.context import Page
from ...views.elements.base import Children
from ..authentication.session import Session
from ..cookies import Cookies

logger = logging.getLogger(__name__)

"""When there is a new route component parameter type, it should be added here."""
COMPONENT_PARAMS = {
    "children": Children,
    "page": Page,
    "cookies": Cookies,
    "headers": dict,
    "body": dict,
    "session": Session,
    "query": dict,
}

APP_DIR = "app"
ROUTES_DIR = os.path.join(APP_DIR, "routes")
GEN_ROUTES_DIR = APP_DIR
SPECS = {"module_name": "_routesgen", "module_base_path_rel": GEN_ROUTES_DIR}


class RouteGenerationError(Exception):
    pass


class ComponentParameter:
    def __init__(self, name: str, type_: type | None = None):
        self.name = name
        self.type = type_


class ComponentInfo:
    """
    Represents a single route component (e.g., layout, view, action, partial).

    This class is responsible for introspecting a Python file that defines a route
    component, extracting metadata about the component function (like its parameters
    and whether it's async), and generating the Python code for a `RouteComponent`
    instance that will be used in the auto-generated routes file.

    Attributes
    ----------
        project_root : str
            The absolute path to the project's root directory.
        abs_path : str
            The absolute path to the Python file containing the component.
        component_type : Literal["layout", "view", "action", "partial"]
            The type of component.
        dynamic_params_in_scope : dict[str, type]
            A dictionary of dynamic URL parameters available in the component's scope.
        is_root_layout : bool
            True if this component is the root layout of the application.
        module_dot_path : str
            The Python import path for the module (e.g., 'app.routes.home.route').
        import_alias : str
            A unique alias for importing the component function to avoid name clashes.
        import_statement : str
            The full 'from ... import ... as ...' statement for the component.
        variable_name : str
            The name of the variable that will hold the `RouteComponent` instance
            in the generated code.
        func : Callable | None
            The actual component function object. None if not found.
        is_async : bool
            True if the component function is an async coroutine.
        func_params : list[ComponentParameter]
            A list of parameters for the component function.
    """

    def __init__(
        self,
        project_root: str,
        abs_path: str,
        component_type: Literal["layout", "view", "action", "partial"],
        dynamic_params_in_scope: dict[str, type],
        is_root_layout: bool,
    ):
        self.abs_path = abs_path
        self.project_root = project_root
        self.component_type = component_type
        # TODO: dynamic params should not have the same name as the default arguments like `children`, `page`, etc.
        self.dynamic_params_in_scope = dynamic_params_in_scope
        self.is_root_layout = is_root_layout

        self.module_dot_path = self._get_module_dot_path()
        self.import_alias = f"{self.module_dot_path.replace('.', '_')}_{component_type}"
        self.import_statement = f"from {self.module_dot_path} import {component_type} as {self.import_alias}"
        self.variable_name = f"_rc_{self.import_alias}"

        self.func, self.is_async, self.func_params = self._parse_function()

    def to_python(self) -> str:
        func_params = []
        for param in self.func_params:
            if param.type:
                if param.type == Children:
                    type_name = "Children"
                else:
                    type_name = param.type.__name__ if hasattr(param.type, "__name__") else str(param.type)

                func_params.append(f'RouteComponentParam("{param.name}", {type_name})')
            else:
                func_params.append(f'RouteComponentParam("{param.name}")')

        args = f"[{', '.join(func_params)}]"
        is_async_kwarg = ", is_async=True" if self.is_async else ", is_async=False"
        is_root_kwarg = ", is_root=True" if self.is_root_layout else ""

        return (
            f"{self.variable_name} = RouteComponent(\n    "
            f"{self.import_alias},\n    {args}{is_async_kwarg}{is_root_kwarg},\n)"
        )

    def _get_module_dot_path(self) -> str:
        rel_path = os.path.relpath(self.abs_path, self.project_root)
        return os.path.splitext(rel_path.replace(os.sep, "."))[0]

    def _parse_function(self) -> tuple[Callable | None, bool, list[ComponentParameter]]:
        module = _load_module_from_file(self.abs_path)

        if not hasattr(module, self.component_type):
            if self.component_type == "layout":
                logger.warning(f"Layout file {self.abs_path} does not have a '{self.component_type}' function.")
                return None, False, []  # Allow layout.py without layout function
            else:
                raise RouteGenerationError(
                    f"View file {self.abs_path} does not have a '{self.component_type}' function."
                )

        func_obj: Callable = getattr(module, self.component_type)
        route_comp_parameters = []
        try:
            sig = inspect.signature(func_obj)
            for name, param in sig.parameters.items():
                if name in COMPONENT_PARAMS:
                    route_comp_parameters.append(ComponentParameter(name, COMPONENT_PARAMS[name]))
                elif name in self.dynamic_params_in_scope:
                    route_comp_parameters.append(
                        ComponentParameter(
                            name, param.annotation if param.annotation != inspect.Parameter.empty else None
                        )
                    )
                else:
                    if param.default == inspect.Parameter.empty:
                        raise RouteGenerationError(
                            f"Parameter '{name}' in {self.import_alias} ({self.abs_path}) "
                            f"is not a recognized special type (Children, Page), "
                            f"not found in dynamic URL parameters ({list(self.dynamic_params_in_scope.keys())}), "
                            f"and has no default value."
                        )
        except ValueError as e:
            raise RouteGenerationError(f"Could not inspect signature of {self.import_alias} in {self.abs_path}") from e

        is_async = inspect.iscoroutinefunction(func_obj)
        return func_obj, is_async, route_comp_parameters


class RouteInfo:
    """
    Represents a single route in the application, aggregating its components and metadata.

    This class encapsulates information about a route, including its URL path, associated
    layout, view, action, and partial components, whether it is dynamic (with URL parameters),
    and any permissions. It is used to generate the Python code for a `Route` instance
    in the auto-generated routes file.

    A route must contain at least a view or an action component.

    Attributes
    ----------
        path : str
            The URL path for the route (e.g., '/home' or '/user/_id_').
        layouts : list[ComponentInfo]
            A list of layout components that wrap this route.
        view : ComponentInfo | None
            The view component for rendering the route's content. None if not present.
        action : ComponentInfo | None
            The action component for handling route-specific logic. None if not present.
        partial : ComponentInfo | None
            The partial component for additional rendering. None if not present.
        is_dynamic : bool | None
            True if the route contains dynamic parameters (e.g., _id_ in path).
        permissions : dict[str, Any]
            A dictionary of permissions associated with the route.
    """

    def __init__(
        self,
        path: str,
        layouts: list[ComponentInfo] | None = None,
        view: ComponentInfo | None = None,
        action: ComponentInfo | None = None,
        partial: ComponentInfo | None = None,
        is_dynamic: bool | None = None,
        permissions: dict[str, Any] | None = None,
    ):
        assert view or action, "At least one of view or action must be present"

        self.path = path
        self.view = view
        self.layouts = layouts or []
        self.action = action
        self.partial = partial
        self.is_dynamic = is_dynamic
        self.permissions = permissions

    def to_python(self) -> str:
        view_tree = [lc.variable_name for lc in self.layouts if lc.func]
        if self.view:
            view_tree.append(self.view.variable_name)
        if self.partial:
            view_tree.append(self.partial.variable_name)

        views_tree_arg = f"[{', '.join(view_tree)}]"
        action_kwarg = f", action={self.action.variable_name}" if self.action else ", action=None"
        permissions_kwarg = f", permissions={self.permissions}" if self.permissions else ", permissions=None"

        if self.is_dynamic:
            regex_path = self.path
            for part in self.path.split("/"):
                if part.startswith("_") and part.endswith("_"):
                    param_name = part[1:-1]
                    regex_path = regex_path.replace(part, f"(?P<{param_name}>[^/]+)")

            regex_path = f"^{regex_path}$"

            return (
                f"    (\n"
                f'        re.compile(r"{regex_path}"),\n'
                f"        Route(\n"
                f'            "{self.path}",\n'
                f"            {views_tree_arg}{action_kwarg}{permissions_kwarg},\n"
                f"        ),\n"
                f"    ),"
            )
        else:
            return (
                f'    "{self.path}": Route(\n'
                f'        "{self.path}", {views_tree_arg}{action_kwarg}{permissions_kwarg}\n'
                f"    ),"
            )


def generate_routes(project_root_path: str):
    routes_dir = os.path.join(project_root_path, ROUTES_DIR)
    if not os.path.isdir(routes_dir):
        raise RouteGenerationError(
            f'No routes directory found in "{project_root_path}".'
            f' Make sure "project_root" argument is set correctly'
            f' and routes are placed under "{ROUTES_DIR}" folder.'
        )

    all_components: dict[str, ComponentInfo] = OrderedDict()
    route_infos: list[RouteInfo] = []

    _walk_app_directory(
        current_dir_abs_path=routes_dir,
        project_root=project_root_path,
        current_url_path_parts=[],
        parent_layout_components=[],
        dynamic_params_so_far=OrderedDict(),
        all_components_map=all_components,
        collected_route_infos=route_infos,
        inherited_permissions={},
    )

    import_statements = {
        "from nik.server.routes.router import Route, RouteComponent, RouteComponentParam",
        "from nik.views.elements import Children",
        "from nik.views.context import Page",
        "from nik.server.cookies import Cookies",
        "from nik.server.authentication.session import Session",
        "import re",
    }
    for comp in all_components.values():
        import_statements.add(comp.import_statement)

    route_comp_definitions = []
    for comp in all_components.values():
        route_comp_definitions.append(
            comp.to_python(),
        )

    none_dynamic_routes_str = []
    dynamic_routes_str = []

    for r_info in route_infos:
        if r_info.is_dynamic:
            dynamic_routes_str.append(r_info.to_python())
        else:
            none_dynamic_routes_str.append(r_info.to_python())

    output = [
        "# type: ignore",
        # Q000 is temporary, will be removed in future versions.
        "# ruff: noqa: E501, F401, I001, Q000",
        "",
        "# This file is auto-generated, do not edit it directly.",
        "",
    ]
    output.extend(sorted(import_statements))
    output.extend(["", "", "# RouteComponent definitions"])
    output.extend(route_comp_definitions)

    output.extend(["", "", "_NONE_DYNAMIC_ROUTES = {"])
    output.extend(none_dynamic_routes_str)
    output.extend(["}", ""])

    output.extend(["", "_DYNAMIC_ROUTES = ("])
    output.extend(dynamic_routes_str)
    output.extend([")", "", ""])

    output.append("ROUTES = (_NONE_DYNAMIC_ROUTES, _DYNAMIC_ROUTES)")

    output_dir = os.path.join(project_root_path, GEN_ROUTES_DIR)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_file_path = os.path.join(output_dir, "_routesgen.py")
    new_content = ("\n".join(output) + "\n").encode("utf-8")
    new_hash = hashlib.sha256(new_content).hexdigest()

    existing_hash = None
    if os.path.exists(output_file_path):
        with open(output_file_path, "rb") as f:
            existing_hash = hashlib.sha256(f.read()).hexdigest()

    if new_hash != existing_hash:
        try:
            with open(output_file_path, "wb") as f:
                f.write(new_content)
            logger.info(f"Successfully generated routes code in {output_file_path}")
        except OSError as e:
            raise e
    else:
        logger.info(f"No changes detected in routes, {output_file_path} is up to date.")


def _walk_app_directory(
    current_dir_abs_path: str,
    project_root: str,
    current_url_path_parts: list[str],
    parent_layout_components: list[ComponentInfo],
    dynamic_params_so_far: dict[str, type],
    all_components_map: dict[str, ComponentInfo],
    collected_route_infos: list[RouteInfo],
    inherited_permissions: dict[str, Any],
):
    layouts_for_current_scope = list(parent_layout_components)
    current_permissions_for_scope = dict(inherited_permissions)

    permissions_file_abs_path = os.path.join(current_dir_abs_path, "permissions.py")
    if os.path.exists(permissions_file_abs_path):
        perm_module = _load_module_from_file(permissions_file_abs_path)

        if not hasattr(perm_module, "permissions"):
            raise RouteGenerationError(
                f"Permissions file {permissions_file_abs_path} does not have a 'permissions' variable."
            )

        perms_value = perm_module.permissions

        if perms_value is None:
            # User deliberately marked permissions = None, we don't inherit permissions in this case.
            current_permissions_for_scope = {}
        elif isinstance(perms_value, dict):
            current_permissions_for_scope.update(perms_value)
        else:
            raise RouteGenerationError(
                f"'permissions' variable in {permissions_file_abs_path} must be a dictionary or None."
            )

    layout_file_abs_path = os.path.join(current_dir_abs_path, "layout.py")
    if os.path.exists(layout_file_abs_path):
        layout_module = _load_module_from_file(layout_file_abs_path)

        if not hasattr(layout_module, "layout"):
            raise RouteGenerationError(f"Layout file {layout_file_abs_path} does not have a 'layout' variable.")

        current_dir_layout_comp: ComponentInfo | None = None
        if layout_file_abs_path not in all_components_map:
            is_root_layout_candidate = not parent_layout_components

            instance = ComponentInfo(
                project_root,
                layout_file_abs_path,
                "layout",
                dynamic_params_so_far,
                is_root_layout=is_root_layout_candidate,
            )
            all_components_map[layout_file_abs_path] = instance
            current_dir_layout_comp = instance
        else:
            current_dir_layout_comp = all_components_map[layout_file_abs_path]

        if current_dir_layout_comp and current_dir_layout_comp.func:
            layouts_for_current_scope.append(current_dir_layout_comp)

    route_file_abs_path = os.path.join(current_dir_abs_path, "route.py")
    if os.path.exists(route_file_abs_path):
        module = _load_module_from_file(route_file_abs_path)

        has_view = hasattr(module, "view")
        has_action = hasattr(module, "action")
        has_partial = hasattr(module, "partial")

        if not has_view and not has_action:
            raise RouteGenerationError(f"Route file {route_file_abs_path} must export a 'view' or 'action' function.")

        view_comp = None
        if has_view:
            view_comp = ComponentInfo(
                project_root, route_file_abs_path, "view", dynamic_params_so_far, is_root_layout=False
            )
            if route_file_abs_path not in all_components_map:
                all_components_map[route_file_abs_path] = view_comp

        partial_comp = None
        if has_partial:
            partial_comp = ComponentInfo(
                project_root, route_file_abs_path, "partial", dynamic_params_so_far, is_root_layout=False
            )
            all_components_map[route_file_abs_path + "_partial"] = partial_comp

        action_comp = None
        if has_action:
            action_comp = ComponentInfo(
                project_root, route_file_abs_path, "action", dynamic_params_so_far, is_root_layout=False
            )
            all_components_map[route_file_abs_path + "_action"] = action_comp

        route_path = "/" + "/".join(current_url_path_parts) if current_url_path_parts else "/"
        if current_dir_abs_path == os.path.join(project_root, APP_DIR) and not current_url_path_parts:
            route_path = "/"

        is_dynamic_route_accurate = any(p.startswith("_") and p.endswith("_") for p in current_url_path_parts)

        collected_route_infos.append(
            RouteInfo(
                route_path,
                layouts_for_current_scope,
                view_comp,
                action_comp,
                partial_comp,
                is_dynamic_route_accurate,
                current_permissions_for_scope,
            )
        )

    excluded_items = {"__pycache__", ".DS_Store"}

    for item_name in sorted(os.listdir(current_dir_abs_path)):
        if item_name in excluded_items or item_name.startswith("."):
            continue

        item_abs_path = os.path.join(current_dir_abs_path, item_name)
        if os.path.isdir(item_abs_path):
            new_dynamic_params = OrderedDict(dynamic_params_so_far)
            url_part = item_name

            if item_name.startswith("_") and item_name.endswith("_") and len(item_name) > 2:
                param_name = item_name[1:-1]
                if param_name in new_dynamic_params:
                    raise RouteGenerationError(
                        f"Duplicate dynamic parameter '{param_name}' in path near {item_abs_path}. "
                        f"Existing params: {list(new_dynamic_params.keys())}"
                    )
                new_dynamic_params[param_name] = str

            _walk_app_directory(
                item_abs_path,
                project_root,
                current_url_path_parts + [url_part],
                layouts_for_current_scope,
                new_dynamic_params,
                all_components_map,
                collected_route_infos,
                current_permissions_for_scope,
            )


def _load_module_from_file(abs_path: str) -> ModuleType:
    """Load layout, route, or permissions modules."""
    module_name = os.path.splitext(os.path.basename(abs_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, abs_path)
    if not spec or not spec.loader:
        raise RouteGenerationError(f'Could not create "{module_name}" module spec for "{abs_path}"')

    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        raise RouteGenerationError(f'Could not import module "{module_name}" from "{abs_path}"') from e

    return module

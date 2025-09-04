from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...utils.string import to_json
from ...views.context import ViewContext
from ...views.elements import Fragment, HtmlElement, Script
from ..errors import MethodNotAllowedError, RoutingError
from ..response import Response

if TYPE_CHECKING:
    from ...views.elements import Children
    from .context import RequestContext
    from .router import MatchedRoute, RouteComponent, Router


class BaseRenderer:
    def __init__(
        self,
        context: RequestContext,
        router: Router,
    ):
        self.context = context
        self.router = router

    async def _get_route_component_kwargs(
        self,
        route_component: RouteComponent,
        children: Children | None = None,
        route_args: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = {}
        for arg in route_component.args:
            if arg.is_children:
                kwargs[arg.name] = children
            elif arg.is_page:
                kwargs[arg.name] = self.context.page
            elif arg.is_cookies:
                kwargs[arg.name] = self.context.cookies
            elif arg.is_query:
                kwargs[arg.name] = self.context.query
            elif arg.is_body:
                kwargs[arg.name] = await self.context.body
            elif arg.is_session:
                kwargs[arg.name] = self.context.session
            elif route_args and arg.name in route_args:
                kwargs[arg.name] = route_args[arg.name]
            else:
                raise ValueError(
                    f"Unsupported argument '{arg.name}' for route component "
                    f"'{route_component.func.__module__}.{route_component.func.__name__}'"
                )
        return kwargs


class ViewRenderer(BaseRenderer):
    async def render(self, current_route: MatchedRoute, previous_route: MatchedRoute | None = None) -> Response:
        """
        Determines the rendering strategy, renders the necessary components,
        and returns a complete Response object.
        """
        views, replaces = self._calculate_render_strategy(current_route, previous_route)

        final_view = None
        actions = {}

        for rc in reversed(views):
            final_view = await self._execute_view(
                route_component=rc,
                actions=actions,
                children=final_view,
                route_args=current_route.args,
            )

        assert final_view, "Rendering resulted in an empty view."

        if self.context.request.is_nik_request:
            assert replaces, "Rendering resulted in no view to replace."
            return Response.json(
                {
                    "replaces": replaces,
                    "view": final_view.render(),
                    "actions": actions,
                },
                cookies=self.context.request.cookies,
            )
        else:
            final_view.add_child(Script(children=[f"window.__nik.run({to_json(actions)});"]))
            return Response.html(
                final_view.render(),
                cookies=self.context.request.cookies,
            )

    def _calculate_render_strategy(
        self, current_route: MatchedRoute, previous_route: MatchedRoute | None = None
    ) -> tuple[list[RouteComponent], str | None]:
        """
        Determines which views to render and what element to replace for partial UI updates.
        """
        if self.context.request.is_form_request:
            return current_route.route.views, None

        replaces = None

        if previous_route:
            if self.context.request.path == self.context.request.previous_path:
                views = [v for v in current_route.route.views if not v.is_layout]
                assert views, "No views found in the current route for internal request"
                last_view = views[-1]
                if self.context.request.is_partial_request:
                    assert len(views) > 1, "There should be at least two views to replace"
                    if last_view.is_partial:
                        replaces = str(views[-1].id)
                        views = [last_view]
                    else:
                        raise Exception(f'Last view must be a partial function "{last_view}"')
                else:
                    if last_view.is_partial:
                        assert len(views) > 1, "There should be at least two views to replace"
                        replaces = str(views[-2].id)
                    else:
                        replaces = str(views[-1].id)
            else:
                views = [v for v in current_route.route.views if v not in previous_route.route.views]
                for pv in previous_route.route.views:
                    if not pv.is_root and pv not in current_route.route.views:
                        replaces = str(pv.id)
                        break
            if not replaces:
                raise ValueError("Could not find a view to replace in the previous route")
        else:
            views = current_route.route.views

        return views, replaces

    async def _execute_view(
        self,
        route_component: RouteComponent,
        actions: dict,
        children: Children | None = None,
        route_args: dict | None = None,
    ) -> HtmlElement:  # FIXME: Return type is not only HtmlElement
        """Renders a single RouteComponent."""

        with ViewContext(page=self.context.page) as ctx:
            view_func_kwargs = await self._get_route_component_kwargs(
                route_component,
                children=children,
                route_args=route_args,
            )

            if route_component.is_async:
                result = await route_component.func(**view_func_kwargs)  # type: ignore
            else:
                result = route_component.func(**view_func_kwargs)
                assert isinstance(result, HtmlElement), "Views must return an HtmlElement"

            actions[str(route_component.id)] = ctx.get_actions()

            if route_component.is_root:
                return result

            return Fragment(id=route_component.id, children=result)


class ActionRenderer(BaseRenderer):
    async def render(self, matched_route: MatchedRoute) -> Response:
        """
        Renders the route modules that has an action function defined.
        """
        if matched_route.route.action is None:
            raise MethodNotAllowedError(self.context.request)

        result = await self._execute_action(matched_route)
        if isinstance(result, Response):
            return result

        return Response.json(
            result,
            cookies=self.context.request.cookies,
        )

    async def _execute_action(
        self,
        matched_route: MatchedRoute,
    ):
        with ViewContext(page=self.context.page) as ctx:
            assert matched_route.route.action, "No action defined for the matched route"

            view_func_kwargs = await self._get_route_component_kwargs(
                matched_route.route.action,
                route_args=matched_route.args,
            )

            try:
                if matched_route.route.action.is_async:
                    result = await matched_route.route.action.func(**view_func_kwargs)  # type: ignore
                else:
                    result = matched_route.route.action.func(**view_func_kwargs)
            except RoutingError as e:
                e.actions = {str(matched_route.route.action.id): ctx.get_actions()}
                raise e

            if isinstance(result, Response):
                return result
            else:
                return {"actions": {str(matched_route.route.action.id): ctx.get_actions()}}

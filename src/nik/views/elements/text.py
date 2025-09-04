from __future__ import annotations

from typing import TYPE_CHECKING

from ..actions import RegisterObservable, SubscribeObservable
from ..context import ViewContext
from ..data import State, When
from .base import Element, ToggleClass, classes_to_list, get_id

if TYPE_CHECKING:
    from .base import Children, Classes, IdArg


class P(Element):
    def __init__(
        self,
        *args: Children,
        id: IdArg = None,
        classes: Classes | None = None,
        children: Children | None = None,
        toggle_class: When | None = None,
        show: When | bool | None = None,
        **kwargs,
    ):
        super().__init__(
            *args,
            tag="p",
            id=id,
            classes=classes,
            children=children,
            toggle_class=toggle_class,
            show=show,
            **kwargs,
        )


class Del(Element):
    def __init__(
        self,
        *args: Children,
        id: IdArg = None,
        classes: Classes | None = None,
        children: Children | None = None,
        toggle_class: When | None = None,
        show: When | bool | None = None,
        **kwargs,
    ):
        super().__init__(
            *args,
            tag="del",
            id=id,
            classes=classes,
            children=children,
            toggle_class=toggle_class,
            show=show,
            **kwargs,
        )


class Ins(Element):
    def __init__(
        self,
        *args: Children,
        id: IdArg = None,
        classes: Classes | None = None,
        children: Children | None = None,
        toggle_class: When | None = None,
        show: When | bool | None = None,
        **kwargs,
    ):
        super().__init__(
            *args,
            tag="ins",
            id=id,
            classes=classes,
            children=children,
            toggle_class=toggle_class,
            show=show,
            **kwargs,
        )


class Pre(Element):
    def __init__(
        self,
        *args: Children,
        id: IdArg = None,
        classes: Classes | None = None,
        children: Children | None = None,
        toggle_class: When | None = None,
        show: When | bool | None = None,
        **kwargs,
    ):
        super().__init__(
            *args,
            tag="pre",
            id=id,
            classes=classes,
            children=children,
            toggle_class=toggle_class,
            show=show,
            **kwargs,
        )


class Blockquote(Element):
    def __init__(
        self,
        *args: Children,
        id: IdArg = None,
        classes: Classes | None = None,
        children: Children | None = None,
        toggle_class: When | None = None,
        show: When | bool | None = None,
        **kwargs,
    ):
        super().__init__(
            *args,
            tag="blockquote",
            id=id,
            classes=classes,
            children=children,
            toggle_class=toggle_class,
            show=show,
            **kwargs,
        )


class Br(Element):
    def __init__(
        self,
        *args: Children,
        id: IdArg = None,
        classes: Classes | None = None,
        toggle_class: When | None = None,
        show: When | bool | None = None,
        **kwargs,
    ):
        super().__init__(
            *args,
            tag="br",
            is_void=True,
            id=id,
            classes=classes,
            children=None,
            toggle_class=toggle_class,
            show=show,
            **kwargs,
        )


class Hr(Element):
    def __init__(
        self,
        *args: Children,
        id: IdArg = None,
        classes: Classes | None = None,
        toggle_class: When | None = None,
        show: When | bool | None = None,
        **kwargs,
    ):
        super().__init__(
            *args,
            tag="hr",
            is_void=True,
            id=id,
            classes=classes,
            children=None,
            toggle_class=toggle_class,
            show=show,
            **kwargs,
        )


class Ul(Element):
    def __init__(
        self,
        *args: Children,
        id: IdArg = None,
        classes: Classes | None = None,
        children: Children | None = None,
        toggle_class: When | None = None,
        show: When | bool | None = None,
        **kwargs,
    ):
        super().__init__(
            *args,
            tag="ul",
            id=id,
            classes=classes,
            children=children,
            toggle_class=toggle_class,
            show=show,
            **kwargs,
        )


class Li(Element):
    def __init__(
        self,
        *args: Children,
        id: IdArg = None,
        classes: Classes | None = None,
        children: Children | None = None,
        toggle_class: When | None = None,
        show: When | bool | None = None,
        **kwargs,
    ):
        super().__init__(
            *args,
            tag="li",
            id=id,
            classes=classes,
            children=children,
            toggle_class=toggle_class,
            show=show,
            **kwargs,
        )


class Div(Element):
    def __init__(
        self,
        *args: Children,
        id: IdArg = None,
        classes: Classes | None = None,
        children: Children | None = None,
        toggle_class: When | None = None,
        show: When | bool | None = None,
        **kwargs,
    ):
        super().__init__(
            *args,
            tag="div",
            id=id,
            classes=classes,
            children=children,
            toggle_class=toggle_class,
            show=show,
            **kwargs,
        )


class A(Element):
    def __init__(
        self,
        *args: Children,
        href: str | None = None,
        active_class: str | None = None,
        controlled: bool = True,
        id: IdArg = None,
        classes: Classes | None = None,
        children: Children | None = None,
        toggle_class: When | None = None,
        show: When | bool | None = None,
        **kwargs,
    ):
        self.active_class = active_class
        self.controlled = controlled

        if active_class:
            if page := ViewContext.get_current().page:
                if page.path == href:
                    classes = classes_to_list(classes) if classes else []
                    classes.append(active_class)

        should_generate_id = bool(active_class)
        id = get_id(id, should_generate_id)

        if not self.controlled:
            kwargs["data-controlled"] = "0"

        super().__init__(
            *args,
            tag="a",
            href=href,
            id=id,
            classes=classes,
            children=children,
            toggle_class=toggle_class,
            show=show,
            **kwargs,
        )

        if active_class:
            assert self.id, "active_class parameter given without an id"

            nav_state = State("page_nav_state", href, key="page_nav_state")
            ViewContext.get_current().add_action(RegisterObservable(nav_state))
            ViewContext.get_current().add_action(
                SubscribeObservable(nav_state, ToggleClass(self.id, When(nav_state, equal_to=href, do=active_class)))
            )


class Strong(Element):
    def __init__(
        self,
        *args: Children,
        id: IdArg = None,
        classes: Classes | None = None,
        children: Children | None = None,
        toggle_class: When | None = None,
        show: When | bool | None = None,
        **kwargs,
    ):
        super().__init__(
            *args,
            tag="strong",
            id=id,
            classes=classes,
            children=children,
            toggle_class=toggle_class,
            show=show,
            **kwargs,
        )


class Em(Element):
    def __init__(
        self,
        *args: Children,
        id: IdArg = None,
        classes: Classes | None = None,
        children: Children | None = None,
        toggle_class: When | None = None,
        show: When | bool | None = None,
        **kwargs,
    ):
        super().__init__(
            *args,
            tag="em",
            id=id,
            classes=classes,
            children=children,
            toggle_class=toggle_class,
            show=show,
            **kwargs,
        )


class Small(Element):
    def __init__(
        self,
        *args: Children,
        id: IdArg = None,
        classes: Classes | None = None,
        children: Children | None = None,
        toggle_class: When | None = None,
        show: When | bool | None = None,
        **kwargs,
    ):
        super().__init__(
            *args,
            tag="small",
            id=id,
            classes=classes,
            children=children,
            toggle_class=toggle_class,
            show=show,
            **kwargs,
        )


class Mark(Element):
    def __init__(
        self,
        *args: Children,
        id: IdArg = None,
        classes: Classes | None = None,
        children: Children | None = None,
        toggle_class: When | None = None,
        show: When | bool | None = None,
        **kwargs,
    ):
        super().__init__(
            *args,
            tag="mark",
            id=id,
            classes=classes,
            children=children,
            toggle_class=toggle_class,
            show=show,
            **kwargs,
        )


class Sub(Element):
    def __init__(
        self,
        *args: Children,
        id: IdArg = None,
        classes: Classes | None = None,
        children: Children | None = None,
        toggle_class: When | None = None,
        show: When | bool | None = None,
        **kwargs,
    ):
        super().__init__(
            *args,
            tag="sub",
            id=id,
            classes=classes,
            children=children,
            toggle_class=toggle_class,
            show=show,
            **kwargs,
        )


class Sup(Element):
    def __init__(
        self,
        *args: Children,
        id: IdArg = None,
        classes: Classes | None = None,
        children: Children | None = None,
        toggle_class: When | None = None,
        show: When | bool | None = None,
        **kwargs,
    ):
        super().__init__(
            *args,
            tag="sup",
            id=id,
            classes=classes,
            children=children,
            toggle_class=toggle_class,
            show=show,
            **kwargs,
        )


class Code(Element):
    def __init__(
        self,
        *args: Children,
        id: IdArg = None,
        classes: Classes | None = None,
        children: Children | None = None,
        toggle_class: When | None = None,
        show: When | bool | None = None,
        **kwargs,
    ):
        super().__init__(
            *args,
            tag="code",
            id=id,
            classes=classes,
            children=children,
            toggle_class=toggle_class,
            show=show,
            **kwargs,
        )


class Q(Element):
    def __init__(
        self,
        *args: Children,
        id: IdArg = None,
        classes: Classes | None = None,
        children: Children | None = None,
        toggle_class: When | None = None,
        show: When | bool | None = None,
        **kwargs,
    ):
        super().__init__(
            *args,
            tag="q",
            id=id,
            classes=classes,
            children=children,
            toggle_class=toggle_class,
            show=show,
            **kwargs,
        )


class Cite(Element):
    def __init__(
        self,
        *args: Children,
        id: IdArg = None,
        classes: Classes | None = None,
        children: Children | None = None,
        toggle_class: When | None = None,
        show: When | bool | None = None,
        **kwargs,
    ):
        super().__init__(
            *args, tag="cite", id=id, classes=classes, children=children, toggle_class=toggle_class, show=show, **kwargs
        )


class Span(Element):
    def __init__(
        self,
        *args: Children,
        id: IdArg = None,
        classes: Classes | None = None,
        children: Children | None = None,
        toggle_class: When | None = None,
        show: When | bool | None = None,
        **kwargs,
    ):
        super().__init__(
            *args,
            tag="span",
            id=id,
            classes=classes,
            children=children,
            toggle_class=toggle_class,
            show=show,
            **kwargs,
        )

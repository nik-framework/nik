from __future__ import annotations

from ..data import When
from .base import Children, Classes, Element, IdArg


class Body(Element):
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
            tag="body",
            id=id,
            classes=classes,
            children=children,
            toggle_class=toggle_class,
            show=show,
            **kwargs,
        )


class Header(Element):
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
            tag="header",
            id=id,
            classes=classes,
            children=children,
            toggle_class=toggle_class,
            show=show,
            **kwargs,
        )


class Footer(Element):
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
            tag="footer",
            id=id,
            classes=classes,
            children=children,
            toggle_class=toggle_class,
            show=show,
            **kwargs,
        )


class Nav(Element):
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
            tag="nav",
            id=id,
            classes=classes,
            children=children,
            toggle_class=toggle_class,
            show=show,
            **kwargs,
        )


class Main(Element):
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
            tag="main",
            id=id,
            classes=classes,
            children=children,
            toggle_class=toggle_class,
            show=show,
            **kwargs,
        )


class Section(Element):
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
            tag="section",
            id=id,
            classes=classes,
            children=children,
            toggle_class=toggle_class,
            show=show,
            **kwargs,
        )


class Article(Element):
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
            tag="article",
            id=id,
            classes=classes,
            children=children,
            toggle_class=toggle_class,
            show=show,
            **kwargs,
        )


class Aside(Element):
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
            tag="aside",
            id=id,
            classes=classes,
            children=children,
            toggle_class=toggle_class,
            show=show,
            **kwargs,
        )


class H1(Element):
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
            tag="h1",
            id=id,
            classes=classes,
            children=children,
            toggle_class=toggle_class,
            show=show,
            **kwargs,
        )


class H2(Element):
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
            tag="h2",
            id=id,
            classes=classes,
            children=children,
            toggle_class=toggle_class,
            show=show,
            **kwargs,
        )


class H3(Element):
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
            tag="h3",
            id=id,
            classes=classes,
            children=children,
            toggle_class=toggle_class,
            show=show,
            **kwargs,
        )


class H4(Element):
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
            tag="h4",
            id=id,
            classes=classes,
            children=children,
            toggle_class=toggle_class,
            show=show,
            **kwargs,
        )


class H5(Element):
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
            tag="h5",
            id=id,
            classes=classes,
            children=children,
            toggle_class=toggle_class,
            show=show,
            **kwargs,
        )


class H6(Element):
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
            tag="h6",
            id=id,
            classes=classes,
            children=children,
            toggle_class=toggle_class,
            show=show,
            **kwargs,
        )


class HGroup(Element):
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
            tag="hgroup",
            id=id,
            classes=classes,
            children=children,
            toggle_class=toggle_class,
            show=show,
            **kwargs,
        )

from __future__ import annotations

from ..data import When
from .base import Children, Element, IdArg


class Head(Element):
    def __init__(
        self,
        *args: Children,
        id: IdArg = None,
        children: Children | None = None,
        toggle_class: When | None = None,
        show: When | bool | None = None,
        **kwargs,
    ):
        super().__init__(
            *args,
            tag="head",
            id=id,
            children=children,
            toggle_class=toggle_class,
            show=show,
            **kwargs,
        )


class Meta(Element):
    def __init__(
        self,
        *args,
        charset: str | None = None,
        name: str | None = None,
        content: str | None = None,
        http_equiv: str | None = None,
        id: IdArg = None,
        toggle_class: When | None = None,
        show: When | bool | None = None,
        **kwargs,
    ):
        if charset is not None:
            kwargs["charset"] = charset
        if name is not None:
            kwargs["name"] = name
        if content is not None:
            kwargs["content"] = content
        if http_equiv is not None:
            kwargs["http-equiv"] = http_equiv

        super().__init__(
            *args,
            tag="meta",
            is_void=True,
            id=id,
            toggle_class=toggle_class,
            show=show,
            **kwargs,
        )


class Link(Element):
    def __init__(
        self,
        *args,
        rel: str | None = None,
        href: str | None = None,
        id: IdArg = None,
        toggle_class: When | None = None,
        show: When | bool | None = None,
        **kwargs,
    ):
        if rel is not None:
            kwargs["rel"] = rel
        if href is not None:
            kwargs["href"] = href

        super().__init__(
            *args,
            tag="link",
            is_void=True,
            id=id,
            toggle_class=toggle_class,
            show=show,
            **kwargs,
        )


class Title(Element):
    def __init__(
        self,
        children: str,
        **kwargs,
    ):
        super().__init__(tag="title", children=[children], **kwargs)


class Script(Element):
    def __init__(
        self,
        *args: Children,
        src: str | None = None,
        id: IdArg = None,
        children: Children | None = None,
        toggle_class: When | None = None,
        show: When | bool | None = None,
        **kwargs,
    ):
        if src is not None:
            kwargs["src"] = src

        super().__init__(
            *args,
            tag="script",
            id=id,
            children=children,
            toggle_class=toggle_class,
            show=show,
            **kwargs,
        )

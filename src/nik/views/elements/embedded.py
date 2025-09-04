from __future__ import annotations

from os.path import abspath

from ..data import When
from .base import Children, Classes, Element, IdArg


class Img(Element):
    def __init__(
        self,
        *args: Children,
        src: str | None = None,
        alt: str | None = None,
        width: str | int | None = None,
        height: str | int | None = None,
        id: IdArg = None,
        classes: Classes | None = None,
        children: Children | None = None,
        toggle_class: When | None = None,
        show: When | bool | None = None,
        **kwargs,
    ):
        super().__init__(
            *args,
            tag="img",
            src=src,
            alt=alt,
            width=width,
            height=height,
            id=id,
            classes=classes,
            children=children,
            toggle_class=toggle_class,
            show=show,
            **kwargs,
        )


class Svg(Element):
    def __init__(self, path: str):
        self.path = path
        self.content = self._load_svg_content()

    def _load_svg_content(self):
        with open(abspath(self.path)) as file:
            return file.read()

    def render(self):
        return self.content

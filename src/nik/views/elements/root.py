from __future__ import annotations

from ..data import When
from .base import Children, Element, IdArg


class Html(Element):
    def __init__(
        self,
        *args,
        lang: str | None = None,
        include_doc_type: bool | None = None,
        id: IdArg = None,
        children: Children | None = None,
        toggle_class: When | None = None,
        show: When | bool | None = None,
        **kwargs,
    ):
        if lang is not None:
            kwargs["lang"] = lang

        self._include_doc_type = include_doc_type

        super().__init__(
            *args,
            tag="html",
            id=id,
            children=children,
            toggle_class=toggle_class,
            show=show,
            **kwargs,
        )

    def render(self):
        html = super().render()
        if self._include_doc_type:
            return "<!DOCTYPE html>\n" + html
        else:
            return html

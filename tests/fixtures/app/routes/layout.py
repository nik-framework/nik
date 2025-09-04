# Route layout

from nik.views.context import Page
from nik.views.elements import Body, Children, Head, Html
from nik.views.elements.metadata import Title


def layout(children: Children, page: Page):
    return Html(
        Head(
            Title(page.title),
        ),
        Body(
            "Root layout",
            children,
        ),
    )

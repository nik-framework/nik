from ...views.elements import H1, Body, Html


def template(children):
    return Html(
        lang="en",
        children=[
            Body(
                children=[
                    children,
                ],
            ),
        ],
    )


def generic_error_view(message: str):
    return template(H1(message)).render()

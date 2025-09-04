# Route layout

from nik.views.elements import Children, Main


def layout(children: Children):
    return Main(
        "Patients sub layout",
        children,
    )

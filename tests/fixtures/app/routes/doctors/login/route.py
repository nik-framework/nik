from nik.server.cookies import Cookies
from nik.server.errors import unauthorized_error
from nik.views.actions import Action
from nik.views.elements import Section
from tests.utils import get_secure_cookie_obj


def action(body: dict, cookies: Cookies):
    if body["username"] == "doctor" and body["password"] == "BadWolf42":
        secure_cookie = get_secure_cookie_obj("doctor")
        cookie = secure_cookie.create({"user_id": 1, "role": "doctor"})
        cookies.set(cookie)

        Action.redirect("/doctors/dashboard")
    else:
        unauthorized_error()


def view():
    return Section(
        "Doctors login page",
    )

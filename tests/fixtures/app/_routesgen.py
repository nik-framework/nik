# type: ignore
# ruff: noqa: E501, F401, I001, Q000

# This file is auto-generated, do not edit it directly.

from app.routes.blocking.route import action as app_routes_blocking_route_action
from app.routes.blocking.route import view as app_routes_blocking_route_view
from app.routes.doctors.login.route import action as app_routes_doctors_login_route_action
from app.routes.doctors.login.route import view as app_routes_doctors_login_route_view
from app.routes.doctors.patients._patient_id_.appointments._appointment_id_.route import action as app_routes_doctors_patients__patient_id__appointments__appointment_id__route_action
from app.routes.doctors.patients._patient_id_.appointments._appointment_id_.route import view as app_routes_doctors_patients__patient_id__appointments__appointment_id__route_view
from app.routes.doctors.patients._patient_id_.route import view as app_routes_doctors_patients__patient_id__route_view
from app.routes.layout import layout as app_routes_layout_layout
from app.routes.patients.appointments.route import view as app_routes_patients_appointments_route_view
from app.routes.patients.dashboard.route import view as app_routes_patients_dashboard_route_view
from app.routes.patients.layout import layout as app_routes_patients_layout_layout
from app.routes.patients.route import view as app_routes_patients_route_view
from app.routes.route import action as app_routes_route_action
from app.routes.route import view as app_routes_route_view
from nik.server.authentication.session import Session
from nik.server.cookies import Cookies
from nik.server.routes.router import Route, RouteComponent, RouteComponentParam
from nik.views.context import Page
from nik.views.elements import Children
import re


# RouteComponent definitions
_rc_app_routes_layout_layout = RouteComponent(
    app_routes_layout_layout,
    [RouteComponentParam("children", Children), RouteComponentParam("page", Page)], is_async=False, is_root=True,
)
_rc_app_routes_route_view = RouteComponent(
    app_routes_route_view,
    [], is_async=True,
)
_rc_app_routes_route_action = RouteComponent(
    app_routes_route_action,
    [], is_async=True,
)
_rc_app_routes_blocking_route_view = RouteComponent(
    app_routes_blocking_route_view,
    [], is_async=False,
)
_rc_app_routes_blocking_route_action = RouteComponent(
    app_routes_blocking_route_action,
    [], is_async=False,
)
_rc_app_routes_doctors_login_route_view = RouteComponent(
    app_routes_doctors_login_route_view,
    [], is_async=False,
)
_rc_app_routes_doctors_login_route_action = RouteComponent(
    app_routes_doctors_login_route_action,
    [RouteComponentParam("body", dict), RouteComponentParam("cookies", Cookies)], is_async=False,
)
_rc_app_routes_doctors_patients__patient_id__route_view = RouteComponent(
    app_routes_doctors_patients__patient_id__route_view,
    [RouteComponentParam("patient_id", str)], is_async=False,
)
_rc_app_routes_doctors_patients__patient_id__appointments__appointment_id__route_view = RouteComponent(
    app_routes_doctors_patients__patient_id__appointments__appointment_id__route_view,
    [RouteComponentParam("patient_id"), RouteComponentParam("appointment_id")], is_async=False,
)
_rc_app_routes_doctors_patients__patient_id__appointments__appointment_id__route_action = RouteComponent(
    app_routes_doctors_patients__patient_id__appointments__appointment_id__route_action,
    [], is_async=False,
)
_rc_app_routes_patients_layout_layout = RouteComponent(
    app_routes_patients_layout_layout,
    [RouteComponentParam("children", Children)], is_async=False,
)
_rc_app_routes_patients_route_view = RouteComponent(
    app_routes_patients_route_view,
    [], is_async=False,
)
_rc_app_routes_patients_appointments_route_view = RouteComponent(
    app_routes_patients_appointments_route_view,
    [], is_async=False,
)
_rc_app_routes_patients_dashboard_route_view = RouteComponent(
    app_routes_patients_dashboard_route_view,
    [], is_async=False,
)


_NONE_DYNAMIC_ROUTES = {
    "/": Route(
        "/", [_rc_app_routes_layout_layout, _rc_app_routes_route_view], action=_rc_app_routes_route_action, permissions=None
    ),
    "/blocking": Route(
        "/blocking", [_rc_app_routes_layout_layout, _rc_app_routes_blocking_route_view], action=_rc_app_routes_blocking_route_action, permissions=None
    ),
    "/doctors/login": Route(
        "/doctors/login", [_rc_app_routes_layout_layout, _rc_app_routes_doctors_login_route_view], action=_rc_app_routes_doctors_login_route_action, permissions=None
    ),
    "/patients": Route(
        "/patients", [_rc_app_routes_layout_layout, _rc_app_routes_patients_layout_layout, _rc_app_routes_patients_route_view], action=None, permissions={'role': 'patient'}
    ),
    "/patients/appointments": Route(
        "/patients/appointments", [_rc_app_routes_layout_layout, _rc_app_routes_patients_layout_layout, _rc_app_routes_patients_appointments_route_view], action=None, permissions={'role': 'patient'}
    ),
    "/patients/dashboard": Route(
        "/patients/dashboard", [_rc_app_routes_layout_layout, _rc_app_routes_patients_layout_layout, _rc_app_routes_patients_dashboard_route_view], action=None, permissions={'role': 'patient'}
    ),
}


_DYNAMIC_ROUTES = (
    (
        re.compile(r"^/doctors/patients/(?P<patient_id>[^/]+)$"),
        Route(
            "/doctors/patients/_patient_id_",
            [_rc_app_routes_layout_layout, _rc_app_routes_doctors_patients__patient_id__route_view], action=None, permissions={'role': 'doctor'},
        ),
    ),
    (
        re.compile(r"^/doctors/patients/(?P<patient_id>[^/]+)/appointments/(?P<appointment_id>[^/]+)$"),
        Route(
            "/doctors/patients/_patient_id_/appointments/_appointment_id_",
            [_rc_app_routes_layout_layout, _rc_app_routes_doctors_patients__patient_id__appointments__appointment_id__route_view], action=_rc_app_routes_doctors_patients__patient_id__appointments__appointment_id__route_action, permissions={'role': 'doctor'},
        ),
    ),
)


ROUTES = (_NONE_DYNAMIC_ROUTES, _DYNAMIC_ROUTES)

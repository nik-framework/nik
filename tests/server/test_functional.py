from __future__ import annotations

import asyncio
import re

import pytest
from tests.utils import create_app, get_secure_cookie_obj


def add_cookies_to_client(client, cookie_type, role=None):
    cookie = get_secure_cookie_obj(cookie_type).create({"user_id": 1, "role": role or cookie_type})
    client.cookies = {key: morsel.value for key, morsel in cookie.items()}


@pytest.fixture
def app(request: pytest.FixtureRequest):
    param = getattr(request, "param", None)
    if param:
        guards = (get_secure_cookie_obj(param),)
    else:
        guards = None

    return create_app("test", guards)


async def test_root_path_async_view(client):
    """view is an async function"""

    response = await client.get("/")

    assert response.status_code == 200
    assert "<title>Nik Framework</title>" in response.text
    assert "Root layout" in response.text
    assert "Patients layout" not in response.text
    assert "<div>Home Page</div>" in response.text


async def test_root_path_async_action(client):
    """action is an async function"""

    response = await client.put("/")

    assert response.status_code == 200
    assert re.search(r'{"actions":{"v_.*?":null}}', response.text)


async def test_patient_route_without_authentication(client):
    response = await client.get("/patients")
    assert response.status_code == 401
    assert '<html lang="en"><body><h1>Unauthorized</h1></body></html>' in response.text


@pytest.mark.parametrize("app", ["patient"], indirect=True)
async def test_patient_route_with_valid_authentication(client):
    add_cookies_to_client(client, "patient")

    response = await client.get("/patients")
    assert response.status_code == 200
    assert "Root layout" in response.text
    assert "Patients sub layout" in response.text
    assert "Patients root path" in response.text


@pytest.mark.parametrize("app", ["patient"], indirect=True)
async def test_patient_route_with_insufficient_permissions(client):
    """Cookie is configured for patient, but we send a "valid" cookie with a doctor role."""

    add_cookies_to_client(client, "patient", role="doctor")
    response = await client.get("/patients")

    assert response.status_code == 403
    assert '<html lang="en"><body><h1>Forbidden</h1></body></html>' == response.text


@pytest.mark.parametrize("app", ["doctor"], indirect=True)
async def test_public_route_under_protected_area(client):
    response = await client.get("/doctors/login")
    assert response.status_code == 200
    assert "Root layout" in response.text
    assert "Patients root path" not in response.text
    assert "<section>Doctors login page</section>" in response.text


@pytest.mark.parametrize("app", ["doctor"], indirect=True)
async def test_route_with_multiple_dynamic_parameters(client):
    add_cookies_to_client(client, "doctor")
    response = await client.get("/doctors/patients/1/appointments/2")

    assert response.status_code == 200
    assert "Root layout" in response.text
    assert "Patients root path" not in response.text
    assert "Patient ID=1, Appointment ID=2" in response.text


@pytest.mark.parametrize("app", ["doctor"], indirect=True)
async def test_action_that_sets_a_cookie(client):
    """This simulates a controlled form submission using JS client."""

    # valid login
    response = await client.post(
        "/doctors/login",
        headers={"content-type": "application/x-www-form-urlencoded"},
        data={"username": "doctor", "password": "BadWolf42"},
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert re.search(r'nik-doctor=".*?"', response.headers["Set-Cookie"])
    assert re.search(r'{"actions":{"v_.*?":\[\["redirect",\["/doctors/dashboard",true\]\]\]}}', response.text)

    # invalid login
    response = await client.post(
        "/doctors/login",
        headers={
            "x-nik-request": "1",
            "x-nik-request-type": "form",
            "content-type": "application/x-www-form-urlencoded",
        },
        data={"username": "doctor", "password": "wrong_password"},
    )
    assert response.status_code == 401
    assert "Set-Cookie" not in response.headers
    assert re.search(r'{"actions":{"v_.*?":null}}', response.text)


async def test_not_found_url(client):
    response = await client.get("/this-is-not-a-real-page")
    assert response.status_code == 404
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert '<html lang="en"><body><h1>Not Found</h1></body></html>' == response.text


async def test_nik_request_with_invalid_previous_path(client):
    response = await client.get(
        "/",
        headers={
            "x-nik-request": "1",
            "x-nik-previous-path": "/this-is-not-a-real-page",
        },
    )
    assert response.status_code == 404
    assert response.headers["content-type"] == "application/json"
    assert "{}" == response.text


@pytest.mark.parametrize("app", ["doctor"], indirect=True)
async def test_nik_request_with_unauthorized_previous_path(client):
    """Previous paths must also be matched and authorized."""

    add_cookies_to_client(client, "doctor")
    response = await client.get(
        "/doctors/patients/1/appointments/2",
        headers={
            "x-nik-request": "1",
            "x-nik-previous-path": "/patients",
        },
    )

    assert response.status_code == 403
    assert response.headers["content-type"] == "application/json"
    assert "{}" == response.text


@pytest.mark.parametrize("app", ["doctor"], indirect=True)
async def test_valid_nik_request_returning_partial_json_response(client):
    add_cookies_to_client(client, "doctor")
    response = await client.get(
        "/doctors/patients/1/appointments/2",
        headers={
            "x-nik-request": "1",
            "x-nik-previous-path": "/doctors/patients/1",
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert re.search(r'{"replaces":"v_.*?","view":".*?","actions":{"v_.*?":null}}', response.text)


async def test_static_file_in_public_folder(client):
    response = await client.get(
        "/public/llm.txt",
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/plain; charset=utf-8"
    assert "Not what you are looking for.\n" == response.text


@pytest.mark.parametrize("app", ["patient"], indirect=True)
async def test_unsupported_request_method(client):
    """eg: When a POST request is made to a route that only exports a view function."""
    add_cookies_to_client(client, "patient")
    response = await client.post("/patients/dashboard")
    assert response.status_code == 405
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert '<html lang="en"><body><h1>Method Not Allowed</h1></body></html>' == response.text


@pytest.mark.parametrize("app", ["doctor"], indirect=True)
async def test_action_explicitly_returning_response_object(client):
    """Actions can return actions or response objects."""

    add_cookies_to_client(client, "doctor")
    response = await client.post("/doctors/patients/1/appointments/2")

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/plain; charset=utf-8"
    assert response.text == "Action performed"


async def test_non_blocking_response_occurs_before_blocking(client):
    """
    Strategy:
    1) Start a blocking sync request (sleeps ~200ms).
    2) Start a non-blocking async request before it completes.
    3) Assert the non-blocking response arrives before the blocking one.
    """

    # Warm up
    await client.get("/")

    slow_task = asyncio.create_task(client.get("/blocking"))
    await asyncio.sleep(0.01)  # ensure slow starts first
    fast_task = asyncio.create_task(client.get("/"))

    done, pending = await asyncio.wait({slow_task, fast_task}, return_when=asyncio.FIRST_COMPLETED)

    # The first completed should be the fast request
    assert fast_task in done
    assert slow_task in pending

    fast_resp = fast_task.result()
    assert fast_resp.status_code == 200

    # Now ensure the slow one finishes and is valid
    slow_resp = await slow_task
    assert slow_resp.status_code == 200
    assert "Blocking sync view" in slow_resp.text


async def test_sync_action_runs_in_thread_and_collects_actions(client):
    # Make a nik action call to /blocking
    resp = await client.post(
        "/blocking",
        headers={"x-nik-request": "1"},
    )
    assert resp.status_code == 200
    assert "refreshView" in resp.text

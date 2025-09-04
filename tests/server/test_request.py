from __future__ import annotations

import pytest
from httpx import AsyncClient
from nik.server.errors import BadRequestError
from nik.server.request import Request
from nik.server.response import Response
from nik.server.types import Receive, Scope, Send


@pytest.fixture
async def app(request: pytest.FixtureRequest):
    async def _app(scope: Scope, receive: Receive, send: Send):
        req = Request(scope, receive)
        if request.param == "query":
            params = dict(req.query)
            params = dict(req.query)
            response = Response.json({"params": params})
        elif request.param == "json_body":
            body = await req.body
            response = Response.json({"json": body})
        elif request.param == "urlencoded_body":
            body = await req.body
            body = await req.body
            response = Response.json({"form": body})
        elif request.param == "cookies":
            response = Response.json({"cookies": dict(req.cookies.items())})
        elif request.param == "headers":
            response = Response.json(
                {
                    "is_nik_request": req.is_nik_request,
                    "is_link_request": req.is_link_request,
                    "is_partial_request": req.is_partial_request,
                    "is_form_request": req.is_form_request,
                    "previous_path": req.previous_path,
                    "nik_request_type": req.nik_request_type,
                }
            )
        else:
            raise NotImplementedError("Invalid test parameter")
        await response.send(send)

    return _app


@pytest.mark.parametrize("app", ["query"], indirect=True)
async def test_query_params(client) -> None:
    response = await client.get("/?name=nik&version=1&tag=python&tag=async&tag=web&empty_param")
    assert response.json() == {
        "params": {"name": "nik", "version": "1", "tag": ["python", "async", "web"], "empty_param": ""}
    }


@pytest.mark.parametrize("app", ["json_body"], indirect=True)
async def test_json_body(client) -> None:
    response = await client.post("/", json={"name": "nik", "version": "1"})
    assert response.json() == {"json": {"name": "nik", "version": "1"}}

    # Invalid json body
    with pytest.raises(BadRequestError):
        response = await client.post("/", data="{ ", headers={"Content-Type": "application/json"})


@pytest.mark.parametrize("app", ["urlencoded_body"], indirect=True)
async def test_urlencoded_body(client) -> None:
    response = await client.post("/", data={"name": "nik", "version": "1"})
    assert response.json() == {"form": {"name": "nik", "version": "1"}}


@pytest.mark.parametrize("app", ["cookies"], indirect=True)
async def test_cookies(client: AsyncClient) -> None:
    response = await client.get("/", headers={"Cookie": "session_id=123456; request_id=req-123456"})
    assert response.json()["cookies"] == {"session_id": "123456", "request_id": "req-123456"}


@pytest.mark.parametrize("app", ["headers"], indirect=True)
async def test_nik_request_headers(client: AsyncClient) -> None:
    response = await client.get("/", headers={})
    json = response.json()
    assert not json["is_nik_request"]
    assert json["previous_path"] is None

    response = await client.get("/", headers={"x-nik-request": "1"})
    assert response.json()["is_nik_request"]

    response = await client.get("/", headers={"x-nik-request": "1", "x-nik-request-type": "link"})
    json = response.json()
    assert json["nik_request_type"] == "link"
    assert json["is_link_request"]

    response = await client.get(
        "/", headers={"x-nik-request": "1", "x-nik-request-type": "link", "x-nik-previous-path": "/dashboard"}
    )
    json = response.json()
    assert json["nik_request_type"] == "link"
    assert json["is_link_request"]
    assert json["previous_path"] == "/dashboard"

    response = await client.get("/", headers={"x-nik-request": "1", "x-nik-request-type": "partial"})
    json = response.json()
    assert json["nik_request_type"] == "partial"
    assert json["is_partial_request"]

    response = await client.get("/", headers={"x-nik-request": "1", "x-nik-request-type": "form"})
    json = response.json()
    assert json["nik_request_type"] == "form"
    assert json["is_form_request"]

import json
from http.cookies import SimpleCookie
from unittest.mock import AsyncMock

from nik.server.cookies import Cookies
from nik.server.response import Response
from tests.utils import get_header_list


def test_text_response():
    response = Response("Hello world!")
    assert response.body == b"Hello world!"
    assert response.status == 200
    assert response.media_type == "text/plain"


def test_bytes_response():
    response = Response(b"Hello, Bytes!", media_type="image/png")
    assert response.body == b"Hello, Bytes!"
    assert response.status == 200
    assert response.media_type == "image/png"


def test_html_response():
    response = Response.html("<h1>Title</h1>", status=202)
    assert response.body == b"<h1>Title</h1>"
    assert response.status == 202
    assert response.media_type == "text/html"


def test_json_response():
    data = {"key": "value", "number": 123}
    response = Response.json(data)
    assert json.loads(response.body) == data
    assert response.status == 200
    assert response.media_type == "application/json"


def test_json_none_response():
    response = Response.json(None)
    assert json.loads(response.body) is None
    assert response.status == 200
    assert response.media_type == "application/json"


def test_implicit_response_headers():
    response = Response("text")
    assert get_header_list(response.raw_headers, "content-type") == [b"text/plain; charset=utf-8"]
    assert get_header_list(response.raw_headers, "content-length") == [b"4"]


def test_custom_response_headers():
    response = Response("text", headers={"X-Custom-Header": "Value"})
    assert get_header_list(response.raw_headers, "x-custom-header") == [b"Value"]


def test_response_cookies():
    cookies = Cookies()

    cookie1 = SimpleCookie()
    cookie1["session_id"] = "12345"
    cookie1["session_id"]["path"] = "/"
    cookies.set(cookie1)

    cookie2 = SimpleCookie()
    cookie2["tracker"] = "abc"
    cookie2["tracker"]["max-age"] = 3600
    cookies.set(cookie2)

    response = Response("test", cookies=cookies)

    cookie_headers = get_header_list(response.raw_headers, "set-cookie")
    assert cookie_headers == [b"session_id=12345; Path=/", b"tracker=abc; Max-Age=3600"]


async def test_send_method():
    cookies = Cookies()
    cookie = SimpleCookie()
    cookie["user"] = "nik"
    cookies.set(cookie)
    response = Response.json({"data": "test"}, status=201, headers={"X-Test": "Value"}, cookies=cookies)

    send_callable = AsyncMock()

    await response.send(send_callable)
    start_call, body_call = send_callable.call_args_list

    assert send_callable.call_count == 2
    assert start_call.args == (
        {
            "type": "http.response.start",
            "status": 201,
            "headers": response.raw_headers,
        },
    )
    assert body_call.args == (
        {
            "type": "http.response.body",
            "body": b'{"data":"test"}',
        },
    )

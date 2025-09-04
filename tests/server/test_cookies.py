from http.cookies import SimpleCookie

import pytest
from nik.server.cookies import Cookies


def test_get_cookies():
    cookies = Cookies("session_id=123456; request_id=req-123456")
    assert cookies.has_new is False
    assert cookies.get("session_id") == "123456"
    assert cookies["request_id"] == "req-123456"
    assert cookies.get("non_existent") is None
    with pytest.raises(KeyError):
        cookies["non_existent"]


def test_add_cookies():
    cookie = SimpleCookie()
    cookie["session_id"] = "123456"
    cookie["session_id"]["path"] = "/some-path"

    cookies = Cookies()
    cookies.set(cookie)

    assert cookies.has_new
    assert len(cookies.new) == 1

    assert cookies.to_set_headers() == "session_id=123456; Path=/some-path"

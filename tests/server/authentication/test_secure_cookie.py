from dataclasses import dataclass
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from nik.server.authentication.securecookie import SecureCookie
from nik.server.cookies import Cookies

SECRET_KEY = "test-secret"
COOKIE_NAME = "test-session"


@dataclass
class SessionData:
    user_id: str
    role: str


@pytest.fixture
def secure_cookie():
    return SecureCookie(
        name=COOKIE_NAME,
        secret=SECRET_KEY,
        options={"httponly": True, "samesite": "Lax"},
        session_data_class=SessionData,
    )


@pytest.fixture
def mock_request():
    request = MagicMock()
    request.cookies = Cookies()
    return request


def test_init(secure_cookie):
    assert secure_cookie.name == COOKIE_NAME
    assert secure_cookie.secret == SECRET_KEY.encode("utf-8")
    assert secure_cookie.options == {"httponly": True, "samesite": "Lax"}
    assert secure_cookie._session_data_class == SessionData


def test_init_raises_error_on_missing_name():
    with pytest.raises(AssertionError, match="Cookie name must be provided."):
        SecureCookie(name="", secret=SECRET_KEY, options={}, session_data_class=SessionData)


def test_init_raises_error_on_missing_secret():
    with pytest.raises(AssertionError, match="Secret key must be provided."):
        SecureCookie(name=COOKIE_NAME, secret="", options={}, session_data_class=SessionData)


def test_create_and_verify_successful(secure_cookie, mock_request):
    data = {"user_id": "123", "role": "admin"}
    cookie = secure_cookie.create(data)

    mock_request.cookies[COOKIE_NAME] = cookie[COOKIE_NAME].value

    session_data = secure_cookie.verify(mock_request)

    assert isinstance(session_data, SessionData)
    assert session_data == SessionData(user_id="123", role="admin")


def test_verify_no_cookie(secure_cookie, mock_request):
    assert secure_cookie.verify(mock_request) is None


def test_verify_tampered_payload(secure_cookie, mock_request):
    data = {"user_id": "123", "role": "admin"}
    cookie = secure_cookie.create(data)
    cookie_value = cookie[COOKIE_NAME].value

    tampered_value = "a" + cookie_value[1:]
    mock_request.cookies[COOKIE_NAME] = tampered_value

    assert secure_cookie.verify(mock_request) is None


def test_verify_incorrect_secret(secure_cookie, mock_request):
    data = {"user_id": "123", "role": "admin"}
    cookie = secure_cookie.create(data)
    mock_request.cookies[COOKIE_NAME] = cookie[COOKIE_NAME].value

    verifier_with_wrong_secret = SecureCookie(
        name=COOKIE_NAME,
        secret="wrong-secret",
        options={},
        session_data_class=SessionData,
    )

    assert verifier_with_wrong_secret.verify(mock_request) is None


def test_verify_malformed_cookie_value(secure_cookie, mock_request):
    mock_request.cookies[COOKIE_NAME] = "not-a-valid-cookie"
    assert secure_cookie.verify(mock_request) is None


def test_verify_payload_mismatch_dataclass(secure_cookie, mock_request):
    data = {"user_id": "123"}
    cookie = secure_cookie.create(data)
    mock_request.cookies[COOKIE_NAME] = cookie[COOKIE_NAME].value

    assert secure_cookie.verify(mock_request) is None


def test_create_raises_error_for_non_serializable_data(secure_cookie):
    with pytest.raises(ValueError, match="Data for cookie must be JSON serializable."):
        secure_cookie.create({"time": datetime.now()})


@pytest.mark.parametrize(
    "option_key, option_value, expected_output",
    [
        ("httponly", True, "HttpOnly"),
        ("secure", True, "Secure"),
        ("samesite", "Strict", "SameSite=Strict"),
        ("path", "/", "Path=/"),
        ("domain", ".example.com", "Domain=.example.com"),
        ("max_age", 3600, "Max-Age=3600"),
    ],
)
def test_create_with_options(option_key, option_value, expected_output):
    cookie_handler = SecureCookie(
        name=COOKIE_NAME,
        secret=SECRET_KEY,
        options={option_key: option_value},
        session_data_class=SessionData,
    )
    cookie = cookie_handler.create({"user_id": "test"})
    cookie_string = cookie.output(header="").strip()
    assert expected_output in cookie_string


def test_create_with_expires_datetime():
    expires_dt = datetime(2029, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    cookie_handler = SecureCookie(
        name=COOKIE_NAME,
        secret=SECRET_KEY,
        options={"expires": expires_dt},
        session_data_class=SessionData,
    )
    cookie = cookie_handler.create({"user_id": "test"})
    cookie_string = cookie.output(header="").strip()
    assert "expires=Mon, 01 Jan 2029 12:00:00 GMT" in cookie_string


def test_create_with_str_expires_datetime():
    cookie_handler = SecureCookie(
        name=COOKIE_NAME,
        secret=SECRET_KEY,
        options={"expires": "Mon, 01 Jan 2029 12:00:00 GMT"},
        session_data_class=SessionData,
    )
    with pytest.raises(ValueError, match="The 'expires' option must be a datetime object."):
        cookie_handler.create({"user_id": "test"})


def test_create_with_invalid_cookie_option():
    cookie_handler = SecureCookie(
        name=COOKIE_NAME,
        secret=SECRET_KEY,
        options={"invalid_option": "value"},
        session_data_class=SessionData,
    )
    with pytest.raises(ValueError, match="Unknown cookie option: invalid_option"):
        cookie_handler.create({"user_id": "test"})

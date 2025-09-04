from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import json
import sys
from datetime import datetime
from email.utils import format_datetime
from http.cookies import SimpleCookie
from typing import TYPE_CHECKING, Any, Generic, TypeVar

T = TypeVar("T", bound=object)

if TYPE_CHECKING:
    from ..request import Request


class SecureCookie(Generic[T]):
    """
    A secure cookie implementation.

    Cookie value format: base64(payload_bytes + separator + signature_bytes)

    Attributes
    ----------
    secret : str
        The secret key for HMAC signing.
    name : str
        The name of the secure cookie.
    options : dict[str, Any]
        Cookie options. eg: httponly, secure, etc.
    _session_data_class : type[T]
        The class type for the session data stored in the cookie.
    separator : bytes
        The separator used between the payload and the signature in the cookie value.

    Example:
    ```
    @dataclass
    class SessionData:
        user_id: str

    cookie = SecureCookie("session", "secret", {"httponly": True}, SessionData)
    ```
    """

    separator = b"."

    def __init__(self, name: str, secret: str, options: dict[str, Any], session_data_class: type[T]):
        assert name, "Cookie name must be provided."
        assert secret, "Secret key must be provided."

        self.name = name
        self.secret = secret.encode("utf-8")
        self.options = options
        self._session_data_class = session_data_class

    def create(self, data: dict[str, Any]) -> SimpleCookie:
        """
        Creates a signed cookie as SimpleCookie object with the provided data.

        The data is JSON-serialized, signed, and base64-encoded.

        Parameters
        ----------
        data : dict[str, Any]
            A dictionary of data to store in the cookie. Must be JSON serializable.

        Returns
        -------
        SimpleCookie
            A SimpleCookie object containing the signed cookie.
            e.g., "nik_session=signed_cookie_value; HttpOnly; Secure; SameSite=Lax; Max-Age=3600"
        """
        try:
            payload_json = json.dumps(data, separators=(",", ":"))
            payload_bytes = payload_json.encode("utf-8")
        except TypeError as e:
            raise ValueError("Data for cookie must be JSON serializable.") from e

        signature_bytes = hmac.new(self.secret, payload_bytes, hashlib.sha256).digest()

        combined_bytes = payload_bytes + self.separator + signature_bytes
        cookie_value = base64.urlsafe_b64encode(combined_bytes).decode("utf-8")

        cookie = SimpleCookie()
        cookie[self.name] = cookie_value

        for key, value in self.options.items():
            attr_key = key.lower()
            morsel = cookie[self.name]

            if attr_key == "httponly":
                morsel["httponly"] = value
            elif attr_key == "secure":
                morsel["secure"] = value
            elif attr_key == "samesite":
                morsel["samesite"] = value
            elif attr_key == "max_age":
                morsel["max-age"] = value
            elif attr_key == "expires":
                if isinstance(value, datetime):
                    morsel["expires"] = format_datetime(value, usegmt=True)
                else:
                    raise ValueError("The 'expires' option must be a datetime object.")
            elif attr_key == "path":
                morsel["path"] = value
            elif attr_key == "domain":
                morsel["domain"] = value
            elif attr_key == "partitioned":  # pragma: no cover
                if sys.version_info < (3, 14):
                    raise ValueError("Partitioned cookies are only supported in Python 3.14 and above.")
                morsel["partitioned"] = True
            else:
                raise ValueError(f"Unknown cookie option: {key}")

        return cookie

    def verify(self, request: Request) -> T | None:
        """
        Verifies a signed cookie value from the cookies in the request object.

        Parameters
        ----------
        request : Request
            The request object containing the cookies to verify.

        Returns
        -------
        T | None
            The session data if the cookie is valid, None otherwise.
        """

        cookie_value = request.cookies.get(self.name)
        if not cookie_value:
            return None

        try:
            combined_bytes = base64.urlsafe_b64decode(cookie_value.encode("utf-8"))
        except (TypeError, binascii.Error):
            return None  # Invalid base64 encoding

        signature_size = hashlib.sha256().digest_size
        separator_len = len(self.separator)

        min_len = signature_size + separator_len
        if len(combined_bytes) < min_len:
            return None

        signature_from_cookie = combined_bytes[-signature_size:]
        separator_in_cookie = combined_bytes[-(signature_size + separator_len) : -signature_size]
        payload_bytes = combined_bytes[: -(signature_size + separator_len)]

        if separator_in_cookie != self.separator:
            return None

        expected_signature_bytes = hmac.new(self.secret, payload_bytes, hashlib.sha256).digest()

        if not hmac.compare_digest(signature_from_cookie, expected_signature_bytes):
            return None  # Signature mismatch

        try:
            payload_json = payload_bytes.decode("utf-8")
            original_data = json.loads(payload_json)
            return self._session_data_class(**original_data)
        except (UnicodeDecodeError, json.JSONDecodeError, TypeError):
            return None

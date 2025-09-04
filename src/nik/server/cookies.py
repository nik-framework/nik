from __future__ import annotations

from collections.abc import MutableMapping
from http.cookies import SimpleCookie, _unquote


def parse_cookies(cookie_header: str) -> dict[str, str]:
    """
    This function has been adapted from Starlette.

    https://github.com/encode/starlette/blob/fa5355442753f794965ae1af0f87f9fec1b9a3de/starlette/requests.py#L40
    """
    cookie_dict: dict[str, str] = {}
    for chunk in cookie_header.split(";"):
        if "=" in chunk:
            key, val = chunk.split("=", 1)
        else:
            key, val = "", chunk
        key, val = key.strip(), val.strip()
        if key or val:
            cookie_dict[key] = _unquote(val)
    return cookie_dict


class Cookies(MutableMapping[str, str]):
    def __init__(self, raw_cookies: str | None = None):
        self._raw_cookies = raw_cookies or ""
        self._cookies = {}
        self._is_parsed = False

        self.new: list[SimpleCookie] = []

    def set(self, cookie: SimpleCookie):
        self.new.append(cookie)

    @property
    def has_new(self) -> bool:
        return bool(self.new)

    def to_set_headers(self):
        """Convert the "new cookies" to a 'Set-Cookie' header value string.

        Useful for HTTP responses.

        eg: sessionid=abc123;
        """
        return "; ".join(cookie.output(header="").strip() for cookie in self.new)

    def items(self):
        self._parse()
        return self._cookies.items()

    def _parse(self):
        if not self._is_parsed:
            self._cookies = parse_cookies(self._raw_cookies)
            self._is_parsed = True

    def __getitem__(self, name: str):
        self._parse()
        return self._cookies[name]

    def __setitem__(self, key: str, value: str):
        self._parse()
        self._cookies[key] = value

    def __delitem__(self, key: str):
        self._parse()
        del self._cookies[key]

    def __iter__(self):
        self._parse()
        return iter(self._cookies)

    def __len__(self):
        self._parse()
        return len(self._cookies)

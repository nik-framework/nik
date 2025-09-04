from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Literal
from urllib.parse import parse_qsl

from .cookies import Cookies
from .errors import BadRequestError
from .types import RawHeaders, Scope

if TYPE_CHECKING:
    from .types import Headers, Receive

NIK_REQUEST_HEADER = "x-nik-request"
NIK_REQUEST_TYPE_HEADER = "x-nik-request-type"
NIK_PARTIAL_REQUEST_HEADER = "x-nik-partial-request"
NIK_PREVIOUS_PATH_HEADER = "x-nik-previous-path"

TRequestType = Literal["link", "partial", "form"]
NIK_REQUEST_TYPES: list[TRequestType] = ["link", "partial", "form"]


def is_nik_request(headers: Headers) -> bool:
    return headers.get(NIK_REQUEST_HEADER, None) == "1"


def get_previous_path(headers: Headers) -> str | None:
    previous_path = headers.get(NIK_PREVIOUS_PATH_HEADER, "").strip()
    if previous_path.startswith("/"):
        return previous_path
    return None


def get_nik_request_type(headers: Headers) -> TRequestType:
    type = headers.get(NIK_REQUEST_TYPE_HEADER, None)
    return type if type in NIK_REQUEST_TYPES else "link"


def parse_query_string(data: bytes) -> dict[str, str | list[str]]:
    result = {}
    for key, value in parse_qsl(data.decode("latin-1"), keep_blank_values=True):
        if key in result:
            existing_value = result[key]
            if isinstance(existing_value, list):
                existing_value.append(value)
            else:
                result[key] = [existing_value, value]
        else:
            result[key] = value
    return result


def parse_headers(headers: RawHeaders) -> dict[str, str]:
    return {k.decode("latin-1"): v.decode("latin-1") for k, v in headers}


class Request:
    def __init__(self, scope: Scope, receive: Receive):
        assert scope["type"] == "http"
        self._scope = scope
        self._receive = receive

        self.method = scope["method"].lower()
        self.path = scope["path"]

        self.headers = parse_headers(scope["headers"])
        self.cookies = Cookies(self.headers.get("cookie", None))
        self._query = None
        self._body = None

        self.is_static_path = self.path.startswith("/public/")
        self.is_nik_request = is_nik_request(self.headers)
        self.nik_request_type = get_nik_request_type(self.headers)
        self.previous_path = get_previous_path(self.headers)

    @property
    def query(self):
        if self._query is None:
            self._query = parse_query_string(self._scope["query_string"])
        return self._query

    @property
    async def body(self):
        if self._body is not None:
            return self._body

        content_type = self.headers.get("content-type", "")

        if content_type.startswith("application/json"):
            self._body = await self._decode_json_body()
        elif content_type.startswith("application/x-www-form-urlencoded"):
            self._body = parse_query_string(await self._read_body())
        else:
            raise NotImplementedError(f"Unsupported content type: {content_type}.")

        return self._body

    @property
    def is_link_request(self) -> bool:
        return self.is_nik_request and self.nik_request_type == "link"

    @property
    def is_partial_request(self) -> bool:
        return self.is_nik_request and self.nik_request_type == "partial"

    @property
    def is_form_request(self) -> bool:
        return self.is_nik_request and self.nik_request_type == "form"

    async def _decode_json_body(self) -> Any:
        try:
            return json.loads(await self._read_body())
        except json.JSONDecodeError as err:
            raise BadRequestError(self, "Invalid JSON body received") from err

    async def _read_body(self) -> bytes:
        body = b""
        more_body = True
        while more_body:
            message = await self._receive()
            body += message.get("body", b"")
            more_body = message.get("more_body", False)

        return body

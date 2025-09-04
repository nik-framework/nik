from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..utils.string import to_json

if TYPE_CHECKING:
    from .cookies import Cookies
    from .types import Headers, Send


class Response:
    def __init__(
        self,
        body: bytes | str,
        status: int = 200,
        media_type: str = "text/plain",
        cookies: Cookies | None = None,
        headers: Headers | None = None,
    ):
        self.body = body if isinstance(body, bytes) else body.encode("utf-8")
        self.status = status
        self.media_type = media_type
        self.cookies = cookies
        self.raw_headers = self.build_headers(headers)

    def build_headers(self, headers: Headers | None = None) -> list[tuple[bytes, bytes]]:
        if headers is None:
            raw_headers = []
            has_content_length = False
            has_content_type = False
        else:
            raw_headers = [(k.lower().encode("latin-1"), v.encode("latin-1")) for k, v in headers.items()]
            keys = [k for k, _ in raw_headers]
            has_content_length = b"content-length" in keys
            has_content_type = b"content-type" in keys

        if not has_content_type:
            content_type = self.media_type
            if self.media_type.startswith("text/"):
                content_type += "; charset=utf-8"
            raw_headers.append((b"content-type", content_type.encode("latin-1")))
        if not has_content_length:
            raw_headers.append((b"content-length", str(len(self.body)).encode("latin-1")))

        if self.cookies is not None and self.cookies.has_new:
            for cookie in self.cookies.new:
                raw_headers.append((b"set-cookie", cookie.output(header="").strip().encode("latin-1")))

        return raw_headers

    @staticmethod
    def json(
        data: Any,
        status=200,
        headers: Headers | None = None,
        cookies: Cookies | None = None,
    ) -> Response:
        return Response(
            body=to_json(
                data,
                ensure_ascii=False,
                allow_nan=False,
                separators=(",", ":"),
            ),
            status=status,
            media_type="application/json",
            headers=headers,
            cookies=cookies,
        )

    @staticmethod
    def html(
        content: str,
        status=200,
        headers: Headers | None = None,
        cookies: Cookies | None = None,
    ) -> Response:
        return Response(
            body=content,
            status=status,
            media_type="text/html",
            headers=headers,
            cookies=cookies,
        )

    async def send(self, send_callable: Send):
        await send_callable(
            {
                "type": "http.response.start",
                "status": self.status,
                "headers": self.raw_headers,
            }
        )
        await send_callable({"type": "http.response.body", "body": self.body})

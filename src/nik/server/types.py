from collections.abc import Awaitable, Callable, Iterable, Mapping, MutableMapping
from typing import Any, Literal, TypedDict

Headers = Mapping[str, str]
Permissions = dict[str, Any]
RawHeaders = Iterable[tuple[bytes, bytes]]


class Scope(TypedDict):
    type: Literal["http", "lifespan"]
    method: str
    scheme: str
    path: str
    query_string: bytes
    root_path: str
    headers: RawHeaders


Message = MutableMapping[str, Any]
Send = Callable[[Message], Awaitable[None]]
Receive = Callable[[], Awaitable[Message]]

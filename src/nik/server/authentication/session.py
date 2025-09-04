from __future__ import annotations

from typing import Generic, TypeVar

D = TypeVar("D")
U = TypeVar("U")


class Session(Generic[D, U]):
    """
    Session class is a data wrapper that holds session data and optional user information.

    Attributes
    ----------
    data: D
        Session data like user_id, user_type, etc. The data often comes from cookies, jwt tokens, etc.
    user: U
        Optional user data, typically from a database or similar source.
    """

    def __init__(self, data: D, user: U | None = None):
        self._data = data
        self._user = user

    @property
    def data(self) -> D:
        return self._data

    @property
    def user(self) -> U | None:
        return self._user

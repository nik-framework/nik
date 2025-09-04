from dataclasses import dataclass

from nik.server.authentication.session import Session


@dataclass
class User:
    id: int
    name: str


def test_session_class():
    data = {"user_id": 123, "role": "admin"}
    user = User(id=123, name="Jane")
    s = Session(data=data, user=user)

    assert s.data == data
    assert s.user == user

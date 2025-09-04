from __future__ import annotations

import base64
import hashlib
import uuid
from collections.abc import Iterable
from copy import deepcopy
from typing import Any, Generic, TypedDict, TypeVar

from .actions import UpdateState
from .context import ViewContext

T = TypeVar("T")

_sentinel = object()

ID_RANDOM_PART_LEN = 6


class State(Generic[T]):
    def __init__(self, name: str, value: T, parent: Any = None, key: str | None = None):
        self.name = name
        self.value: T = value
        self.parent = parent
        self.key = key or self._make_key()

    def update(self, value: T) -> State[T]:
        """
        Set the value of the State and return a new instance with the updated value.
        """
        new_obj = State(self.name, value, parent=self.parent, key=self.key)
        ViewContext.get_current().add_action(UpdateState(new_obj, value))
        return new_obj

    def append(self, value: Any) -> State[T]:
        """
        Append a value to the State's value if it is a list.
        """
        assert isinstance(self.value, list), "State value must be a list to append items"

        new_value = deepcopy(self.value)
        new_value.append(value)
        new_obj = State(self.name, new_value, parent=self.parent, key=self.key)
        ViewContext.get_current().add_action(UpdateState(new_obj, value, operation="append"))
        return new_obj

    def render(self):
        return str(self.value)

    def __eq__(self, other):
        if isinstance(other, State):
            return self.key == other.key
        return False

    def __bool__(self):
        return bool(self.value)

    def __hash__(self):
        return self.key.__hash__()

    def __str__(self):
        return self.value.__str__()

    def __iter__(self) -> Any:
        if isinstance(self.value, Iterable) and not isinstance(self.value, (str, bytes)):
            return iter(self.value)
        raise TypeError(f"State value of type {type(self.value).__name__} is not iterable")

    def __getitem__(self, item: str) -> State:
        if isinstance(self.value, dict):
            return State(
                name=item,
                value=self.value.get(item),
                parent=self,
                key=f"{self.key}.{item}",
            )
        raise TypeError(f"State value of type {type(self.value).__name__} is not subscriptable")

    def __setitem__(self, key: str, value: Any):
        assert isinstance(self.value, dict), "State value must be a dict to set items"

        obj = State(self.name, deepcopy(self.value), parent=self.parent, key=self.key)
        prop_state = State(
            name=key,
            value=value,
            parent=obj,
            key=f"{self.key}.{key}",
        )
        obj.value[key] = prop_state
        ViewContext.get_current().add_action(UpdateState(prop_state, value))

    def _make_key(self) -> str:
        base = f"{self.name.lower()}"
        if self.parent:
            base += f"_{self.parent.__class__.__name__.lower()}"

        return deterministic_id(base, f"sv_{base}")

    def to_json(self):
        return self.key

    def negate(self) -> State[bool]:
        return State(self.name, not self.value, parent=self.parent, key=self.key)

    def __repr__(self):
        return f"State(name={self.name}, value={self.value}, key={self.key})"


class When:
    def __init__(self, condition: State, equal_to: Any = _sentinel, not_equal_to: Any = _sentinel, do: Any = None):
        self.condition = condition
        self.result = do

        if equal_to is not _sentinel:
            self.op = "equal_to"
            self.op_value = equal_to
        elif not_equal_to is not _sentinel:
            self.op = "not_equal_to"
            self.op_value = not_equal_to
        else:
            self.op = None

    def __bool__(self) -> bool:
        if self.op == "equal_to":
            return self.condition.value == self.op_value
        elif self.op == "not_equal_to":
            return self.condition.value != self.op_value
        else:
            return bool(self.condition.value)

    def __repr__(self):
        return f"When(condition={self.condition}, result={self.result})"


class WhenNot(When):
    def __bool__(self):
        return not super().__bool__()


class Id:
    def __init__(self, value: str):
        self.value = value

    @staticmethod
    def generate(prefix: str | None = None) -> Id:
        """Generates a random ID."""
        random_part = uuid.uuid4().hex[:ID_RANDOM_PART_LEN]
        if prefix:
            return Id(f"{prefix}_{random_part}")
        return Id(random_part)

    @staticmethod
    def from_string(base: str, prefix: str | None = None) -> Id:
        """Generates a unique and deterministic ID from the base string."""
        return Id(deterministic_id(base, prefix))

    def to_json(self):
        return self.value

    def __str__(self):
        return self.value

    def __repr__(self):
        return f"Id(value={self.value})"


def deterministic_id(base: str, prefix: str | None = None) -> str:
    h = hashlib.md5(base.encode()).digest()
    id = base64.urlsafe_b64encode(h).decode("utf-8")[:ID_RANDOM_PART_LEN]
    if prefix:
        id = f"{prefix}_{id}"

    return id


class UploadedFile(TypedDict):
    name: str
    content: str
    type: str

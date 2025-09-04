from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, Literal

from .callbacks import UpdateState as UpdateStateCallback
from .context import ViewContext

if TYPE_CHECKING:
    from .callbacks import Callback
    from .data import Id, State


class Action:
    name: ClassVar[str]

    def to_action(self) -> list:
        """Convert the reactivity declaration to an action."""
        raise NotImplementedError("Subclasses must implement to_action method")

    @staticmethod
    def redirect(url: str, full: bool = True):
        ViewContext.get_current().add_action(Redirect(url, full))

    @staticmethod
    def refresh_view(partial: bool = False):
        ViewContext.get_current().add_action(RefreshView(partial))


class OnClick(Action):
    name: ClassVar[str] = "onClick"

    def __init__(self, id: Id, callback: Callback):
        self.id = id
        self.callback = callback

    def to_action(self) -> list:
        return [self.id, *self.callback.to_action()]


class RegisterObservable(Action):
    name: ClassVar[str] = "registerObservable"

    def __init__(self, value: State):
        self.value = value

    def to_action(self) -> list:
        value = self._get_root_state()
        return [value.key, value.value]

    def __hash__(self):
        value = self._get_root_state()
        return hash(value.key)

    def __eq__(self, other):
        assert isinstance(other, RegisterObservable), "Cannot compare ObservedValue with non-ObservedValue"
        result = self.value == other.value
        return result

    def _get_root_state(self) -> Any:
        """Get the value of the observable."""

        if self.value.parent is None:
            return self.value
        else:
            return self.value.parent


class SubscribeObservable(Action):
    name: ClassVar[str] = "subscribeObservable"

    def __init__(self, value: State, callback: Callback):
        self.value = value
        self.callback = callback

    def to_action(self) -> list:
        args = [self.value.key, None]
        if self.value.parent is not None:
            args = [self.value.parent.key, self.value.name]
        args.extend(self.callback.to_action())
        return args


class UpdateState(Action):
    name: ClassVar[str] = "updateState"

    def __init__(self, state: State, value: Any, operation: Literal["append"] | None = None):
        self.callback = UpdateStateCallback(state, value, operation)

    def to_action(self) -> list:
        args = self.callback.to_action()
        args.pop(0)
        return args


class Redirect(Action):
    name: ClassVar[str] = "redirect"

    def __init__(self, url: str, full: bool):
        self.url = url
        self.full = full

    def to_action(self) -> list:
        return [self.url, self.full]


class ListenSubmit(Action):
    name: ClassVar[str] = "listenSubmit"

    def __init__(self, form_id: Id, reset_after_success: bool):
        self.form_id = form_id
        self.reset_after_success = reset_after_success

    def to_action(self) -> list:
        return [self.form_id, self.reset_after_success]


class BindValue(Action):
    name: ClassVar[str] = "bindValue"

    def __init__(self, value: State, to: Id):
        self.id = to
        self.value = value

    def to_action(self) -> list:
        return [self.id, self.value.key]


class RefreshView(Action):
    name: ClassVar[str] = "refreshView"

    def __init__(self, partial: bool = False):
        self.partial = partial

    def to_action(self) -> list:
        return [self.partial]

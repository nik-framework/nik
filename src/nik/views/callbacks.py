from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, ClassVar, Literal

"""
Callback classes for handling client-side actions.
Callbacks are triggered by the actions.
They all extend to Callback and they are usually passed as attributes to the `Element`s.

**Important**
They should NOT return the name property in the to_action method.
"""


if TYPE_CHECKING:
    from .data import Id, State, When
    from .elements import Element


class Callback:
    name: ClassVar[str]

    def to_action(self) -> list:
        raise NotImplementedError("Subclasses must implement to_action method")


class UpdateState(Callback):
    name: ClassVar[str] = "updateState"

    def __init__(self, state: State, value: Any, operation: Literal["append"] | None = None):
        self.state = state
        self.value = value
        self.operation = operation

    def to_action(self) -> list:
        args: list[str | None] = [self.name]
        if self.state.parent is None:
            args.extend([self.state.key, None])
        else:
            args.extend([self.state.parent.key, self.state.name])
        args.append(self.value)
        args.append(self.operation)
        return args


class ToggleShow(Callback):
    name: ClassVar[str] = "toggleShow"

    def __init__(self, id: Id):
        self.id = id

    def to_action(self) -> list:
        return [self.name, self.id]


class ToggleClass(Callback):
    name: ClassVar[str] = "toggleClass"

    def __init__(self, elm_id: Id, when: When):
        self.elm_id = elm_id
        self.when = when

    def to_action(self) -> list:
        return [self.name, self.elm_id, self.when.op, self.when.op_value, self.when.result]


class PartialFetch(Callback):
    name: ClassVar[str] = "partialFetch"

    def __init__(self, data: dict[str, Any], url: str | None = None):
        self.data = data
        self.url = url

    def to_action(self) -> list:
        return [self.name, self.data, self.url]


class _TemplateRefDict:
    """No matter what key is given always return the name of the key."""

    def __getitem__(self, key: str) -> str:
        return "{{value." + key + "}}"

    def __getattr__(self, item: str) -> str:
        return "{{value." + item + "}}"


class InsertElements(Callback):
    name = "insertElements"

    def __init__(self, element: Element | Callable[[Any], Element], parent_id: Id):
        self.element = element
        self.parent_id = parent_id

    def to_action(self) -> list:
        pseudo_dict = _TemplateRefDict()
        if callable(self.element):
            template = self.element(pseudo_dict).render()
        else:
            template = self.element.render()

        return [self.name, template, self.parent_id]


class ReactiveAttribute(Callback):
    name: ClassVar[str] = "reactiveAttribute"

    def __init__(self, id: Id, attribute: str, when: When):
        self.id = id
        self.attribute = attribute
        self.when = when

    def to_action(self) -> list:
        return [self.name, self.id, self.attribute, self.when.__class__.__name__]


class ConsoleLog(Callback):
    name = "consoleLog"

    def __init__(self, message: str):
        self.message = message

    def to_action(self) -> list:
        return [self.name, self.message]


class UpdateFormStateClass(Callback):
    name = "updateFormStateClass"

    def __init__(
        self,
        form_id: Id,
        loading_class: str | None,
        error_class: str | None,
    ):
        assert loading_class or error_class, "At least one of loading_class or error_class must be provided"

        self.form_id = form_id
        self.loading_class = loading_class
        self.error_class = error_class

    def to_action(self) -> list:
        return [self.name, self.form_id, self.loading_class, self.error_class]

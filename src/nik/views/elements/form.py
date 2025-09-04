from __future__ import annotations

from typing import Any

from ..actions import BindValue, ListenSubmit, RegisterObservable, SubscribeObservable
from ..callbacks import Callback, UpdateFormStateClass
from ..context import ViewContext
from ..data import (
    Id,
    State,
    When,
)
from .base import Children, Classes, Element, IdArg, get_id


class Form(Element):
    def __init__(
        self,
        *args: Children,
        method: str = "post",
        errors: State | None = None,
        reset_after_success: bool = False,
        loading_class: str | None = None,
        error_class: str | None = None,
        id: IdArg = None,
        toggle_class: When | None = None,
        show: When | bool | None = None,
        on_click: Callback | None = None,
        children: Children | None = None,
        classes: Classes | None = None,
        **kwargs,
    ):
        self.method = method
        self.loading_class = loading_class
        self.error_class = error_class
        self.errors = errors
        self.reset_after_success = reset_after_success

        kwargs["method"] = method

        should_generate_id = isinstance(errors, State)
        id = get_id(id, should_generate_id)

        super().__init__(
            *args,
            tag="form",
            id=id,
            toggle_class=toggle_class,
            show=show,
            on_click=on_click,
            children=children,
            classes=classes,
            **kwargs,
        )

        if self.id:
            ViewContext.get_current().add_action(ListenSubmit(self.id, self.reset_after_success))

            if self.loading_class or self.error_class:
                form_state = State(f"{self.id}_form_state", "ready", key=f"{self.id}_form_state")
                ViewContext.get_current().add_action(RegisterObservable(form_state))
                ViewContext.get_current().add_action(
                    SubscribeObservable(form_state, UpdateFormStateClass(self.id, self.loading_class, self.error_class))
                )

            if self.errors is not None:
                ViewContext.get_current().add_action(RegisterObservable(self.errors))


class Input(Element):
    def __init__(
        self,
        *args,
        type: str = "text",
        value: State | str | None = None,
        required: bool | None = None,
        disabled: bool | When | None = None,
        id: IdArg = None,
        toggle_class: When | None = None,
        show: When | bool | None = None,
        classes: Classes | None = None,
        **kwargs,
    ):
        self.value = value

        if type is not None:
            kwargs["type"] = type
        if required is not None:
            kwargs["required"] = required
        if disabled is not None:
            kwargs["disabled"] = disabled
        if value is not None:
            kwargs["value"] = str(value)

        should_generate_id = isinstance(value, State)
        id = get_id(id, should_generate_id)

        super().__init__(
            *args,
            tag="input",
            is_void=True,
            id=id,
            toggle_class=toggle_class,
            show=show,
            classes=classes,
            **kwargs,
        )

        self._bind_value()

    def _bind_value(self):
        if self.value is None or not isinstance(self.value, State):
            return

        assert self.id, "Binding value without an id"

        no_on_change_types = ("checkbox", "radio", "submit", "reset", "button")
        if self.attributes["type"] in no_on_change_types:
            raise ValueError(
                f"Cannot bind value to an input of type '{self.attributes['type']}'. "
                "These types do not support on_change events."
            )

        ViewContext.get_current().add_action(RegisterObservable(self.value))
        ViewContext.get_current().add_action(BindValue(self.value, to=self.id))


class Checkbox(Input):
    def __init__(
        self,
        checked: State | Any | None = None,
        required: bool = False,
        id: IdArg = None,
        classes: Classes | None = None,
        auto_save: bool = False,
        toggle_class: When | None = None,
        show: When | bool | None = None,
        **kwargs,
    ):
        value = None
        if checked is not None:
            kwargs["checked"] = bool(checked)
            value = checked

        super().__init__(
            type="checkbox",
            required=required,
            id=id,
            classes=classes,
            auto_save=auto_save,
            value=value,
            toggle_class=toggle_class,
            show=show,
            **kwargs,
        )


class Button(Element):
    def __init__(
        self,
        *args: Children,
        type: str | None = None,
        id: IdArg = None,
        classes: Classes | None = None,
        children: Children | None = None,
        toggle_class: When | None = None,
        show: When | bool | None = None,
        on_click: Callback | None = None,
        **kwargs,
    ):
        if type is not None:
            kwargs["type"] = type

        super().__init__(
            *args,
            tag="button",
            id=id,
            classes=classes,
            children=children,
            toggle_class=toggle_class,
            show=show,
            on_click=on_click,
            **kwargs,
        )


class Label(Element):
    def __init__(
        self,
        *args: Children,
        for_: Id | str | None = None,
        id: IdArg = None,
        classes: Classes | None = None,
        children: Children | None = None,
        toggle_class: When | None = None,
        show: When | bool | None = None,
        **kwargs,
    ):
        if for_ is not None:
            kwargs["for"] = for_

        super().__init__(
            *args,
            tag="label",
            id=id,
            classes=classes,
            children=children,
            toggle_class=toggle_class,
            show=show,
            **kwargs,
        )

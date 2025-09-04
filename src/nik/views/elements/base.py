from __future__ import annotations

from collections.abc import Callable, Iterable
from copy import deepcopy
from typing import Any, TypeVar, Union

from ..actions import OnClick, RegisterObservable, SubscribeObservable
from ..callbacks import (
    Callback,
    InsertElements,
    ReactiveAttribute,
    ToggleClass,
    ToggleShow,
)
from ..context import ViewContext
from ..data import (
    Id,
    State,
    When,
)

IdArg = Id | str | None
Child = Union["HtmlElement", "PseudoElement", str]
Children = Child | list[Union[Child, "Children"]]
Classes = str | list[str]
ItemsType = TypeVar("ItemsType", bound=Iterable[Any])
AttributeValueType = str | When | Id | State | bool | None


def get_id(id: IdArg, generate: bool = False):
    if not id:
        if generate:
            return Id.generate("el")

        return None

    if isinstance(id, str):
        id = Id(id)

    if isinstance(id, Id):
        return id


def classes_to_list(classes: Classes) -> list[str]:
    if isinstance(classes, str):
        return classes.strip().split()
    elif isinstance(classes, list):
        return [c.strip() for c in classes]


class Style:
    def __init__(self, name: str, value: str):
        self.name = name
        self.value = value

    def render(self):
        return f"{self.name}: {self.value};"

    def to_json(self):
        return {"name": self.name, "value": self.value}


class HtmlElement:
    def __init__(
        self,
        tag: str,
        is_void: bool = False,
        attributes: dict[str, AttributeValueType] | None = None,
        children: Children | None = None,
    ):
        self.tag = tag
        self.is_void = is_void
        self.attributes = attributes if attributes is not None else {}

        if children is None:
            children = []
        elif not isinstance(children, list):
            children = [children]

        self.children: list[Children] = []
        for child in children:
            self.add_child(child)

    def add_child(self, child: Children):
        if isinstance(child, list):
            for c in child:
                self.add_child(c)
        elif isinstance(child, (HtmlElement, str)):
            self.children.append(child)

    def _render_attributes(self):
        for key, value in self.attributes.items():
            yield self._render_attribute(key, value)

    def _render_attribute(self, key: str, value: AttributeValueType):
        if isinstance(value, (bool, State, When)):
            return f"{key}" if value else ""
        elif isinstance(value, (str, Id)):
            return f'{key}="{value}"' if value else ""
        elif value is None:
            return ""
        else:
            return f"{key}={value}"

    def render(self):
        if isinstance(self, PseudoElement):
            return self._render_child(self.children)

        attributes_str = " ".join(self._render_attributes()).strip()

        if self.is_void:
            if len(self.children) > 0:
                raise ValueError(f"Void tags '{self.tag}' cannot have children.")

            return f"<{self.tag} {attributes_str}>"

        children_html = ""
        if len(self.children) > 0:
            children_html = "".join(self._render_child(child) for child in self.children)

        opening = f"<{self.tag} {attributes_str}".strip()

        return f"{opening}>{children_html}</{self.tag}>"

    def _render_child(self, child: Children | HtmlElement | str) -> str:
        if isinstance(child, str):
            return child
        elif isinstance(child, HtmlElement):
            return child.render()
        elif isinstance(child, PseudoElement):
            return ""

        return "".join(self._render_child(c) for c in child)

    def __deepcopy__(self, memo):
        new_element = HtmlElement(
            tag=self.tag,
            is_void=self.is_void,
            attributes=self.attributes.copy(),
            children=deepcopy(self.children, memo),
        )
        return new_element


class Element(HtmlElement):
    def __init__(
        self,
        *args: Children,
        tag: str,
        is_void: bool = False,
        id: IdArg = None,
        toggle_class: When | None = None,
        show: When | bool | None = None,
        on_click: Callback | None = None,
        children: Children | None = None,
        classes: Classes | None = None,
        **kwargs,
    ):
        if args:
            if children is not None:
                raise ValueError("Cannot specify both positional arguments and children keyword argument")
            children = list(args)

        if children is not None and not isinstance(children, list):
            children = [children]

        if is_void and children is not None and len(children) > 0:
            raise ValueError(f"Void tags '{self.tag}' cannot have children.")

        self.toggle_class = toggle_class
        self.show = show
        self.on_click = on_click

        attributes = {**kwargs}

        should_generate_id = toggle_class is not None or show is not None or on_click is not None
        self.id = get_id(id, should_generate_id)
        if self.id:
            attributes["id"] = str(self.id)

        classes = self._toggle_class(classes)
        if len(classes) > 0:
            attributes["class"] = " ".join(classes)

        show_style = self._show()
        if show_style:
            if "style" in attributes:
                attributes["style"] += (" " + show_style.render()).strip()
            else:
                attributes["style"] = show_style.render()

        self._on_click()
        self._reactive_attributes(attributes)

        super().__init__(tag=tag, is_void=is_void, attributes=attributes, children=children)

    def _toggle_class(self, classes: Classes | None = None) -> list[str]:
        classes = classes_to_list(classes) if classes else []

        if self.toggle_class is None:
            return classes

        assert self.id, "toggle_class parameter given without an id"

        if self.toggle_class:
            classes.append(self.toggle_class.result)
        elif self.toggle_class.result in classes:
            classes.remove(self.toggle_class.result)

        ViewContext.get_current().add_action(RegisterObservable(self.toggle_class.condition))
        ViewContext.get_current().add_action(
            SubscribeObservable(self.toggle_class.condition, ToggleClass(self.id, self.toggle_class))
        )

        return classes

    def _show(self) -> Style | None:
        if self.show is None:
            return None

        assert self.id, "show parameter given without an id"

        style = None
        if not self.show:
            style = Style("display", "none")
        elif isinstance(self.show, When):
            ViewContext.get_current().add_action(RegisterObservable(self.show.condition))
            ViewContext.get_current().add_action(SubscribeObservable(self.show.condition, ToggleShow(self.id)))

        return style

    def _on_click(self):
        if self.on_click is None:
            return
        assert self.id, "on_click parameter given without an id"

        ViewContext.get_current().add_action(OnClick(self.id, self.on_click))

    def _reactive_attributes(self, attributes: dict[str, str | When]):
        for key, value in attributes.items():
            if isinstance(value, When):
                assert self.id, f"Reactive attribute '{key}' given without an id"
                ViewContext.get_current().add_action(RegisterObservable(value.condition))
                ViewContext.get_current().add_action(
                    SubscribeObservable(value.condition, ReactiveAttribute(self.id, key, value))
                )


class Fragment(Element):
    def __init__(self, *args: Children, id: IdArg, children: Children | None = None):
        super().__init__(*args, tag="fragment", id=id, children=children)


class PseudoElement(HtmlElement):
    def __init__(self, tag: str, children: Children | None = None):
        super().__init__(tag=tag, is_void=False, children=children)


class ForEach(PseudoElement):
    def __init__(self, items: State[ItemsType], element: Element | Callable[[Any], Element], parent: Id | None = None):
        self.items = items
        self.element = element
        self.parent = parent

        children = []

        if items:
            if callable(element):
                children.extend(element(item) for item in items)
            else:
                children.extend(deepcopy(element) for _ in items)

        super().__init__(tag="for-each", children=children)

        if parent:
            ViewContext.get_current().add_action(RegisterObservable(self.items))
            ViewContext.get_current().add_action(
                SubscribeObservable(self.items, InsertElements(self.element, parent_id=parent))
            )

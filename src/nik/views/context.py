from __future__ import annotations

from typing import Any, ClassVar, Protocol


class Actionable(Protocol):
    name: ClassVar[str]

    def to_action(self) -> list:
        raise NotImplementedError("Subclasses must implement to_action method")


class Page:
    def __init__(self, path: str, loading: bool = False, error: bool = False, title: str = "Nik Framework"):
        self.path = path
        self.title = title

        self.loading = loading
        self.error = error

    def to_json(self):
        return {"loading": self.loading, "error": self.error}


Actions = dict[str, set[Actionable]]


class ViewContext:
    _current_context: ClassVar[ViewContext | None] = None

    def __init__(self, page: Page | None = None):
        self.page = page
        self.actions: Actions = {}

    @classmethod
    def get_current(cls) -> ViewContext:
        if cls._current_context is None:
            raise RuntimeError("No active ViewContext")
        return cls._current_context

    def add_action(self, action: Actionable):
        if action.name not in self.actions:
            self.actions[action.name] = set()
        self.actions[action.name].add(action)

    def get_actions(self) -> list[Any] | None:
        if not self.actions:
            return None

        prioritized_keys = ["registerObservable", "subscribeObservable"]
        prioritized_actions = []
        other_actions = []

        for name, actions in self.actions.items():
            action_list = [action.to_action() for action in actions]
            if name in prioritized_keys:
                prioritized_actions.append([name, *action_list])
            else:
                other_actions.append([name, *action_list])

        return prioritized_actions + other_actions

    def __enter__(self):
        self._previous_context = ViewContext._current_context
        ViewContext._current_context = self
        return self

    def __exit__(self, *args):
        ViewContext._current_context = self._previous_context

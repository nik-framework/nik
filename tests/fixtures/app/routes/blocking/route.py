import time

from nik.views.actions import Action
from nik.views.elements import Div


def action():
    # Simulate blocking synchronous work
    time.sleep(0.25)
    # Collect an action to verify context propagation inside threads
    Action.refresh_view(partial=True)
    # No explicit return; ActionRenderer will produce actions payload from ViewContext


def view():
    # Simulate blocking synchronous work
    time.sleep(0.25)
    return Div("Blocking sync view")

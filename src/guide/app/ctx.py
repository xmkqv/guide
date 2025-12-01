from contextvars import ContextVar
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from guide.app.pages.mission import Controller

controller = ContextVar[Controller]("controller")


def use_controller() -> Controller:
    """Get the current controller from context."""
    c = controller.get()
    assert c is not None, "No controller in context"
    return c


def set_controller(c: Controller) -> None:
    """Set the current controller in context."""
    controller.set(c)

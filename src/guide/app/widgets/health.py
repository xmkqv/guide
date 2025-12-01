"""Health status widget."""

import flet as ft
from fletx.core import FletXWidget
from fletx.decorators import obx

from guide.app.ctx import use_controller
from guide.app.widgets.utils import render_badge


class HealthWidget(FletXWidget):
    def __init__(self) -> None:
        self.ctrl = use_controller()
        super().__init__()

    @property
    def health(self) -> str:
        if self.ctrl.error:
            return "failing"
        return "healthy"

    @obx
    def build(self) -> ft.Control:
        color = ft.Colors.GREY_800
        match self.health:
            case "healthy":
                color = ft.Colors.GREEN_900
            case "failing":
                color = ft.Colors.RED_900
            case _:
                pass
        return render_badge(self.health, color)

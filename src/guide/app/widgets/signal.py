"""Signal/test results visualization widget."""

from typing import TYPE_CHECKING

import flet as ft
from fletx.core import FletXWidget
from fletx.decorators import obx

from guide.app.ctx import use_controller
from guide.signal import Test

if TYPE_CHECKING:
    from guide.mission import Mission


class Signal(FletXWidget):
    @obx
    def build(self) -> ft.Control:
        c = use_controller()

        return ft.Column(
            [
                ft.Text("Signal", size=20, weight=ft.FontWeight.BOLD),
                ft.Text("Recent Tests", size=14, color=ft.Colors.GREY_500),
                ft.Column(
                    [_build_test(t, c.mission) for t in c.mission.signal], spacing=2
                ),
            ],
            spacing=12,
        )


def _build_test(test: Test, mission: Mission) -> ft.Control:
    data = test.data or {}
    outcome = data.get("outcome", "unknown")
    ts = (
        (data.get("timestamp", "")[:19].replace("T", " "))
        if data.get("timestamp")
        else ""
    )
    dur = f"{data['duration']:.3f}s" if data.get("duration") else ""

    spec = next((s for s in mission.design if s.id == test.ref), None)
    spec_name = spec.name if spec else test.ref

    outcome_color = (
        ft.Colors.GREEN_900
        if outcome == "passed"
        else ft.Colors.RED_900
        if outcome == "failed"
        else ft.Colors.GREY_800
    )

    return ft.Container(
        ft.Row(
            [
                ft.Text(ts, size=11, color=ft.Colors.GREY_500, width=140),
                ft.Container(
                    ft.Text(test.id, size=11),
                    bgcolor=ft.Colors.ORANGE_900,
                    padding=ft.padding.symmetric(horizontal=8, vertical=2),
                    border_radius=4,
                    border=ft.border.all(1, ft.Colors.GREY_700),
                ),
                ft.Container(
                    ft.Text(outcome, size=11),
                    bgcolor=outcome_color,
                    padding=ft.padding.symmetric(horizontal=8, vertical=2),
                    border_radius=4,
                ),
                ft.Text(spec_name, size=12, expand=True),
                ft.Text(dur, size=11, color=ft.Colors.GREY_500),
            ],
            spacing=8,
        ),
        padding=ft.padding.symmetric(vertical=4),
        border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_900)),
    )

"""Design tree visualization widget."""

import flet as ft
from fletx.core import FletXWidget
from fletx.decorators import obx

from guide.app.ctx import use_controller
from guide.design import Spec


class Design(FletXWidget):
    def __init__(self) -> None:
        super().__init__()

    @obx
    def build(self) -> ft.Control:
        ctrl = use_controller()
        specs = [_build_spec(_) for _ in ctrl.mission.design]
        return ft.Column(specs, spacing=12)


def _build_spec(spec: Spec) -> ft.Control:
    detail = spec.detail or {}
    detail_parts: list[str] = []
    if inv := detail.get("invariant"):
        detail_parts.append(f"invariant: {inv}")
    if con := detail.get("constraint"):
        detail_parts.append(f"constraint: {con}")

    controls: list[ft.Control] = [
        ft.Row(
            [
                ft.Container(
                    ft.Text(spec.id, size=11),
                    bgcolor=ft.Colors.BLUE_900,
                    padding=ft.padding.symmetric(horizontal=8, vertical=2),
                    border_radius=4,
                ),
                ft.Text(spec.name, weight=ft.FontWeight.W_500),
            ],
            spacing=8,
        ),
    ]
    if detail_parts:
        controls.append(
            ft.Text(" | ".join(detail_parts), size=11, color=ft.Colors.GREY_500)
        )

    return ft.Container(
        ft.Column(controls, spacing=4),
        bgcolor=ft.Colors.GREY_900,
        padding=ft.padding.only(left=12, top=10, right=12, bottom=10),
        border_radius=8,
        border=ft.border.only(left=ft.BorderSide(3, ft.Colors.BLUE_900)),
    )

import flet as ft
from fletx.core import FletXWidget
from fletx.decorators import obx


class Header(FletXWidget):
    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__()

    @obx
    def build(self):
        return ft.Container(
            ft.Row(
                [
                    ft.Column(
                        [ft.Text(self.name, size=28, weight=ft.FontWeight.BOLD)],
                        spacing=4,
                    ),
                    ft.Row(
                        [
                            ft.Container(
                                ft.Text("healthy", size=11),
                                bgcolor=ft.Colors.GREEN_900,
                                padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                border_radius=4,
                            ),
                        ],
                        spacing=8,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.only(bottom=20),
            border=ft.border.only(bottom=ft.BorderSide(2, ft.Colors.GREY_800)),
        )

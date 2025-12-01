"""Metrics display widget."""

from typing import TypedDict, Unpack

import flet as ft
from fletx.core import FletXWidget
from fletx.decorators import obx


class MetricsWidget(FletXWidget):
    def __init__(self) -> None:
        self.widgets: list[MetricWidget] = []
        super().__init__()

    def append(self, /, **metric: Unpack[Metric]) -> None:
        self.widgets.append(MetricWidget(**metric))

    @obx
    def build(self) -> ft.Control:
        return ft.Row([w.build() for w in self.widgets], spacing=10)


class Metric(TypedDict):
    label: str
    count: int
    bg: str


class MetricWidget(FletXWidget):
    def __init__(self, *, label: str, count: int, bg: str) -> None:
        self.label = label
        self.count = count
        self.bg = bg
        super().__init__()

    @obx
    def build(self) -> ft.Control:
        return ft.Container(
            ft.Column(
                [
                    ft.Text(self.label, size=12, color=ft.Colors.GREY_500),
                    ft.Text(str(self.count), size=24, weight=ft.FontWeight.BOLD),
                ],
                spacing=4,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=self.bg,
            padding=20,
            border_radius=8,
            expand=1,
        )

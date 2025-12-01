"""Application entry point."""

import flet as ft
from fletx.core import FletXController, FletXPage, RxInt

from guide.app import widgets
from guide.app.ctx import set_controller
from guide.app.errors import SyncError
from guide.design import Spec
from guide.mission import Mission


class Page(FletXPage):
    def __init__(self, mission: Mission) -> None:
        c = Controller(mission)
        set_controller(c)

        self.header = widgets.header.Header(c.mission.name)
        self.design = widgets.design.Design()
        self.signal = widgets.signal.Signal()

        self.metrics = widgets.metrics.MetricsWidget()
        self.metrics.append(
            label="Specs", count=len(c.mission.design), bg=ft.Colors.BLUE_900
        )
        self.metrics.append(
            label="Tests", count=len(c.mission.signal), bg=ft.Colors.ORANGE_900
        )

        super().__init__()

    @obx
    def build(self) -> ft.Control:
        return ft.SafeArea(
            ft.Column(
                [
                    self.header.build(),
                    self.metrics.build(),
                    ft.Row(
                        [
                            self.design.build(),
                            self.signal.build(),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    ),
                ],
                spacing=20,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),
            expand=True,
        )


class Controller(FletXController):
    def __init__(self, mission: Mission) -> None:
        self.mission: Mission = mission
        self.error: SyncError | None = None
        self.refresh_trigger: RxInt = RxInt(0)
        super().__init__()

    def sync(self) -> None:
        """Sync test results and refresh."""
        self.mission = self.mission.sync()
        self.refresh_trigger.increment()

    def find_spec(self, spec_id: str) -> Spec | None:
        """Find spec by id in flat design list."""
        for spec in self.mission.design:
            if spec.id == spec_id:
                return spec
        return None

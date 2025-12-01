import flet as ft

from guide.app import pages
from guide.mission import Mission


def main():
    mission: Mission = Mission.load_nearest()
    page = pages.mission.Page(mission)
    page.width = 900
    page.height = 700
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE)
    page.theme_mode = ft.ThemeMode.DARK
    ft.app(target=page)


if __name__ == "__main__":
    main()

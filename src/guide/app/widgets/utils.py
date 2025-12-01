import flet as ft


def render_badge(text: str, bg: str, border: bool = False) -> ft.Control:
    return ft.Container(
        ft.Text(text, size=11),
        bgcolor=bg,
        padding=ft.padding.symmetric(horizontal=8, vertical=2),
        border_radius=4,
        border=ft.border.all(1, ft.Colors.GREY_700) if border else None,
    )


def render_empty(msg: str) -> ft.Control:
    """Render empty state message."""
    return ft.Text(msg, color=ft.Colors.GREY_500)

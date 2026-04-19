import tkinter as tk
from typing import Callable, Optional

from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold


def create_option_menu(
    parent: tk.Widget,
    options: list[str],
    variable: Optional[tk.StringVar] = None,
    *,
    width: int = 10,
    font_size: int = 10,
    cursor: str = "hand2",
    on_change: Optional[Callable[[str], None]] = None,
    bg: Optional[str] = None,
    fg: Optional[str] = None,
    active_bg: Optional[str] = None,
    active_fg: Optional[str] = None,
) -> tuple[tk.OptionMenu, tk.StringVar]:
    """
    Create a styled OptionMenu dropdown matching the filter bar style.

    Args:
        parent:     Parent widget.
        options:    List of string options to display.
        variable:   Existing StringVar to bind to. A new one is created if
                    omitted; its initial value is set to the first option.
        width:      Character-unit width. Default is 14.
        font_size:  Font size for both the field and the popup menu.
        cursor:     Cursor to show on hover.
        on_change:  Optional callback called with the new value whenever
                    the selection changes.
        bg:         Background color. Defaults to colors["secondary-400"].
        fg:         Foreground color. Defaults to colors["primary-50"].
        active_bg:  Active background color. Defaults to colors["secondary-500"].
        active_fg:  Active foreground color. Defaults to colors["primary-50"].

    Returns:
        tuple[tk.OptionMenu, tk.StringVar]: (OptionMenu widget, StringVar used for selection).
    """
    bg_color = bg or colors["secondary-400"]
    fg_color = fg or colors["primary-50"]
    active_bg_color = active_bg or colors["secondary-500"]
    active_fg_color = active_fg or colors["primary-50"]

    if variable is None:
        variable = tk.StringVar(value=options[0] if options else "")

    option_menu = tk.OptionMenu(
        parent,
        variable,
        *options,
        command=lambda val: on_change(val) if on_change else None,
    )
    option_menu.config(
        bg=bg_color,
        fg=fg_color,
        activebackground=active_bg_color,
        activeforeground=active_fg_color,
        font=quickSandBold(font_size),
        borderwidth=0,
        highlightthickness=0,
        cursor=cursor,
        width=width,
        relief="flat",
    )
    option_menu["menu"].config(
        bg=bg_color,
        fg=fg_color,
        activebackground=active_bg_color,
        activeforeground=active_fg_color,
        font=quickSandBold(font_size),
        bd=0,
    )

    return option_menu, variable

import tkinter as tk

from app.presentation.styles.colors import colors
from app.presentation.widgets.window import create_toplevel

# Todo - Change the size of the window


def exploreWindow():
    """
    This function is used to create the Explore Window.
    """

    # create the window using the reusable helper
    _exploreWindow_: tk.Toplevel = create_toplevel(
        title="🔍 Explore 🔍",
        width=573,
        height=580,
        icon_path="app/assets/PhotoShowIcon.ico",
        bg_color=colors["primary-50"],
    )

    _exploreWindow_.grab_set()

import tkinter as tk

from styles.colors import colors


def on_enter(event: tk.Event, button: tk.Button) -> None:
    """
    This function will change the background color of the button when hovering over it.

    Parameters:
        event (tk.Event): The event object from the mouse entering the button.
        button (tk.Button): The button widget to change the background color of.

    Returns:
        None
    """

    button["background"] = colors["accent-100"]


def on_leave(event: tk.Event, button: tk.Button) -> None:
    """
    This function will change the background color of the button when the mouse is not hovering over it.

    Parameters:
        event (tk.Event): The event object from the mouse leaving the button.
        button (tk.Button): The button widget to change the background color of.

    Returns:
        None
    """

    button["background"] = colors["accent-300"]

import tkinter as tk
from typing import Optional

from PIL import Image, ImageTk


def create_toplevel(
    title: str,
    width: int,
    height: int,
    icon_path: Optional[str] = None,
    bg_color: Optional[str] = None,
    parent: Optional[tk.Tk] = None,
) -> tk.Toplevel:
    """Create and return a centered Toplevel window with common configuration.

    Args:
        title: Window title.
        width: Window width in pixels.
        height: Window height in pixels.
        icon_path: Optional path to an .ico file.
        bg_color: Optional background color for the window.
        parent: Optional parent Tk window.

    Returns:
        :tk.Toplevel: Configured `tk.Toplevel` instance.
    """
    win = tk.Toplevel(parent) if parent else tk.Toplevel()
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (height / 2))
    win.geometry("%dx%d+%d+%d" % (width, height, x, y))
    win.title(title)
    if icon_path:
        try:
            win.iconbitmap(icon_path)
        except Exception:
            # icon may not be available on all platforms or path could be wrong
            pass
    win.resizable(False, False)
    if bg_color is not None:
        win.config(bg=bg_color)
    return win


def add_logo_canvas(
    window: tk.Toplevel,
    logo_path: str,
    x: int = 120,
    y: int = 20,
    width: int = 334,
    height: int = 120,
) -> tk.Canvas:
    """Add a logo canvas to the given window and return the canvas.

    If loading the image fails, an empty canvas is returned so callers
    can continue without crashing.

        Args:
            window: The Toplevel window to add the canvas to.
            logo_path: Path to the logo image file.
            x: X coordinate for the canvas placement.
            y: Y coordinate for the canvas placement.
            width: Width of the canvas.
            height: Height of the canvas.
        Returns:
            :tk.Canvas: The canvas with the logo image, or an empty canvas if loading fails.

    """
    canvas = tk.Canvas(window, height=height, width=width, highlightthickness=0)
    canvas.place(x=x, y=y)
    try:
        logo_image = Image.open(logo_path)
        logo_image = logo_image.resize((width, height))
        canvas.image = ImageTk.PhotoImage(logo_image)
        canvas.create_image(0, 0, anchor=tk.NW, image=canvas.image)
    except Exception:
        # ignore image errors, return canvas without image
        pass
    return canvas


def create_main_window(
    title: str,
    width: int,
    height: int,
    icon_path: Optional[str] = None,
    bg_color: Optional[str] = None,
) -> tk.Tk:
    """Create and return a centered Tk root window with common configuration.

    This parallels `create_toplevel` but returns a `tk.Tk` instance suitable
    for main application windows that need to own the mainloop.

    Args:
        title: Window title.
        width: Window width in pixels.
        height: Window height in pixels.
        icon_path: Optional path to an .ico file.
        bg_color: Optional background color for the window.
    Returns:
        :tk.Tk: Configured `tk.Tk` instance.

    """
    root = tk.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (height / 2))
    root.geometry("%dx%d+%d+%d" % (width, height, x, y))
    root.title(title)
    if icon_path:
        try:
            root.iconbitmap(icon_path)
        except Exception:
            # icon may not be available on all platforms or path could be wrong
            pass
    root.resizable(False, False)
    if bg_color is not None:
        root.config(bg=bg_color)
    return root

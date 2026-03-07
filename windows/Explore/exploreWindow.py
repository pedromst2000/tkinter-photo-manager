import tkinter as tk
from styles.colors import colors


# Todo - Change the size of the window



def exploreWindow(email: str):
    """
    This function is used to create the Explore Window.
    :param email: str (user email, currently unused)
    """

    # open the window
    _exploreWindow_ = tk.Toplevel()

    # centering the window
    exploreWindowWidth = 573  # width of the window
    exploreWindowHeight = 580  # height of the window

    screenWidth = _exploreWindow_.winfo_screenwidth()  # width of the screen

    screenHeight = _exploreWindow_.winfo_screenheight()  # height of the screen

    x = (screenWidth / 2) - (exploreWindowWidth / 2)  # calculate x position

    y = (screenHeight / 2) - (exploreWindowHeight / 2)  # calculate y position

    # setting the window size and position
    # %d = integer
    # %dx%d = width x height
    # %d+%d = x position + y position
    _exploreWindow_.geometry(
        "%dx%d+%d+%d" % (exploreWindowWidth, exploreWindowHeight, x, y)
    )
    _exploreWindow_.title("🔍 Explore 🔍")
    _exploreWindow_.iconbitmap("assets/PhotoShowIcon.ico")
    _exploreWindow_.resizable(0, 0)
    _exploreWindow_.config(bg=colors["primary-50"])

    _exploreWindow_.grab_set()

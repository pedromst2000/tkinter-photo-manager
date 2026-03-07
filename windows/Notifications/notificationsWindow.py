import tkinter as tk
from styles.colors import colors


# Todo - Change the size of the window



def notificationsWindow(email: str):
    """
    This function is used to display the notifications window.
    :param email: str (user email, currently unused)
    """

    # open the window
    _notificationsWindow_ = tk.Toplevel()

    # centering the window
    notificationsWindowWidth = 573  # width of the window
    notificationsWindowHeight = 580  # height of the window

    screenWidth = _notificationsWindow_.winfo_screenwidth()  # width of the screen

    screenHeight = _notificationsWindow_.winfo_screenheight()  # height of the screen

    x = (screenWidth / 2) - (notificationsWindowWidth / 2)  # calculate x position

    y = (screenHeight / 2) - (notificationsWindowHeight / 2)  # calculate y position

    # setting the window size and position
    # %d = integer
    # %dx%d = width x height
    # %d+%d = x position + y position
    _notificationsWindow_.geometry(
        "%dx%d+%d+%d" % (notificationsWindowWidth, notificationsWindowHeight, x, y)
    )
    _notificationsWindow_.title("🔔 Notifications 🔔")
    _notificationsWindow_.iconbitmap("assets/PhotoShowIcon.ico")
    _notificationsWindow_.resizable(0, 0)
    _notificationsWindow_.config(bg=colors["primary-50"])

    _notificationsWindow_.grab_set()

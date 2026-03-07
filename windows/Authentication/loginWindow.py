import tkinter as tk
from tkinter import messagebox, Canvas, Label, Entry, Button, NW
from PIL import ImageTk, Image
from models.users import login, findUserID, getUserInfo
from styles.colors import colors
from styles.fonts import quickSandBold, quickSandRegular
from windows.Home.homeWindow import homeWindow
from windows.Home.homeBannedWindow import homeBannedWindow
from windows.Authentication.registerWindow import registerWindow
from utils.widgets.input import on_focus_in, on_focus_out, on_click_outside
from utils.widgets.button import (
    on_enter as button_on_enter,
    on_leave as button_on_leave,
)
from utils.authentication.authentication import (
    checkEmail,
    togglePasswordVisibility,
    manageVisibility,
    on_enter as label_on_enter,
    on_leave as label_on_leave,
)

# global variable flags
isLogged = False  # this variable will be used to check if the user is logged or not
isNewUser = False  # this variable will be used to check if the user is new or not


def loginWindow(Window: object) -> None:
    """
    This function is used to create the login window.

    :param Window: The window of the application.

    :return: None
    """

    # open the window
    _loginWindow_ = tk.Toplevel()

    # centering the window
    loginWindowWidth = 573  # width of the window
    loginWindowHeight = 580  # height of the window

    screenWidth = _loginWindow_.winfo_screenwidth()  # width of the screen

    screenHeight = _loginWindow_.winfo_screenheight()  # height of the screen

    x = (screenWidth / 2) - (loginWindowWidth / 2)  # calculate x position

    y = (screenHeight / 2) - (loginWindowHeight / 2)  # calculate y position

    # setting the window size and position
    # %d = integer
    # %dx%d = width x height
    # %d+%d = x position + y position
    _loginWindow_.geometry("%dx%d+%d+%d" % (loginWindowWidth, loginWindowHeight, x, y))
    _loginWindow_.title("Sign In")
    _loginWindow_.iconbitmap("assets/PhotoShowIcon.ico")
    _loginWindow_.resizable(0, 0)
    _loginWindow_.config(bg=colors["primary-50"])

    canvasLogo = Canvas(_loginWindow_, height=120, width=334, highlightthickness=0)
    canvasLogo.place(x=120, y=20)

    logo_image = Image.open("assets/images/Logo_auth.png")
    logo_image = logo_image.resize((334, 120))

    canvasLogo.image = ImageTk.PhotoImage(logo_image)

    canvasLogo.create_image(0, 0, anchor=NW, image=canvasLogo.image)

    # ---------------------------

    # email icon label
    emailIcon = Image.open("assets/images/UI_Icons/Email_Icon.png")
    emailIcon = emailIcon.resize((48, 44))

    canvasEmailIcon = Canvas(_loginWindow_, height=40, width=46, highlightthickness=0)
    canvasEmailIcon.place(x=130, y=170)

    canvasEmailIcon.image = ImageTk.PhotoImage(emailIcon)

    canvasEmailIcon.create_image(0, 0, anchor=NW, image=canvasEmailIcon.image)

    # ---------------------------

    # password icon label
    passwordIcon = Image.open("assets/images/UI_Icons/Password_Icon.png")
    passwordIcon = passwordIcon.resize((48, 44))

    canvasPasswordIcon = Canvas(
        _loginWindow_, height=40, width=46, highlightthickness=0
    )
    canvasPasswordIcon.place(x=130, y=280)

    canvasPasswordIcon.image = ImageTk.PhotoImage(passwordIcon)
    canvasPasswordIcon.create_image(0, 0, anchor=NW, image=canvasPasswordIcon.image)

    # ---------------------------

    emailLabel = Label(
        _loginWindow_,
        text="email",
        font=quickSandBold(14),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    )
    emailLabel.place(x=175, y=190, anchor="w")

    # ---------------------------
    passwordLabel = Label(
        _loginWindow_,
        text="password",
        font=quickSandBold(14),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    )
    passwordLabel.place(x=175, y=302, anchor="w")

    # ---------------------------

    inputEmail = Entry(
        _loginWindow_,
        width=30,
        borderwidth=0,
        font=quickSandBold(12),
        bg=colors["secondary-300"],
        fg=colors["secondary-500"],
        highlightthickness=0,
        cursor="xterm",
    )

    inputEmail.place(x=140, y=220)
    inputEmail.bind("<FocusIn>", lambda e: on_focus_in(e, inputEmail))
    inputEmail.bind("<FocusOut>", lambda e: on_focus_out(e, inputEmail))
    # ---------------------------

    inputPassword = Entry(
        _loginWindow_,
        width=30,
        borderwidth=0,
        font=quickSandBold(12),
        bg=colors["secondary-300"],
        fg=colors["secondary-500"],
        highlightthickness=0,
        show="*",
        cursor="xterm",
    )
    inputPassword.place(x=140, y=330)
    inputPassword.bind("<FocusIn>", lambda e: on_focus_in(e, inputPassword))
    inputPassword.bind("<FocusOut>", lambda e: on_focus_out(e, inputPassword))

    # ---------------------------
    #  manage password
    canvasManagePassword = Canvas(
        _loginWindow_, height=36, width=50, highlightthickness=0, cursor="hand2"
    )

    canvasManagePassword.config(highlightthickness=0, bd=0, bg=colors["primary-50"])

    # bind - when the user releases the key (onKeyPress), the function will be called
    inputPassword.bind(
        "<KeyRelease>",
        lambda event: manageVisibility(
            ImageTk, Image, canvasManagePassword, NW, inputPassword, 445, 325
        ),
    )

    # bind - when the user clicks (onClick) on the canvas, the function will be called
    canvasManagePassword.bind(
        "<Button-1>",
        lambda event: togglePasswordVisibility(
            ImageTk, Image, canvasManagePassword, NW, inputPassword, 445, 325
        ),
    )

    # ---------------------------

    labelInfo = tk.Label(
        _loginWindow_,
        text="Don't have an account? Sign up!",
        font=quickSandRegular(12),
        bd=0,
        bg=colors["primary-50"],
        highlightthickness=0,
        fg=colors["secondary-500"],
        cursor="hand2",
    )
    labelInfo.place(x=162, y=409)
    labelInfo.bind("<Enter>", lambda e: label_on_enter(e, labelInfo))
    labelInfo.bind("<Leave>", lambda e: label_on_leave(e, labelInfo))
    labelInfo.bind(
        "<Button-1>",
        lambda event: openSignUpLink(event, _loginWindow_, Window),
    )

    # ---------------------------

    btnSignIn = Button(
        _loginWindow_,
        width=24,
        height=2,
        text="Sign In",
        borderwidth=10,
        font=quickSandBold(13),
        background=colors["accent-300"],
        bd=0,
        highlightthickness=0,
        activebackground=colors["accent-100"],
        cursor="hand2",
    )

    btnSignIn.place(x=164, y=475)
    # Hoover effect on the button
    btnSignIn.bind("<Enter>", lambda e: button_on_enter(e, btnSignIn))
    btnSignIn.bind("<Leave>", lambda e: button_on_leave(e, btnSignIn))

    _loginWindow_.bind(
        "<Button-1>",
        lambda e: on_click_outside(e, _loginWindow_, inputEmail, inputPassword),
    )

    def trigger_check_login(event=None):
        """
        Helper function to trigger the login check using the current input values.
        Can be called by button click or Enter key event.

        :param event: Optional event object from Tkinter (default: None)
        :return: None
        """
        checkLogin(inputEmail.get(), inputPassword.get(), _loginWindow_, Window)

    # Bind button click
    btnSignIn.bind("<Button-1>", trigger_check_login)
    # Bind Enter key (Return) to window
    _loginWindow_.bind("<Return>", trigger_check_login)

    _loginWindow_.grab_set()


def checkLogin(email: str, password: str, loginWindow: object, Window: object) -> None:
    global isLogged, isNewUser

    """
    This function will check if the user exists in the database.
    
    :param email: str
    :param password: str
    :param loginWindow: object
    :param Window: object
    
    :return: None
    """

    if email == "" or password == "":
        return messagebox.showerror(
            "Error", "Email and password are required", parent=loginWindow
        )

    elif (
        checkEmail(email) == False
    ):  # checking with the util function if the email is valid
        return messagebox.showerror("Error", "Invalid email", parent=loginWindow)

    # this function returns the user if the email and password are correct, otherwise returns None
    user = login(email, password)
    userID = findUserID(email)
    userPayload = getUserInfo(userID)

    if user == None:  # if the user doesn't exist
        messagebox.showerror("Error", "Invalid Credentials", parent=loginWindow)

    elif user != None:  # if the user exists
        messagebox.showinfo(
            "Success", f"Welcome back {user['username']}", parent=loginWindow
        )

        isLogged = True
        isNewUser = False

        loginWindow.destroy()  # destroy the login window
        Window.destroy()
        (
            homeWindow(email, isLogged, isNewUser)
            if userPayload["isBlocked"] == False
            else homeBannedWindow(email)
        )


def openSignUpLink(event: object, loginWindow: object, window: object) -> None:
    """
    This function will open the sign up window through the login window.

    :param event: object
    :param loginWindow: object
    :param window: object

    :return: None
    """
    loginWindow.destroy()
    registerWindow(window)

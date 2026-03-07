import tkinter as tk
from PIL import ImageTk, Image
from windows.Explore.exploreWindow import exploreWindow
from windows.Profile.profileWindow import profileWindow
from windows.Notifications.notificationsWindow import notificationsWindow
from windows.Dashboard.dashboardWindow import dashboardWindow
from windows.Manage.manageWindow import manageWindow
from windows.Settings.settingsWindow import settingsWindow


class menu:
    def __init__(
        self,
        homeCanvas: tk.Canvas = None,
        homeWindow: tk.Tk = None,
    ) -> None:
        """
        This class is used to create the menu options.
        :param homeCanvas: tk.Canvas
        :param homeWindow: tk.Tk

        :return: None

        """

        # global variables
        self.homeCanvas = homeCanvas
        self.homeWindow = homeWindow
        self.gap = 50
        self.posAdminMenuX = 130
        self.posRegularMenuX = 300
        self.posMenuY = 310
        self.isAdminOpt = False

        # ------------------------------------------------------
        self.exploreImg = ImageTk.PhotoImage(
            Image.open("assets/images/home/menu/explore.png")
        )

        self.profileImg = ImageTk.PhotoImage(
            Image.open("assets/images/home/menu/profile.png")
        )
        self.notificationsImg = ImageTk.PhotoImage(
            Image.open("assets/images/home/menu/notifications.png")
        )

        self.settingsImg = ImageTk.PhotoImage(
            Image.open("assets/images/home/menu/settings.png")
        )

        self.manageImg = ImageTk.PhotoImage(
            Image.open("assets/images/home/menu/manage.png")
        )

        self.dashboardImg = ImageTk.PhotoImage(
            Image.open("assets/images/home/menu/dashboard.png")
        )
        self.signOutImg = ImageTk.PhotoImage(
            Image.open("assets/images/home/menu/signOut.png")
        )

        # -----------------------------------------------------

        #   menu buttons
        exploreOptButton = tk.Button(
            self.homeCanvas,
            image=self.exploreImg,
            width=113,
            height=120,
            cursor="hand2",
            borderwidth=0,
            highlightthickness=0,
        )

        profileOptButton = tk.Button(
            self.homeCanvas,
            image=self.profileImg,
            width=113,
            height=120,
            cursor="hand2",
            borderwidth=0,
            highlightthickness=0,
        )

        notificationsOptButton = tk.Button(
            self.homeCanvas,
            image=self.notificationsImg,
            width=113,
            height=120,
            cursor="hand2",
            borderwidth=0,
            highlightthickness=0,
        )

        settingsOptButton = tk.Button(
            self.homeCanvas,
            image=self.settingsImg,
            width=113,
            height=120,
            cursor="hand2",
            borderwidth=0,
            highlightthickness=0,
        )

        manageOptButton = tk.Button(
            self.homeCanvas,
            image=self.manageImg,
            width=113,
            height=120,
            cursor="hand2",
            borderwidth=0,
            highlightthickness=0,
        )

        dashboardOptButton = tk.Button(
            self.homeCanvas,
            image=self.dashboardImg,
            width=113,
            height=120,
            cursor="hand2",
            borderwidth=0,
            highlightthickness=0,
        )

        signOutOptButton = tk.Button(
            self.homeCanvas,
            image=self.signOutImg,
            width=113,
            height=120,
            cursor="hand2",
            borderwidth=0,
            highlightthickness=0,
        )

        # render the menu options

        self.menuOpts = {
            "regular": [
                exploreOptButton,
                profileOptButton,
                notificationsOptButton,
                dashboardOptButton,
                signOutOptButton,
            ],
            "admin": [
                exploreOptButton,
                profileOptButton,
                notificationsOptButton,
                settingsOptButton,
                manageOptButton,
                dashboardOptButton,
                signOutOptButton,
            ],
        }

    # ---------------------------------------------------
    # Methods

    def regularMenu(self, email: str) -> None:
        """
        This method is used to create the regular menu options.

        :param email: str
        :param Window: object

        """

        for i, opt in enumerate(self.menuOpts["regular"]):
            opt.place(
                x=self.posRegularMenuX + (i * (opt.winfo_reqwidth() + self.gap)),
                y=self.posMenuY,
            )

            if i == 0:
                opt.bind("<Button-1>", lambda e: exploreWindow(email))
            elif i == 1:
                opt.bind("<Button-1>", lambda e: profileWindow(email))
            elif i == 2:
                opt.bind("<Button-1>", lambda e: notificationsWindow(email))
            elif i == 3:
                opt.bind("<Button-1>", lambda e: dashboardWindow(email))
            elif i == 4:
                opt.bind(
                    "<Button-1>",
                    lambda e: self.homeWindow.destroy(),
                )

    def adminMenu(self, email: str) -> None:
        """
        This method is used to create the admin menu options.

        :param email: str
        :param Window: object

        """

        for i, opt in enumerate(self.menuOpts["admin"]):
            opt.place(
                x=self.posAdminMenuX + (i * (opt.winfo_reqwidth() + self.gap)),
                y=self.posMenuY,
            )

            if i == 0:
                opt.bind("<Button-1>", lambda e: exploreWindow(email))

            elif i == 1:
                opt.bind("<Button-1>", lambda e: profileWindow(email))

            elif i == 2:
                opt.bind("<Button-1>", lambda e: notificationsWindow(email))

            elif i == 3:
                opt.bind("<Button-1>", lambda e: settingsWindow())

            elif i == 4:
                opt.bind("<Button-1>", lambda e: manageWindow())

            elif i == 5:
                opt.bind("<Button-1>", lambda e: dashboardWindow(email))

            elif i == 6:
                opt.bind(
                    "<Button-1>",
                    lambda e: self.homeWindow.destroy(),
                )

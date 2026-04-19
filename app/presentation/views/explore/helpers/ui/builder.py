import tkinter as tk

from app.presentation.styles.colors import colors
from app.presentation.views.album.main import open_album
from app.presentation.views.comments.main import open_comments
from app.presentation.views.helpers.data.state import ExploreState
from app.presentation.views.helpers.ui.carousel import navigate_next, navigate_prev
from app.presentation.views.helpers.ui.interactions import handle_like, handle_rate
from app.presentation.views.helpers.ui.modals import open_report_dialog
from app.presentation.views.helpers.ui.preview import reset_preview
from app.presentation.views.helpers.ui.treeview import on_treeview_select
from app.presentation.views.photo.main import open_photo_details
from app.presentation.views.profile.author import open_author_profile
from app.presentation.widgets.filter_bar import FilterBarWidget
from app.presentation.widgets.helpers.ui_dialogs import handle_delete_photo
from app.presentation.widgets.preview_panel import PreviewPanelWidget
from app.presentation.widgets.treeview import TreeviewWidget

# Layout constants
_WIN_W = 1300
_WIN_H = 750
_PAGE_BG = colors["primary-50"]
_PANEL_BG = colors["secondary-300"]
_BTN_BG = colors["accent-300"]
_BTN_FG = colors["secondary-500"]
_CANVAS_BG = colors["secondary-400"]


def build_filter_bar(win: tk.Toplevel, state: ExploreState):
    """
    Build the Author / Category / Sort filter bar at the top.

    Delegates to FilterBarWidget.

    Args:
        win: Parent window
        state: Explore state object
    """
    try:
        win.config(bg=_PAGE_BG)
    except Exception:
        pass
    FilterBarWidget(
        win, state, width=_WIN_W, bg=_PAGE_BG, btn_bg=_BTN_BG, btn_fg=_BTN_FG
    )


def build_treeview_panel(body: tk.Frame, state: ExploreState):
    """
    Build the left treeview panel showing photo list.

    Delegates to TreeviewWidget.

    Args:
        body: Parent frame
        state: Explore state object
    """

    try:
        body.config(bg=_PAGE_BG)
    except Exception:
        pass

    TreeviewWidget(
        body,
        state,
        columns=[
            {"key": "album", "heading": "Album", "width": 180},
            {"key": "author", "heading": "Author", "width": 140},
            {"key": "category", "heading": "Category", "width": 190},
        ],
        title="Explore Photos & Albums",
        description="Browse photos, open albums, and interact with the photos.",
        on_select=lambda e: on_treeview_select(e, state),
        on_page_changed=lambda: reset_preview(state),
        width=540,
        height=_WIN_H - 76,
        bg=_PAGE_BG,
    )


def build_preview_panel(body: tk.Frame, state: ExploreState):
    """
    Build the right preview panel with carousel and metadata.

    Delegates to PreviewPanelWidget.

    Args:
        body: Parent frame
        state: Explore state object
    """

    try:
        body.config(bg=_PAGE_BG)
    except Exception:
        pass

    PreviewPanelWidget(
        body,
        state,
        title="Preview Photos",
        subtitle=(
            "View the album above  •  Click the username to view the author's profile"
            "  •  Hover over the stars to rate the photo"
        ),
        show_metadata=True,
        on_prev=lambda: navigate_prev(state),
        on_next=lambda: navigate_next(state),
        on_username_click=lambda: open_author_profile(state),
        on_rate=lambda v: handle_rate(state, v, body),
        buttons=[
            {
                "name": "like_btn",
                "label": "  Add Like",
                "icon": "Like_Icon_V2.png",
                "unlike_icon": "Unlike_Icon_V2.png",
                "command": lambda: handle_like(state, body),
            },
            {
                "name": "details_btn",
                "label": "  See Details",
                "icon": "Eye_Icon_V2.png",
                "command": lambda: open_photo_details(state),
            },
            {
                "name": "comments_btn",
                "label": "  See Comments",
                "icon": "Comment_Icon_V2.png",
                "command": lambda: open_comments(state),
            },
            {
                "name": "album_btn",
                "label": "  See Album",
                "icon": "Eye_Icon_V2.png",
                "command": lambda: open_album(state),
            },
            {
                "name": "delete_btn",
                "label": "  Delete Photo",
                "icon": "Remove_Icon.png",
                "command": lambda: handle_delete_photo(state),
            },
            {
                "name": "report_btn",
                "label": "  Report Photo",
                "icon": "Report_Icon.png",
                "command": lambda: open_report_dialog(
                    body,
                    photo_id=(
                        state.selected_photo.get("id") if state.selected_photo else None
                    ),
                ),
            },
        ],
        x_pos=545,
        width=_WIN_W - 545,
        height=_WIN_H - 76,
        panel_bg=_PANEL_BG,
        btn_bg=_BTN_BG,
        btn_fg=_BTN_FG,
        canvas_bg=_CANVAS_BG,
    )

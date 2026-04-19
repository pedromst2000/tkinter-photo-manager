"""Modal dialog classes and wrappers for report and contact admin."""

import tkinter as tk
from typing import Optional

from app.presentation.views.helpers.ui.modals.contact_admin import (  # noqa: F401
    ContactAdminModal,
)
from app.presentation.views.helpers.ui.modals.report import ReportModal  # noqa: F401

__all__ = [
    "ReportModal",
    "ContactAdminModal",
    "open_report_dialog",
    "open_contact_admin",
]


def open_report_dialog(
    parent: tk.Widget,
    photo_id: Optional[int] = None,
    comment_id: Optional[int] = None,
) -> None:
    """
    Open a modal dialog for reporting a photo or comment.

    Args:
        parent: Parent widget for modality/centering.
        photo_id: ID of the photo to report (mutually exclusive with comment_id).
        comment_id: ID of the comment to report (mutually exclusive with photo_id).
    """
    if (photo_id is None and comment_id is None) or (
        photo_id is not None and comment_id is not None
    ):
        return
    ReportModal(parent, photo_id=photo_id, comment_id=comment_id).open()


def open_contact_admin(parent: tk.Widget, event: Optional[tk.Event] = None) -> None:
    """
    Open the contact admin modal dialog.

    Args:
        parent: Parent widget for modality/centering.
        event: Optional triggering event (ignored, kept for binding compatibility).
    """
    ContactAdminModal(parent).open()

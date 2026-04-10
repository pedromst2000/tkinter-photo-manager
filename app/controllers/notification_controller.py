from typing import List, Tuple

from app.core.db.engine import SessionLocal
from app.core.db.models.notification import NotificationModel
from app.core.db.models.notification_types import NotificationTypeModel
from app.core.services.notification_service import NotificationService
from app.core.state.session import session


class NotificationController:
    """
    Controller for user notifications and admin notification settings.

    Coordinates between views and models/services for:
    - Retrieving user notifications
    - Marking notifications as read
    - Toggling notification types (admin)
    """

    # ── User notifications ────────────────────────────────────────────────────

    @staticmethod
    def get_my_notifications() -> List[dict]:
        """
        Retrieve notifications for the currently logged-in user.
        Returns:
            List of notification dictionaries, or empty list if not authenticated.
        """
        if session.user_id is None:
            return []
        with SessionLocal() as db:
            return NotificationModel.get_by_user(db, session.user_id)

    @staticmethod
    def get_unread_count() -> int:
        """
        Get the count of unread notifications for the currently logged-in user.
        Returns:
            int: Number of unread notifications, or 0 if not authenticated.
        """
        if session.user_id is None:
            return 0
        with SessionLocal() as db:
            return NotificationModel.get_unread_count(db, session.user_id)

    @staticmethod
    def mark_read(not_id: int) -> bool:
        """
        Mark a specific notification as read.
        Args:
            not_id (int): The ID of the notification to mark as read.
        Returns:
            bool: True if marked successfully, False otherwise.
        """
        return NotificationService.mark_read(not_id)

    @staticmethod
    def mark_all_read() -> Tuple[bool, str]:
        """
        Mark all notifications as read for the currently logged-in user.
        Returns:
            Tuple of (success, message).
        """
        assert session.user_id is not None
        NotificationService.mark_all_read(session.user_id)
        return True, "All notifications marked as read"

    # ── Admin: notification settings ──────────────────────────────────────────

    @staticmethod
    def get_types() -> List[dict]:
        """
        Retrieve all notification types (admin only).
        Returns:
            List of notification type dictionaries, or empty list if not admin.
        """
        with SessionLocal() as db:
            return NotificationTypeModel.get_all(db)

    @staticmethod
    def toggle_notification_type(type_key: str, enabled: bool) -> Tuple[bool, str]:
        """
        Toggle a specific notification type on or off (admin only).
        Args:
            type_key (str): The key of the notification type to toggle.
            enabled (bool): True to enable, False to disable.
        Returns:
            Tuple of (success, message).
        """
        if not type_key:
            return False, "Notification type is required"
        if NotificationService.toggle_type(type_key, enabled):
            state = "enabled" if enabled else "disabled"
            return True, f"Notifications for '{type_key}' are now {state}"
        return False, f"Notification type '{type_key}' not found"

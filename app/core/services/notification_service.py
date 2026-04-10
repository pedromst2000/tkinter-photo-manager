from typing import Optional

from app.core.db.engine import SessionLocal
from app.core.db.models.notification import NotificationModel
from app.core.db.models.notification_types import NotificationTypeModel


class NotificationService:
    """
    Service class for notification business logic.

    Business rules enforced:
    - Notifications are only created if their type is enabled in notification_types.
    - The service method abstracts away the need for controllers to check notification type status.
    """

    @staticmethod
    def mark_read(not_id: int) -> bool:
        """Mark a notification as read. Returns True if successful."""
        with SessionLocal() as session:
            result = NotificationModel.mark_read(session, not_id)
            session.commit()
            return result

    @staticmethod
    def mark_all_read(user_id: int) -> None:
        """Mark all notifications as read for a user."""
        with SessionLocal() as session:
            NotificationModel.mark_all_read(session, user_id)
            session.commit()

    @staticmethod
    def toggle_type(type_key: str, enabled: bool) -> bool:
        """
        Enable or disable a notification type.

        Returns:
            bool: True if the type was found and updated, False otherwise.
        """
        with SessionLocal() as session:
            result = NotificationTypeModel.set_enabled(session, type_key, enabled)
            session.commit()
            return result

    @staticmethod
    def send(
        type_key: str,
        message: str,
        user_id: int,
        sender_id: int,
        photo_id: Optional[int] = None,
        album_id: Optional[int] = None,
        comment_id: Optional[int] = None,
    ) -> Optional[dict]:
        """
        Create a notification only if the type is enabled in notification_types.

        Args:
            type_key (str): The type string of the notification (e.g. 'daily_content').
            message (str): The message content of the notification.
            user_id (int): The ID of the user to receive the notification.
            sender_id (int): The ID of the user who triggered the notification (required).
            photo_id (int, optional): FK to photos.id — set when the notification targets a photo.
            album_id (int, optional): FK to albuns.id — set when the notification targets an album.
            comment_id (int, optional): FK to comments.id — set when the notification targets a comment.

        Returns:
            dict: The created notification as a dict, or None if the type is disabled or unknown.
        """
        with SessionLocal() as session:
            nt = NotificationTypeModel.get_by_type(session, type_key)
            if not nt or not nt["isEnabled"]:
                return None

            result = NotificationModel.create(
                session,
                type_id=nt["id"],
                message=message,
                user_id=user_id,
                sender_id=sender_id,
                photo_id=photo_id,
                album_id=album_id,
                comment_id=comment_id,
            )
            session.commit()
            return result

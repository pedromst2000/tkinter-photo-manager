from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
)

from db.engine import Base, SessionLocal


class NotificationModel(Base):
    """
    NotificationModel represents a notification in the database.
    """

    __tablename__: str = "notifications"

    __table_args__ = (
        CheckConstraint("id > 0 AND id < 10000000", name="ck_notifications_id_range"),
        CheckConstraint(
            "userID > 0 AND userID < 10000000", name="ck_notifications_userID_range"
        ),
        CheckConstraint(
            "(senderID IS NULL) OR (senderID > 0 AND senderID < 10000000)",
            name="ck_notifications_senderID_null_or_range",
        ),
        CheckConstraint(
            "length(trim(type)) > 0", name="ck_notifications_type_not_empty"
        ),
        CheckConstraint(
            "length(trim(message)) > 0", name="ck_notifications_message_not_empty"
        ),
        # at most one reference column may be non-null (photo, comment or album)
        CheckConstraint(
            "((photoID IS NOT NULL) + (commentID IS NOT NULL) + (albumID IS NOT NULL)) <= 1",
            name="ck_notifications_one_reference",
        ),
        # performance indexes for common queries
        Index("ix_notifications_userid_createdat", "userID", "createdAt"),
        Index("ix_notifications_userid_isread", "userID", "isRead"),
    )

    id: int = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    # link 'type' to notification_settings.type to enforce allowed types
    type: str = Column(
        String(50),
        ForeignKey("notification_settings.type", ondelete="CASCADE"),
        nullable=False,
    )
    message: str = Column(String(255), nullable=False)
    userID: int = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )  # recipient
    senderID: int = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )  # who triggered it
    # explicit nullable FKs for referenced target types (one-of)
    photoID: int = Column(
        Integer, ForeignKey("photos.id", ondelete="CASCADE"), nullable=True
    )
    commentID: int = Column(
        Integer, ForeignKey("comments.id", ondelete="CASCADE"), nullable=True
    )
    albumID: int = Column(
        Integer, ForeignKey("albuns.id", ondelete="CASCADE"), nullable=True
    )
    isRead: bool = Column(Boolean, default=False, nullable=False)
    createdAt: DateTime = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updatedAt: DateTime = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self) -> dict:
        """
        Convert the NotificationModel instance to a dictionary.

        Returns:
            dict: A dictionary representation of the NotificationModel instance.
        """
        return {
            "id": self.id,
            "type": self.type,
            "message": self.message,
            "userID": self.userID,
            "senderID": self.senderID,
            "photoID": self.photoID,
            "commentID": self.commentID,
            "albumID": self.albumID,
            "isRead": self.isRead,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }

    @classmethod
    def get_all(cls) -> list:
        """
        Retrieve all notifications from the database and return them as a list of dictionaries.

        Returns:
            list: A list of dictionaries, each representing a notification.
        """
        with SessionLocal() as session:
            return [n.to_dict() for n in session.query(cls).all()]

    @classmethod
    def get_by_user(cls, user_id: int) -> list:
        """
        Retrieve all notifications for a specific user (newest first).

        Parameters:
            user_id (int): The recipient user ID.

        Returns:
            list: A list of notification dicts.
        """
        with SessionLocal() as session:
            return [
                n.to_dict()
                for n in session.query(cls)
                .filter_by(userID=user_id)
                .order_by(cls.createdAt.desc())
                .all()
            ]

    @classmethod
    def get_unread_count(cls, user_id: int) -> int:
        """
        Return the number of unread notifications for a user.

        Parameters:
            user_id (int): The recipient user ID.

        Returns:
            int: Count of unread notifications.
        """
        with SessionLocal() as session:
            return session.query(cls).filter_by(userID=user_id, isRead=False).count()

    @classmethod
    def mark_read(cls, notID: int) -> bool:
        """
        Mark a single notification as read.

        Parameters:
            notID (int): The notification ID.

        Returns:
            bool: True if updated successfully.
        """
        with SessionLocal() as session:
            with session.begin():
                n = session.query(cls).filter_by(id=notID).first()
                if n:
                    n.isRead = True
                    return True
        return False

    @classmethod
    def mark_all_read(cls, user_id: int) -> None:
        """
        Mark all notifications for a user as read.

        Parameters:
            user_id (int): The recipient user ID.
        """
        with SessionLocal() as session:
            with session.begin():
                session.query(cls).filter_by(userID=user_id, isRead=False).update(
                    {"isRead": True}
                )

    @classmethod
    def create(
        cls,
        type: str,
        message: str,
        user_id: int,
        sender_id: int = None,
        photo_id: int = None,
        comment_id: int = None,
        album_id: int = None,
    ) -> dict:
        """
        Create a new notification.

        Parameters:
            type (str): Notification type ('follow', 'like', 'comment', 'new_photo', 'new_album').
            message (str): Human-readable notification message.
            user_id (int): The recipient user ID.
            sender_id (int, optional): Who triggered the notification.
            reference_id (int, optional): Related resource PK.
            reference_type (str, optional): Type of related resource.

        Returns:
            dict: A dictionary representation of the newly created notification.
        """
        # application-level validation: trim and ensure non-empty
        t = type.strip() if type is not None else ""
        m = message.strip() if message is not None else ""
        if not t:
            raise ValueError("Notification type must not be empty")
        if not m:
            raise ValueError("Notification message must not be empty")
        if len(t) > 50:
            raise ValueError("Notification type must be at most 50 characters")
        if len(m) > 255:
            raise ValueError("Notification message must be at most 255 characters")

        # enforce at-most-one reference at application level as well
        refs_given = sum(1 for v in (photo_id, comment_id, album_id) if v is not None)
        if refs_given > 1:
            raise ValueError(
                "At most one of photo_id, comment_id or album_id may be provided"
            )

        # ensure type exists in notification settings
        from db.models.notification_settings import NotificationSettingsModel

        if not NotificationSettingsModel.get_by_type(t):
            raise ValueError(f"Unknown notification type: {t}")

        with SessionLocal() as session:
            with session.begin():
                obj = cls(
                    type=t,
                    message=m,
                    userID=user_id,
                    senderID=sender_id,
                    photoID=photo_id,
                    commentID=comment_id,
                    albumID=album_id,
                )
                session.add(obj)
                session.flush()
                return obj.to_dict()

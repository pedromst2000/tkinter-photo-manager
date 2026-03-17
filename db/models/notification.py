from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String

from db.engine import Base, SessionLocal


class NotificationModel(Base):
    """
    NotificationModel represents a notification in the database.
    """

    __tablename__: str = "notifications"

    notID: int = Column(Integer, primary_key=True, autoincrement=True)
    type: str = Column(String, nullable=False)
    message: str = Column(String, nullable=False)
    userID: int = Column(
        Integer, ForeignKey("users.userID"), nullable=False
    )  # recipient
    senderID: int = Column(
        Integer, ForeignKey("users.userID"), nullable=True
    )  # who triggered it
    referenceID: int = Column(Integer, nullable=True)  # related resource PK
    referenceType: str = Column(String, nullable=True)  # 'photo' | 'album' | 'comment'
    isRead: bool = Column(Boolean, default=False)
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
            "notID": self.notID,
            "type": self.type,
            "message": self.message,
            "userID": self.userID,
            "senderID": self.senderID,
            "referenceID": self.referenceID,
            "referenceType": self.referenceType,
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
                n = session.query(cls).filter_by(notID=notID).first()
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
        reference_id: int = None,
        reference_type: str = None,
    ) -> dict:
        """
        Create a new notification.

        Parameters:
            type (str): Notification type ('follow', 'like', 'comment', 'reply', 'new_photo', 'new_album').
            message (str): Human-readable notification message.
            user_id (int): The recipient user ID.
            sender_id (int, optional): Who triggered the notification.
            reference_id (int, optional): Related resource PK.
            reference_type (str, optional): Type of related resource.

        Returns:
            dict: A dictionary representation of the newly created notification.
        """
        with SessionLocal() as session:
            with session.begin():
                obj = cls(
                    type=type,
                    message=message,
                    userID=user_id,
                    senderID=sender_id,
                    referenceID=reference_id,
                    referenceType=reference_type,
                )
                session.add(obj)
                session.flush()
                return obj.to_dict()

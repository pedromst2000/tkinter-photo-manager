from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Integer,
    String,
    UniqueConstraint,
)

from db.engine import Base, SessionLocal


class NotificationSettingsModel(Base):
    """
    Stores one row per notification type.
    The admin can toggle isEnabled to control which notification types are auto-sent.
    """

    __tablename__: str = "notification_settings"

    __table_args__ = (
        UniqueConstraint("type", name="uq_notification_settings_type"),
        CheckConstraint(
            "id > 0 AND id < 10000000", name="ck_notification_settings_id_range"
        ),
        CheckConstraint(
            "length(trim(type)) > 0", name="ck_notification_settings_type_not_empty"
        ),
        CheckConstraint(
            "length(trim(label)) > 0", name="ck_notification_settings_label_not_empty"
        ),
    )

    id: int = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    type: str = Column(
        String(50), unique=True, nullable=False
    )  # e.g. 'follow', 'like', 'comment'
    label: str = Column(String(255), nullable=False)
    isEnabled: bool = Column(Boolean, default=True, nullable=False)
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
        Convert the NotificationSettingsModel instance to a dictionary.

        Returns:
            dict: A dictionary representation of the NotificationSettingsModel instance.
        """

        return {
            "id": self.id,
            "type": self.type,
            "label": self.label,
            "isEnabled": self.isEnabled,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }

    @classmethod
    def get_all(cls) -> list:
        """
        Get all notification settings.

        Returns:
            list: List of all notification settings as dictionaries.
        """

        with SessionLocal() as session:
            return [s.to_dict() for s in session.query(cls).order_by(cls.id).all()]

    @classmethod
    def get_by_type(cls, type_key: str) -> dict | None:
        """
        Get a notification setting by its type key.

        Parameters:
            type_key (str): The type key of the notification setting to retrieve.
        Returns:
            dict | None: The notification setting as a dictionary if found, otherwise None.
        """

        with SessionLocal() as session:
            s = session.query(cls).filter_by(type=type_key).first()
            return s.to_dict() if s else None

    @classmethod
    def is_enabled(cls, type_key: str) -> bool:
        """
        Check if a notification setting is enabled.

        Parameters:
            type_key (str): The type key of the notification setting to check.

        Returns:
            bool: True if the notification setting is enabled, False otherwise.
        """
        with SessionLocal() as session:
            s = session.query(cls).filter_by(type=type_key).first()
            return s.isEnabled if s else False

    @classmethod
    def set_enabled(cls, type_key: str, enabled: bool) -> bool:
        """
        Enable or disable a notification setting.

        Parameters:
            type_key (str): The type key of the notification setting to update.
            enabled (bool): True to enable, False to disable.
        Returns:
            bool: True if the setting was updated successfully, False otherwise.
        """

        with SessionLocal() as session:
            with session.begin():
                s = session.query(cls).filter_by(type=type_key).first()
                if s:
                    s.isEnabled = enabled
                    return True
        return False

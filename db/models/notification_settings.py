from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from db.engine import Base, SessionLocal


class NotificationSettingsModel(Base):
    """
    Stores one row per notification type.
    The admin can toggle isEnabled to control which notification types are auto-sent.
    """

    __tablename__: str = "notification_settings"

    settingID: int = Column(Integer, primary_key=True, autoincrement=True)
    type: str = Column(
        String, unique=True, nullable=False
    )  # e.g. 'follow', 'like', 'comment'
    label: str = Column(String, nullable=False)  # human-readable admin UI label
    isEnabled: bool = Column(Boolean, default=True)
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
            "settingID": self.settingID,
            "type": self.type,
            "label": self.label,
            "isEnabled": self.isEnabled,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }

    @classmethod
    def get_all(cls) -> list:
        with SessionLocal() as session:
            return [
                s.to_dict() for s in session.query(cls).order_by(cls.settingID).all()
            ]

    @classmethod
    def get_by_type(cls, type_key: str) -> dict | None:
        with SessionLocal() as session:
            s = session.query(cls).filter_by(type=type_key).first()
            return s.to_dict() if s else None

    @classmethod
    def is_enabled(cls, type_key: str) -> bool:
        with SessionLocal() as session:
            s = session.query(cls).filter_by(type=type_key).first()
            return s.isEnabled if s else False

    @classmethod
    def set_enabled(cls, type_key: str, enabled: bool) -> bool:
        with SessionLocal() as session:
            with session.begin():
                s = session.query(cls).filter_by(type=type_key).first()
                if s:
                    s.isEnabled = enabled
                    return True
        return False

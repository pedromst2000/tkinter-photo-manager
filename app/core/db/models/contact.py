from datetime import datetime, timezone

from sqlalchemy import func  # import func for SQL functions like lower() and trim()
from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
)

from app.core.db.engine import Base, SessionLocal


class ContactModel(Base):
    """
    ContactModel represents a contact message in the database, with methods to create and retrieve contacts.
    """

    __tablename__: str = "contacts"

    __table_args__ = (
        CheckConstraint("id > 0 AND id < 10000000", name="ck_contacts_id_range"),
        CheckConstraint(
            "userId > 0 AND userId < 10000000", name="ck_contacts_userId_range"
        ),
        CheckConstraint("length(trim(title)) > 0", name="ck_contacts_title_not_empty"),
        CheckConstraint(
            "length(trim(message)) > 0", name="ck_contacts_message_not_empty"
        ),
        CheckConstraint("length(title) <= 75", name="ck_contacts_title_maxlen"),
        CheckConstraint("length(message) <= 255", name="ck_contacts_message_maxlen"),
        Index("ix_contacts_userId", "userId"),
    )

    id: int = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    title: str = Column(String(75), nullable=False)
    message: str = Column(String(255), nullable=False)
    userId: int = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
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
        Convert the ContactModel instance to a dictionary.

        Returns:
            dict: A dictionary representation of the ContactModel instance.
        """
        return {
            "id": self.id,
            "title": self.title,
            "message": self.message,
            "userId": self.userId,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }

    @classmethod
    def get_all(cls) -> list:
        """
        Retrieve all contact messages from the database and return them as a list of dictionaries.

        Returns:
            list: A list of dictionaries, each representing a contact message.
        """
        with SessionLocal() as session:
            return [c.to_dict() for c in session.query(cls).all()]

    @classmethod
    def create(cls, title: str, message: str, userId: int) -> dict:
        """
        Create a new contact message in the database with the given title, message, and userId.
        Validates that the title is unique (case-insensitive, trimmed) and that required fields are not empty.

        Args:
            title (str): The title of the contact message (trimmed by service/controller).
            message (str): The content of the contact message (trimmed by service/controller).
            userId (int): The ID of the user who submitted the contact message.

        Returns:
            dict: A dictionary representation of the newly created contact message.

        Raises:
            ValueError: If a contact with the same title already exists.
        """
        try:
            with SessionLocal() as session:
                with session.begin():
                    # Duplicate-title check inside the same write transaction (atomic read-then-write)
                    normalized = title.strip().lower()
                    already_exists = session.query(
                        session.query(cls)
                        .filter(func.lower(func.trim(cls.title)) == normalized)
                        .exists()
                    ).scalar()
                    if already_exists:
                        raise ValueError("Duplicate title")
                    obj: ContactModel = cls(title=title, message=message, userId=userId)
                    session.add(obj)
                    session.flush()
                    return obj.to_dict()
        except ValueError:
            raise  # Re-raise validation errors
        except Exception as e:
            from app.utils.log_utils import log_issue

            log_issue("ContactModel.create failed during database operation", exc=e)
            raise

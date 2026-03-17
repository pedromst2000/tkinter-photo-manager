from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from db.engine import Base, SessionLocal


class ContactModel(Base):
    """
    ContactModel represents a contact message in the database, with methods to create and retrieve contacts.
    """

    __tablename__: str = "contacts"

    contactID: int = Column(Integer, primary_key=True, autoincrement=True)
    title: str = Column(String, nullable=False)
    message: str = Column(String, nullable=False)
    userID: int = Column(Integer, ForeignKey("users.userID"), nullable=False)
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
            "contactID": self.contactID,
            "title": self.title,
            "message": self.message,
            "userID": self.userID,
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
    def create(cls, title: str, message: str, userID: int) -> dict:
        """
        Create a new contact message in the database.

        Parameters:
            title (str): The title of the contact message.
            message (str): The content of the contact message.
            userID (int): The ID of the user who submitted the contact message.

        Returns:
            dict: A dictionary representation of the newly created contact message.
        """
        with SessionLocal() as session:
            with session.begin():
                obj: ContactModel = cls(title=title, message=message, userID=userID)
                session.add(obj)
                session.flush()
                return obj.to_dict()

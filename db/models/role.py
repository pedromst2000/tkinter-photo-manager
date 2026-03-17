from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String

from db.engine import Base, SessionLocal


class RoleModel(Base):
    """
    RoleModel represents a user role in the database, with methods to retrieve roles.
    """

    __tablename__: str = "roles"

    roleID: int = Column(Integer, primary_key=True, autoincrement=True)
    role: str = Column(String, unique=True, nullable=False)
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
        Convert the RoleModel instance to a dictionary.

        Returns:
            dict: A dictionary representation of the RoleModel instance.
        """
        return {
            "roleID": self.roleID,
            "role": self.role,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }

    @classmethod
    def get_all(cls) -> list:
        """
        Retrieve all roles from the database and return them as a list of dictionaries.

        Returns:
            list: A list of dictionaries, each representing a role.
        """
        with SessionLocal() as session:
            return [r.to_dict() for r in session.query(cls).all()]

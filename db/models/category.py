from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String

from db.engine import Base, SessionLocal


class CategoryModel(Base):
    """
    CategoryModel represents a category in the database, with methods to create, retrieve, and delete categories.
    """

    __tablename__: str = "categories"

    categoryID: int = Column(Integer, primary_key=True, autoincrement=True)
    category: str = Column(String, unique=True, nullable=False)
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
        Convert the CategoryModel instance to a dictionary.

        Returns:
            dict: A dictionary representation of the CategoryModel instance.
        """
        return {
            "categoryID": self.categoryID,
            "category": self.category,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }

    @classmethod
    def get_all(cls) -> list:
        """
        Retrieve all categories from the database and return them as a list of dictionaries.

        Returns:
            list: A list of dictionaries, each representing a category.
        """
        with SessionLocal() as session:
            return [c.to_dict() for c in session.query(cls).all()]

    @classmethod
    def create(cls, category: str) -> dict:
        """
        Create a new category in the database.

        Parameters:
            category (str): The name of the category to create.

        Returns:
            dict: A dictionary representation of the newly created category.
        """
        with SessionLocal() as session:
            with session.begin():
                obj: CategoryModel = cls(category=category)
                session.add(obj)
                session.flush()
                return obj.to_dict()

    @classmethod
    def delete(cls, category: str) -> None:
        """
        Delete a category from the database by name.

        Parameters:
            category (str): The name of the category to delete.
        Returns:
            None
        """
        with SessionLocal() as session:
            with session.begin():
                session.query(cls).filter_by(category=category).delete()

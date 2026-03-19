from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    UniqueConstraint,
    func,
)

from db.engine import Base, SessionLocal


class RatingModel(Base):
    """
    RatingModel represents a rating given by a user to a photo.
    """

    __tablename__ = "ratings"

    __table_args__ = (
        CheckConstraint("id > 0 AND id < 10000000", name="ck_ratings_id_range"),
        CheckConstraint("rating >= 1 AND rating <= 5", name="ck_ratings_range"),
        CheckConstraint(
            "userID > 0 AND userID < 10000000", name="ck_ratings_user_range"
        ),
        CheckConstraint(
            "photoID > 0 AND photoID < 10000000", name="ck_ratings_photo_range"
        ),
        UniqueConstraint("userID", "photoID", name="uq_ratings_user_photo"),
        Index("ix_ratings_photoID", "photoID"),
        Index("ix_ratings_userID", "userID"),
    )

    id: int = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    userID: int = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    photoID: int = Column(
        Integer, ForeignKey("photos.id", ondelete="CASCADE"), nullable=False
    )
    rating: int = Column(Integer, nullable=False)
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
        Convert the RatingModel instance to a dictionary.

        Returns:
            dict: A dictionary representation of the RatingModel instance.
        """

        return {
            "id": self.id,
            "userID": self.userID,
            "photoID": self.photoID,
            "rating": self.rating,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }

    @classmethod
    def create(cls, user_id: int, photo_id: int, rating_value: int) -> dict:
        """
        Create or update a rating for a photo by a user.

        Parameters:
            user_id (int): The ID of the user giving the rating.
            photo_id (int): The ID of the photo being rated.
            rating_value (int): The rating value (1-5).
        Returns:
            dict: The created or updated rating entry as a dictionary.
        """

        # clamp rating
        r = max(1, min(5, int(rating_value)))
        with SessionLocal() as session:
            with session.begin():
                existing = (
                    session.query(cls)
                    .filter_by(userID=user_id, photoID=photo_id)
                    .first()
                )
                if existing:
                    existing.rating = r
                    session.flush()
                    return existing.to_dict()
                obj = cls(userID=user_id, photoID=photo_id, rating=r)
                session.add(obj)
                session.flush()
                return obj.to_dict()

    @classmethod
    def get_for_photo(cls, photo_id: int) -> list:
        """
        Retrieve all ratings for a given photo.

        Parameters:
            photo_id (int): The ID of the photo for which to retrieve ratings.

        Returns:
            list: A list of dictionaries, each representing a rating for the photo.
        """

        with SessionLocal() as session:
            return [
                r.to_dict()
                for r in session.query(cls).filter_by(photoID=photo_id).all()
            ]

    @classmethod
    def get_average_for_photo(cls, photo_id: int) -> float:
        """
        Calculate the average rating for a given photo.

        Parameters:
            photo_id (int): The ID of the photo for which to calculate the average rating.
        Returns:
            float: The average rating for the photo, rounded to one decimal place. Returns 0.0 if there are no ratings.
        """

        with SessionLocal() as session:
            avg = (
                session.query(func.avg(cls.rating)).filter_by(photoID=photo_id).scalar()
            )
            if avg is None:
                return 0.0
            return round(float(avg), 1)

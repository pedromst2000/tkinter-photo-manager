from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    UniqueConstraint,
)

from db.engine import Base, SessionLocal


class LikeModel(Base):
    """
    LikeModel represents a like relationship between a user and a photo.
    """

    __tablename__: str = "likes"

    __table_args__ = (
        UniqueConstraint("userID", "photoID", name="uq_like_pair"),
        CheckConstraint("id > 0 AND id < 10000000", name="ck_likes_id_range"),
        CheckConstraint(
            "userID > 0 AND userID < 10000000", name="ck_likes_userID_range"
        ),
        CheckConstraint(
            "photoID > 0 AND photoID < 10000000", name="ck_likes_photoID_range"
        ),
        Index("ix_likes_photoID", "photoID"),
        Index("ix_likes_userID", "userID"),
    )

    id: int = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    userID: int = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    photoID: int = Column(
        Integer, ForeignKey("photos.id", ondelete="CASCADE"), nullable=False
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
        Convert the LikeModel instance to a dictionary.

        Returns:
            dict: A dictionary representation of the LikeModel instance.
        """

        return {
            "id": self.id,
            "userID": self.userID,
            "photoID": self.photoID,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }

    @classmethod
    def like(cls, user_id: int, photo_id: int) -> dict | None:
        """
        Create a like relationship.
        Parameters:
            user_id (int): The ID of the user liking the photo.
            photo_id (int): The ID of the photo being liked.
        Returns:
            dict | None: The new like entry, or None if already liked.
        """

        with SessionLocal() as session:
            with session.begin():
                existing = (
                    session.query(cls)
                    .filter_by(userID=user_id, photoID=photo_id)
                    .first()
                )
                if existing:
                    return existing.to_dict()
                obj = cls(userID=user_id, photoID=photo_id)
                session.add(obj)
                session.flush()
                return obj.to_dict()

    @classmethod
    def unlike(cls, user_id: int, photo_id: int) -> bool:
        """
        Remove a like relationship.
        Parameters:
            user_id (int): The ID of the user unliking the photo.
            photo_id (int): The ID of the photo being unliked.
        Returns:
            bool: True if the like was removed, False if it didn't exist.
        """

        with SessionLocal() as session:
            with session.begin():
                deleted = (
                    session.query(cls)
                    .filter_by(userID=user_id, photoID=photo_id)
                    .delete()
                )
                return deleted > 0

    @classmethod
    def has_liked(cls, user_id: int, photo_id: int) -> bool:
        """
        Check whether a user has liked a photo.

        Parameters:
            user_id (int): The ID of the user.
            photo_id (int): The ID of the photo.

        Returns:
            bool: True if the user has liked the photo, False otherwise.
        """
        with SessionLocal() as session:
            return (
                session.query(cls).filter_by(userID=user_id, photoID=photo_id).first()
                is not None
            )

    @classmethod
    def count_by_photo(cls, photo_id: int) -> int:
        """
        Count the number of likes for a given photo.

        Parameters:
            photo_id (int): The ID of the photo.

        Returns:
            int: The number of likes for the photo.
        """
        with SessionLocal() as session:
            return session.query(cls).filter_by(photoID=photo_id).count()

    @classmethod
    def get_liked_photos(cls, user_id: int) -> list:
        """
        Get all photos liked by a user.

        Parameters:
            user_id (int): The ID of the user.

        Returns:
            list[dict]: A list of liked photo entries.
        """
        with SessionLocal() as session:
            return [
                like_obj.to_dict()
                for like_obj in session.query(cls).filter_by(userID=user_id).all()
            ]

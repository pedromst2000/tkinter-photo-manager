from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    desc,
)
from sqlalchemy.orm import Session

from app.core.db.engine import Base


class PhotoImageModel(Base):
    """
    PhotoImageModel represents an image associated with a photo in the database
    """

    __tablename__ = "photo_image"

    __table_args__ = (
        UniqueConstraint("photoId", name="uq_photo_image_photoId"),
        CheckConstraint("id > 0 AND id < 10000000", name="ck_photo_image_id_range"),
        CheckConstraint(
            "photoId > 0 AND photoId < 10000000", name="ck_photo_image_photoId_range"
        ),
        CheckConstraint(
            "length(trim(image)) > 0", name="ck_photo_image_image_not_empty"
        ),
    )

    id: int = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    photoId: int = Column(
        Integer, ForeignKey("photos.id", ondelete="CASCADE"), nullable=False
    )
    image: str = Column(String(255), nullable=False)
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
        Convert the PhotoImageModel instance to a dictionary.

        Returns:
            dict: A dictionary representation of the PhotoImageModel instance.
        """

        return {
            "id": self.id,
            "photoId": self.photoId,
            "image": self.image,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }

    @classmethod
    def create(cls, session: Session, photo_id: int, image: str) -> dict:
        """
        Create or update a PhotoImageModel record.

        Args:
            session: Active SQLAlchemy session.
            photo_id (int): The ID of the photo to which this image belongs.
            image (str): The file path or URL of the image (pre-validated).

        Returns:
            dict: A dictionary representation of the created/updated PhotoImageModel instance.
        """
        existing = (
            session.query(cls)
            .filter_by(photoId=photo_id)
            .order_by(desc(cls.createdAt))
            .first()
        )
        if existing:
            existing.image = image
            session.flush()
            return existing.to_dict()

        obj = cls(photoId=photo_id, image=image)
        session.add(obj)
        session.flush()
        return obj.to_dict()

    @classmethod
    def get_for_photo(cls, session: Session, photo_id: int) -> dict | None:
        """
        Return the single image record for a photo as a dict, or None.

        Args:
            session: Active SQLAlchemy session.
            photo_id (int): The ID of the photo for which to retrieve the image.

        Returns:
            dict | None: A dictionary representation of the image record, or None if not found.
        """
        row = (
            session.query(cls)
            .filter_by(photoId=photo_id)
            .order_by(desc(cls.createdAt))
            .first()
        )
        return row.to_dict() if row else None

    @classmethod
    def get_primary_for_photo(cls, session: Session, photo_id: int) -> str | None:
        """
        Return the primary image path for a photo, or None.

        Args:
            session: Active SQLAlchemy session.
            photo_id (int): The ID of the photo for which to retrieve the primary image.

        Returns:
            str | None: The file path or URL of the primary image, or None if not found.
        """
        row = (
            session.query(cls)
            .filter_by(photoId=photo_id)
            .order_by(desc(cls.createdAt))
            .first()
        )
        if row:
            return row.image
        return None

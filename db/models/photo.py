from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from db.engine import Base, SessionLocal


class PhotoModel(Base):
    """
    PhotoModel represents a photo in the database, with methods to create, retrieve, and delete photos.
    """

    __tablename__: str = "photos"

    __table_args__ = (
        CheckConstraint("id > 0 AND id < 10000000", name="ck_photos_id_range"),
        CheckConstraint(
            "categoryID > 0 AND categoryID < 10000000",
            name="ck_photos_categoryID_range",
        ),
        CheckConstraint(
            "(albumID IS NULL) OR (albumID > 0 AND albumID < 10000000)",
            name="ck_photos_albumID_null_or_range",
        ),
        CheckConstraint(
            "length(trim(description)) > 0", name="ck_photos_description_not_empty"
        ),
        CheckConstraint(
            "length(description) <= 255", name="ck_photos_description_maxlen"
        ),
        Index("ix_photos_albumID", "albumID"),
        Index("ix_photos_categoryID", "categoryID"),
    )

    id: int = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    description: str = Column(String(255), nullable=False)
    publishedDate: DateTime = Column(DateTime(timezone=True), nullable=False)
    categoryID: int = Column(
        Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False
    )
    albumID: int = Column(
        Integer, ForeignKey("albuns.id", ondelete="CASCADE"), nullable=True
    )
    createdAt: DateTime = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updatedAt: DateTime = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # ORM relationships — cascade photo deletion to all child rows
    images_rel = relationship(
        "PhotoImageModel", cascade="all, delete-orphan", passive_deletes=True
    )

    @property
    def images(self):
        return self.images_rel

    ratings_rel = relationship(
        "RatingModel", cascade="all, delete-orphan", passive_deletes=True
    )

    @property
    def ratings(self):
        return self.ratings_rel

    comments_rel = relationship(
        "CommentModel", cascade="all, delete-orphan", passive_deletes=True
    )

    @property
    def comments(self):
        return self.comments_rel

    likes_rel = relationship(
        "LikeModel", cascade="all, delete-orphan", passive_deletes=True
    )

    @property
    def likes(self):
        return self.likes_rel

    def to_dict(self) -> dict:
        """
        Convert the PhotoModel instance to a dictionary.

        Returns:
            dict: A dictionary representation of the PhotoModel instance.
        """
        return {
            "id": self.id,
            "description": self.description,
            "publishedDate": self.publishedDate,
            "rating": 0.0,
            "categoryID": self.categoryID,
            "albumID": self.albumID,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }

    @classmethod
    def get_all(cls) -> list:
        """
        Retrieve all photos from the database and return them as a list of dictionaries.

        Returns:
            list: A list of dictionaries, each representing a photo.
        """
        with SessionLocal() as session:
            return [p.to_dict() for p in session.query(cls).all()]

    @classmethod
    def create(
        cls,
        description: str,
        publishedDate,
        categoryID: int,
        albumID: int = None,
    ) -> dict:
        """
        Create a new photo in the database.

        Parameters:
            description (str): The description of the photo.
            publishedDate (datetime): The date and time when the photo was published.
            categoryID (int): The ID of the category the photo belongs to.
            albumID (int, optional): The ID of the album the photo belongs to. Defaults to None.
            Note: image data is stored in `photo_images` table; ratings are stored in `ratings`.
        Returns:
            dict: A dictionary representation of the newly created photo.
        """
        with SessionLocal() as session:
            with session.begin():
                obj: PhotoModel = cls(
                    description=description,
                    publishedDate=publishedDate,
                    categoryID=categoryID,
                    albumID=albumID,
                )
                session.add(obj)
                session.flush()
                return obj.to_dict()

    @classmethod
    def delete(cls, photoID: int) -> None:
        """
        Delete a photo from the database by its ID.

        Parameters:
            photoID (int): The ID of the photo to delete.
        Returns:
            None
        """
        with SessionLocal() as session:
            with session.begin():
                p = session.query(cls).filter_by(id=photoID).first()
                if p:
                    session.delete(p)

    @classmethod
    def delete_many(cls, *photoIDs: int) -> None:
        """
        Delete multiple photos from the database by their IDs.

        Parameters:
            *photoIDs (int): A variable number of photo IDs to delete.
        Returns:
            None
        """
        with SessionLocal() as session:
            with session.begin():
                for pid in photoIDs:
                    p = session.query(cls).filter_by(id=int(pid)).first()
                    if p:
                        session.delete(p)

    @classmethod
    def get_by_id(cls, photo_id: int) -> dict | None:
        """
        Retrieve a photo by its ID.

        Parameters:
            photo_id (int): The ID of the photo to retrieve.

        Returns:
            dict | None: A dictionary representation of the photo if found, otherwise None.
        """
        with SessionLocal() as session:
            p = session.query(cls).filter_by(id=photo_id).first()
            if not p:
                return None
            data = p.to_dict()
            # lazy import to avoid circular imports (use package-relative imports)
            try:
                from .photo_image import PhotoImageModel
                from .rating import RatingModel

                img = PhotoImageModel.get_primary_for_photo(p.id)
                data["image"] = img or ""
                data["rating"] = RatingModel.get_average_for_photo(p.id) or 0.0
            except Exception:
                # if enrichment fails, provide sensible defaults
                data["image"] = ""
                data["rating"] = 0.0
            return data

    @classmethod
    def get_by_album(cls, album_id: int) -> list:
        """
        Retrieve all photos in a specific album.

        Parameters:
            album_id (int): The ID of the album.

        Returns:
            list: A list of dictionaries representing photos in the album.
        """
        with SessionLocal() as session:
            return [
                p.to_dict()
                for p in session.query(cls).filter_by(albumID=album_id).all()
            ]

    @classmethod
    def get_by_category(cls, category_id: int) -> list:
        """
        Retrieve all photos in a specific category.

        Parameters:
            category_id (int): The ID of the category.

        Returns:
            list: A list of dictionaries representing photos in the category.
        """
        with SessionLocal() as session:
            return [
                p.to_dict()
                for p in session.query(cls).filter_by(categoryID=category_id).all()
            ]

    @classmethod
    def update(cls, updated: dict) -> bool:
        """
        Update an existing photo in the database.

        Parameters:
            updated (dict): A dictionary containing the updated photo information.

        Returns:
            bool: True if updated successfully, False otherwise.
        """
        allowed = {"description", "publishedDate", "categoryID", "albumID"}
        with SessionLocal() as session:
            with session.begin():
                p = session.query(cls).filter_by(id=updated["id"]).first()
                if p:
                    for key, value in updated.items():
                        if key == "id":
                            continue
                        if key not in allowed:
                            continue
                        if key == "description":
                            val = str(value).strip()
                            if not val:
                                return False
                            setattr(p, key, val)
                        else:
                            setattr(p, key, value)
                    return True
        return False

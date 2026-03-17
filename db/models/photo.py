from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String

from db.engine import Base, SessionLocal


class PhotoModel(Base):
    """
    PhotoModel represents a photo in the database, with methods to create, retrieve, and delete photos.
    """

    __tablename__: str = "photos"

    photoID: int = Column(Integer, primary_key=True, autoincrement=True)
    description: str = Column(String, nullable=False)
    publishedDate: DateTime = Column(DateTime(timezone=True), nullable=False)
    createdAt: DateTime = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updatedAt: DateTime = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    image: str = Column(String, nullable=False)
    views: int = Column(Integer, default=0)
    rating: float = Column(Float, default=0.0)
    categoryID: int = Column(
        Integer, ForeignKey("categories.categoryID"), nullable=False
    )
    albumID: int = Column(Integer, ForeignKey("albuns.albumID"), nullable=True)
    userID: int = Column(Integer, ForeignKey("users.userID"), nullable=True)

    def to_dict(self) -> dict:
        """
        Convert the PhotoModel instance to a dictionary.

        Returns:
            dict: A dictionary representation of the PhotoModel instance.
        """
        return {
            "photoID": self.photoID,
            "description": self.description,
            "publishedDate": self.publishedDate,
            "image": self.image,
            "views": self.views,
            "rating": self.rating,
            "categoryID": self.categoryID,
            "albumID": self.albumID,
            "userID": self.userID,
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
        image: str,
        categoryID: int,
        albumID: int = None,
        userID: int = None,
        views: int = 0,
        rating: float = 0.0,
    ) -> dict:
        """
        Create a new photo in the database.

        Parameters:
            description (str): The description of the photo.
            publishedDate (datetime): The date and time when the photo was published.
            image (str): The file path or URL of the photo.
            categoryID (int): The ID of the category the photo belongs to.
            albumID (int, optional): The ID of the album the photo belongs to. Defaults to None.
            userID (int, optional): The ID of the user who uploaded the photo. Defaults to None.
            likes (int, optional): The number of likes the photo has. Defaults to 0.
            views (int, optional): The number of views the photo has. Defaults to 0.
            rating (float, optional): The average rating of the photo. Defaults to 0.0.
        Returns:
            dict: A dictionary representation of the newly created photo.
        """
        with SessionLocal() as session:
            with session.begin():
                obj: PhotoModel = cls(
                    description=description,
                    publishedDate=publishedDate,
                    image=image,
                    categoryID=categoryID,
                    albumID=albumID,
                    userID=userID,
                    views=views,
                    rating=rating,
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
                session.query(cls).filter_by(photoID=photoID).delete()

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
                    session.query(cls).filter_by(photoID=int(pid)).delete()

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
            p = session.query(cls).filter_by(photoID=photo_id).first()
            return p.to_dict() if p else None

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
    def get_by_user(cls, user_id: int) -> list:
        """
        Retrieve all photos uploaded by a specific user.

        Parameters:
            user_id (int): The ID of the user.

        Returns:
            list: A list of dictionaries representing the user's photos.
        """
        with SessionLocal() as session:
            return [
                p.to_dict() for p in session.query(cls).filter_by(userID=user_id).all()
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
    def count_by_user(cls, user_id: int) -> int:
        """
        Count all photos uploaded by a specific user.

        Parameters:
            user_id (int): The ID of the user.

        Returns:
            int: The number of photos uploaded by the user.
        """
        with SessionLocal() as session:
            return session.query(cls).filter_by(userID=user_id).count()

    @classmethod
    def update(cls, updated: dict) -> bool:
        """
        Update an existing photo in the database.

        Parameters:
            updated (dict): A dictionary containing the updated photo information.

        Returns:
            bool: True if updated successfully, False otherwise.
        """
        with SessionLocal() as session:
            with session.begin():
                p = session.query(cls).filter_by(photoID=updated["photoID"]).first()
                if p:
                    for key, value in updated.items():
                        if key != "photoID":
                            setattr(p, key, value)
                    return True
        return False

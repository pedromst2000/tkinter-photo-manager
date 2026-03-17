from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from db.engine import Base, SessionLocal


class AlbumModel(Base):
    """
    AlbumModel represents an album in the database, with methods to create, retrieve, and update albums.
    """

    __tablename__: str = "albuns"

    albumID: int = Column(Integer, primary_key=True, autoincrement=True)
    name: str = Column(String, nullable=False)
    creatorID: int = Column(Integer, ForeignKey("users.userID"), nullable=False)
    createdAt: DateTime = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updatedAt: DateTime = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self) -> dict:
        """Convert the AlbumModel instance to a dictionary.

        Returns:
            dict: A dictionary representation of the AlbumModel instance.
        """

        return {
            "albumID": self.albumID,
            "name": self.name,
            "creatorID": self.creatorID,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }

    @classmethod
    def get_all(cls) -> list:
        """
        Retrieve all albums from the database and return them as a list of dictionaries.
        Returns:
            list: A list of dictionaries, each representing an album.
        """

        with SessionLocal() as session:
            return [a.to_dict() for a in session.query(cls).all()]

    @classmethod
    def create(cls, name: str, creatorID: int) -> dict:
        """
        Create a new album in the database.

        Parameters:
            name (str): The name of the album.
            creatorID (int): The ID of the user creating the album.

        Returns:
            dict: A dictionary representation of the newly created album.
        """
        with SessionLocal() as session:
            with session.begin():
                obj: AlbumModel = cls(name=name, creatorID=creatorID)
                session.add(obj)
                session.flush()
                return obj.to_dict()

    @classmethod
    def update(cls, updated: dict) -> dict:
        """
        Update an existing album in the database.

        Parameters:
            updated (dict): A dictionary containing the updated album information, including "albumID" and "name".
        Returns:
            dict: A dictionary representation of the updated album.
        """
        with SessionLocal() as session:
            with session.begin():
                a: AlbumModel = (
                    session.query(cls).filter_by(albumID=updated["albumID"]).first()
                )
                if a:
                    a.name = updated["name"]
        return updated

    @classmethod
    def get_by_id(cls, album_id: int) -> dict | None:
        """
        Retrieve an album by its ID.

        Parameters:
            album_id (int): The ID of the album to retrieve.

        Returns:
            dict | None: A dictionary representation of the album if found, otherwise None.
        """
        with SessionLocal() as session:
            a = session.query(cls).filter_by(albumID=album_id).first()
            return a.to_dict() if a else None

    @classmethod
    def get_by_creator(cls, creator_id: int) -> list:
        """
        Retrieve all albums created by a specific user.

        Parameters:
            creator_id (int): The ID of the user who created the albums.

        Returns:
            list: A list of dictionaries representing the user's albums.
        """
        with SessionLocal() as session:
            return [
                a.to_dict()
                for a in session.query(cls).filter_by(creatorID=creator_id).all()
            ]

    @classmethod
    def delete(cls, album_id: int) -> bool:
        """
        Delete an album from the database by its ID.

        Parameters:
            album_id (int): The ID of the album to delete.

        Returns:
            bool: True if deleted successfully, False otherwise.
        """
        with SessionLocal() as session:
            with session.begin():
                a = session.query(cls).filter_by(albumID=album_id).first()
                if a:
                    session.delete(a)
                    return True
        return False

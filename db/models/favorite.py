from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer

from db.engine import Base, SessionLocal


class FavoriteModel(Base):
    """
    FavoriteModel represents a favorite album entry in the database, with methods to create and retrieve favorites.
    """

    __tablename__: str = "favorites"

    favoriteID: int = Column(Integer, primary_key=True, autoincrement=True)
    albumID: int = Column(Integer, ForeignKey("albuns.albumID"), nullable=False)
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
        Convert the FavoriteModel instance to a dictionary.

        Returns:
            dict: A dictionary representation of the FavoriteModel instance.
        """
        return {
            "favoriteID": self.favoriteID,
            "albumID": self.albumID,
            "userID": self.userID,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }

    @classmethod
    def get_all(cls) -> list:
        """
        Retrieve all favorite album entries from the database and return them as a list of dictionaries.

        Returns:
            list: A list of dictionaries, each representing a favorite album entry.
        """
        with SessionLocal() as session:
            return [f.to_dict() for f in session.query(cls).all()]

    @classmethod
    def create(cls, albumID: int, userID: int) -> dict:
        """
        Create a new favorite album entry in the database.

        Parameters:
            albumID (int): The ID of the album being favorited.
            userID (int): The ID of the user who is favoriting the album.

        Returns:
            dict: A dictionary representation of the newly created favorite album entry.
        """
        with SessionLocal() as session:
            with session.begin():
                obj: FavoriteModel = cls(albumID=albumID, userID=userID)
                session.add(obj)
                session.flush()
                return obj.to_dict()

    @classmethod
    def get_users_by_album(cls, albumID: int) -> list:
        """
        Return the IDs of all users who have favorited a given album.

        Parameters:
            albumID (int): The album ID to query favorites for.

        Returns:
            list[int]: A list of userID values.
        """
        with SessionLocal() as session:
            rows = session.query(cls).filter(cls.albumID == albumID).all()
            return [row.userID for row in rows]

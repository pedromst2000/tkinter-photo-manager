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


class FavoriteModel(Base):
    """
    FavoriteModel represents a favorite album entry in the database, with methods to create and retrieve favorites.
    """

    __tablename__: str = "favorites"

    __table_args__ = (
        CheckConstraint("id > 0 AND id < 10000000", name="ck_favorites_id_range"),
        CheckConstraint(
            "albumID > 0 AND albumID < 10000000", name="ck_favorites_albumID_range"
        ),
        CheckConstraint(
            "userID > 0 AND userID < 10000000", name="ck_favorites_userID_range"
        ),
        UniqueConstraint("userID", "albumID", name="uq_favorites_user_album"),
        Index("ix_favorites_albumID", "albumID"),
        Index("ix_favorites_userID", "userID"),
    )

    id: int = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    albumID: int = Column(
        Integer, ForeignKey("albuns.id", ondelete="CASCADE"), nullable=False
    )
    userID: int = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
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
        Convert the FavoriteModel instance to a dictionary.

        Returns:
            dict: A dictionary representation of the FavoriteModel instance.
        """
        return {
            "id": self.id,
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
                # idempotent create: return existing if already favorited
                existing = (
                    session.query(cls).filter_by(albumID=albumID, userID=userID).first()
                )
                if existing:
                    return existing.to_dict()
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

    @classmethod
    def get_by_user(cls, userID: int) -> list:
        """Return favorite rows for a user as dicts.

        Parameters:
            userID (int): The user ID to query favorites for.

        Returns:
            list[dict]: A list of favorite entries as dictionaries.
        """
        with SessionLocal() as session:
            rows = session.query(cls).filter(cls.userID == userID).all()
            return [r.to_dict() for r in rows]

    @classmethod
    def delete_for_user(cls, albumID: int, userID: int) -> bool:
        """
        Delete a favorite for a user.

        Parameters:
            albumID (int): The ID of the album to remove from favorites.
            userID (int): The ID of the user whose favorite is being removed.

        Returns:
            bool: True if the favorite was deleted, False otherwise.
        """
        with SessionLocal() as session:
            with session.begin():
                q = session.query(cls).filter_by(albumID=albumID, userID=userID)
                count = q.delete()
                return count > 0

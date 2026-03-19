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

from db.engine import Base, SessionLocal


class CommentModel(Base):
    """
    CommentModel represents a plain comment in the database.
    """

    __tablename__: str = "comments"

    __table_args__ = (
        CheckConstraint("id > 0 AND id < 10000000", name="ck_comments_id_range"),
        CheckConstraint(
            "authorID > 0 AND authorID < 10000000", name="ck_comments_author_range"
        ),
        CheckConstraint(
            "photoID > 0 AND photoID < 10000000", name="ck_comments_photo_range"
        ),
        CheckConstraint(
            "length(trim(comment)) > 0", name="ck_comments_comment_not_empty"
        ),
        CheckConstraint("length(comment) <= 255", name="ck_comments_comment_maxlen"),
        Index("ix_comments_photoID_createdAt", "photoID", "createdAt"),
    )

    id: int = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    authorID: int = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    comment: str = Column(String(255), nullable=False)
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
        Convert the CommentModel instance to a dictionary.

        Returns:
            dict: A dictionary representation of the CommentModel instance.
        """
        return {
            "id": self.id,
            "authorID": self.authorID,
            "comment": self.comment,
            "photoID": self.photoID,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }

    @classmethod
    def get_all(cls) -> list:
        """
        Retrieve all comments from the database and return them as a list of dictionaries.

        Returns:
            list: A list of dictionaries, each representing a comment.
        """
        with SessionLocal() as session:
            return [c.to_dict() for c in session.query(cls).all()]

    @classmethod
    def get_by_photo(cls, photo_id: int) -> list:
        """
        Retrieve all comments for a photo ordered by creation time (oldest first).

        Parameters:
            photo_id (int): The photo ID.

        Returns:
            list: A list of comment dicts.
        """
        with SessionLocal() as session:
            return [
                c.to_dict()
                for c in session.query(cls)
                .filter_by(photoID=photo_id)
                .order_by(cls.createdAt)
                .all()
            ]

    @classmethod
    def create(
        cls,
        authorID: int,
        comment: str,
        photoID: int,
    ) -> dict:
        """
        Create a new comment in the database.

        Parameters:
            authorID (int): The ID of the user who authored the comment.
            comment (str): The content of the comment.
            photoID (int): The ID of the photo the comment belongs to.

        Returns:
            dict: A dictionary representation of the newly created comment.
        """
        # application-level validation: trim and validate content length
        trimmed = comment.strip() if comment is not None else ""
        if not trimmed:
            raise ValueError("Comment must not be empty")
        if len(trimmed) > 255:
            raise ValueError("Comment must be at most 255 characters")

        with SessionLocal() as session:
            with session.begin():
                obj: CommentModel = cls(
                    authorID=authorID,
                    comment=trimmed,
                    photoID=photoID,
                )
                session.add(obj)
                session.flush()
                return obj.to_dict()

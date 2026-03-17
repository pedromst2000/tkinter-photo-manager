from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from db.engine import Base, SessionLocal


class CommentModel(Base):
    """
    CommentModel represents a comment (or reply) in the database.
    """

    __tablename__: str = "comments"

    commentID: int = Column(Integer, primary_key=True, autoincrement=True)
    authorID: int = Column(Integer, ForeignKey("users.userID"), nullable=False)
    comment: str = Column(String, nullable=False)
    photoID: int = Column(Integer, ForeignKey("photos.photoID"), nullable=False)
    parentCommentID: int = Column(
        Integer, ForeignKey("comments.commentID"), nullable=True
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
            "commentID": self.commentID,
            "authorID": self.authorID,
            "comment": self.comment,
            "photoID": self.photoID,
            "parentCommentID": self.parentCommentID,
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
        Retrieve all top-level comments for a photo (oldest first).

        Parameters:
            photo_id (int): The photo ID.

        Returns:
            list: A list of top-level comment dicts.
        """
        with SessionLocal() as session:
            return [
                c.to_dict()
                for c in session.query(cls)
                .filter_by(photoID=photo_id, parentCommentID=None)
                .order_by(cls.createdAt)
                .all()
            ]

    @classmethod
    def get_replies(cls, parent_comment_id: int) -> list:
        """
        Retrieve all replies for a given parent comment (oldest first).

        Parameters:
            parent_comment_id (int): The parent comment ID.

        Returns:
            list: A list of reply dicts.
        """
        with SessionLocal() as session:
            return [
                c.to_dict()
                for c in session.query(cls)
                .filter_by(parentCommentID=parent_comment_id)
                .order_by(cls.createdAt)
                .all()
            ]

    @classmethod
    def create(
        cls,
        authorID: int,
        comment: str,
        photoID: int,
        parentCommentID: int = None,
    ) -> dict:
        """
        Create a new comment or reply in the database.

        Parameters:
            authorID (int): The ID of the user who authored the comment.
            comment (str): The content of the comment.
            photoID (int): The ID of the photo the comment belongs to.
            parentCommentID (int, optional): The parent comment ID for replies.

        Returns:
            dict: A dictionary representation of the newly created comment.
        """
        with SessionLocal() as session:
            with session.begin():
                obj: CommentModel = cls(
                    authorID=authorID,
                    comment=comment,
                    photoID=photoID,
                    parentCommentID=parentCommentID,
                )
                session.add(obj)
                session.flush()
                return obj.to_dict()

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, UniqueConstraint

from db.engine import Base, SessionLocal


class FollowModel(Base):
    """
    FollowModel represents a follow relationship between two users.
    """

    __tablename__: str = "follows"

    followID: int = Column(Integer, primary_key=True, autoincrement=True)
    followerID: int = Column(Integer, ForeignKey("users.userID"), nullable=False)
    followedID: int = Column(Integer, ForeignKey("users.userID"), nullable=False)
    createdAt: DateTime = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updatedAt: DateTime = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        UniqueConstraint("followerID", "followedID", name="uq_follow_pair"),
    )

    def to_dict(self) -> dict:
        """
        Convert the FollowModel instance to a dictionary.

        Returns:
            dict: A dictionary representation of the FollowModel instance.
        """

        return {
            "followID": self.followID,
            "followerID": self.followerID,
            "followedID": self.followedID,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }

    @classmethod
    def follow(cls, follower_id: int, followed_id: int) -> dict | None:
        """
        Create a follow relationship.

        Parameters:
            follower_id (int): The ID of the user doing the following.
            followed_id (int): The ID of the user being followed.

        Returns:
            dict | None: The new follow entry, or None if already following.
        """
        with SessionLocal() as session:
            with session.begin():
                existing = (
                    session.query(cls)
                    .filter_by(followerID=follower_id, followedID=followed_id)
                    .first()
                )
                if existing:
                    return None
                obj = cls(followerID=follower_id, followedID=followed_id)
                session.add(obj)
                session.flush()
                return obj.to_dict()

    @classmethod
    def unfollow(cls, follower_id: int, followed_id: int) -> bool:
        """
        Remove a follow relationship.

        Parameters:
            follower_id (int): The ID of the user doing the unfollowing.
            followed_id (int): The ID of the user being unfollowed.

        Returns:
            bool: True if the relationship was removed, False if it didn't exist.
        """
        with SessionLocal() as session:
            with session.begin():
                deleted = (
                    session.query(cls)
                    .filter_by(followerID=follower_id, followedID=followed_id)
                    .delete()
                )
                return deleted > 0

    @classmethod
    def is_following(cls, follower_id: int, followed_id: int) -> bool:
        """
        Check whether follower_id is following followed_id.

        Returns:
            bool: True if the follow relationship exists.
        """
        with SessionLocal() as session:
            return (
                session.query(cls)
                .filter_by(followerID=follower_id, followedID=followed_id)
                .first()
            ) is not None

    @classmethod
    def get_followers(cls, user_id: int) -> list:
        """
        Return all follow entries where followed_id == user_id (people who follow this user).

        Returns:
            list[dict]: FollowModel dicts with followerID field.
        """
        with SessionLocal() as session:
            return [
                f.to_dict()
                for f in session.query(cls).filter_by(followedID=user_id).all()
            ]

    @classmethod
    def get_following(cls, user_id: int) -> list:
        """
        Return all follow entries where follower_id == user_id (users this user follows).

        Returns:
            list[dict]: FollowModel dicts with followedID field.
        """
        with SessionLocal() as session:
            return [
                f.to_dict()
                for f in session.query(cls).filter_by(followerID=user_id).all()
            ]

    @classmethod
    def count_followers(cls, user_id: int) -> int:
        """
        Return the number of users following user_id.

        Parameters:
            user_id (int): The ID of the user whose followers to count.

        Returns:
            int: The number of followers.
        """
        with SessionLocal() as session:
            return session.query(cls).filter_by(followedID=user_id).count()

    @classmethod
    def count_following(cls, user_id: int) -> int:
        """
        Return the number of users that user_id follows.

        Parameters:
            user_id (int): The ID of the user whose following to count.

        Returns:
            int: The number of users that user_id follows.
        """
        with SessionLocal() as session:
            return session.query(cls).filter_by(followerID=user_id).count()

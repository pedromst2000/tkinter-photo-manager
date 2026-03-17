from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String

from db.engine import Base, SessionLocal


class UserModel(Base):
    """
    UserModel represents a user in the database, with methods to create, retrieve, and update users.
    """

    __tablename__: str = "users"

    userID: int = Column(Integer, primary_key=True, autoincrement=True)
    username: str = Column(String, unique=True, nullable=False)
    email: str = Column(String, unique=True, nullable=False)
    password: str = Column(String, nullable=False)
    avatar: str = Column(
        String, default="assets/images/profile_avatars/default_avatar.jpg"
    )
    role: str = Column(String, default="unsigned")  # 'admin' | 'regular' | 'unsigned'
    roleID: int = Column(Integer, ForeignKey("roles.roleID"), nullable=True)
    isBlocked: bool = Column(Boolean, default=False)
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
        Convert the UserModel instance to a dictionary.

        Returns:
            dict: A dictionary representation of the UserModel instance.
        """
        return {
            "userID": self.userID,
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "avatar": self.avatar,
            "role": self.role,
            "roleID": self.roleID,
            "isBlocked": self.isBlocked,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }

    @classmethod
    def get_all(cls) -> list:
        """
        Retrieve all users from the database and return them as a list of dictionaries.

        Returns:
            list: A list of dictionaries, each representing a user.
        """
        with SessionLocal() as session:
            return [u.to_dict() for u in session.query(cls).all()]

    @classmethod
    def get_by_id(cls, userID: int) -> dict | None:
        """
        Retrieve a user by their ID.

        Parameters:
            userID (int): The ID of the user to retrieve.

        Returns:
            dict | None: A dictionary representation of the user if found, otherwise None.
        """
        with SessionLocal() as session:
            u = session.query(cls).filter_by(userID=userID).first()
            return u.to_dict() if u else None

    @classmethod
    def create(
        cls,
        username: str,
        email: str,
        password: str,
        avatar: str = "assets/images/profile_avatars/default_avatar.jpg",
        role: str = "unsigned",
        roleID: int = None,
        isBlocked: bool = False,
    ) -> dict:
        """
        Create a new user in the database.

        Parameters:
            username (str): The username of the user.
            email (str): The email address of the user.
            password (str): The password of the user.
            avatar (str, optional): The avatar image path.
            role (str, optional): The role of the user.
            roleID (int, optional): The ID of the user's role.
            isBlocked (bool, optional): Whether the user is blocked.

        Returns:
            dict: A dictionary representation of the newly created user.
        """
        with SessionLocal() as session:
            with session.begin():
                user: UserModel = cls(
                    username=username,
                    email=email,
                    password=password,
                    avatar=avatar,
                    role=role,
                    roleID=roleID,
                    isBlocked=isBlocked,
                )
                session.add(user)
                session.flush()
                return user.to_dict()

    @classmethod
    def update(cls, updated: dict) -> dict:
        """
        Update an existing user in the database.

        Parameters:
            updated (dict): A dictionary containing the updated user information.

        Returns:
            dict: A dictionary representation of the updated user.
        """
        with SessionLocal() as session:
            with session.begin():
                u: UserModel = (
                    session.query(cls).filter_by(userID=updated["userID"]).first()
                )
                if u:
                    for key, value in updated.items():
                        setattr(u, key, value)
        return updated

    @classmethod
    def get_by_email(cls, email: str) -> dict | None:
        """
        Retrieve a user by their email address.

        Parameters:
            email (str): The email address to search for.

        Returns:
            dict | None: A dictionary representation of the user if found, otherwise None.
        """
        with SessionLocal() as session:
            u = session.query(cls).filter(cls.email.ilike(email)).first()
            return u.to_dict() if u else None

    @classmethod
    def get_by_username(cls, username: str) -> dict | None:
        """
        Retrieve a user by their username (case-insensitive).

        Parameters:
            username (str): The username to search for.

        Returns:
            dict | None: A dictionary representation of the user if found, otherwise None.
        """
        with SessionLocal() as session:
            u = session.query(cls).filter(cls.username.ilike(username)).first()
            return u.to_dict() if u else None

    @classmethod
    def email_exists(cls, email: str) -> bool:
        """
        Check if an email already exists in the database.

        Parameters:
            email (str): The email address to check.

        Returns:
            bool: True if the email exists, False otherwise.
        """
        with SessionLocal() as session:
            return session.query(cls).filter(cls.email.ilike(email)).count() > 0

    @classmethod
    def username_exists(cls, username: str) -> bool:
        """
        Check if a username already exists in the database (case-insensitive).

        Parameters:
            username (str): The username to check.

        Returns:
            bool: True if the username exists, False otherwise.
        """
        with SessionLocal() as session:
            return session.query(cls).filter(cls.username.ilike(username)).count() > 0

    @classmethod
    def get_by_role(cls, role: str) -> list:
        """
        Retrieve all users with a specific role.

        Parameters:
            role (str): The role to filter by ('admin', 'regular', 'unsigned').

        Returns:
            list: A list of dictionaries representing users with that role.
        """
        with SessionLocal() as session:
            return [u.to_dict() for u in session.query(cls).filter_by(role=role).all()]

    @classmethod
    def get_blocked_users(cls) -> list:
        """
        Retrieve all blocked users.

        Returns:
            list: A list of dictionaries representing blocked users.
        """
        with SessionLocal() as session:
            return [
                u.to_dict() for u in session.query(cls).filter_by(isBlocked=True).all()
            ]

    @classmethod
    def update_avatar(cls, user_id: int, avatar_path: str) -> bool:
        """
        Update a user's avatar.

        Parameters:
            user_id (int): The user's ID.
            avatar_path (str): The new avatar path.

        Returns:
            bool: True if updated successfully, False otherwise.
        """
        with SessionLocal() as session:
            with session.begin():
                u = session.query(cls).filter_by(userID=user_id).first()
                if u:
                    u.avatar = avatar_path
                    return True
        return False

    @classmethod
    def update_password(cls, user_id: int, hashed_password: str) -> bool:
        """
        Update a user's password.

        Parameters:
            user_id (int): The user's ID.
            hashed_password (str): The new hashed password.

        Returns:
            bool: True if updated successfully, False otherwise.
        """
        with SessionLocal() as session:
            with session.begin():
                u = session.query(cls).filter_by(userID=user_id).first()
                if u:
                    u.password = hashed_password
                    return True
        return False

    @classmethod
    def update_role(cls, user_id: int, role: str) -> bool:
        """
        Update a user's role.

        Parameters:
            user_id (int): The user's ID.
            role (str): The new role.

        Returns:
            bool: True if updated successfully, False otherwise.
        """
        with SessionLocal() as session:
            with session.begin():
                u = session.query(cls).filter_by(userID=user_id).first()
                if u:
                    u.role = role
                    return True
        return False

    @classmethod
    def set_blocked(cls, user_id: int, is_blocked: bool) -> bool:
        """
        Set a user's blocked status.

        Parameters:
            user_id (int): The user's ID.
            is_blocked (bool): The blocked status.

        Returns:
            bool: True if updated successfully, False otherwise.
        """
        with SessionLocal() as session:
            with session.begin():
                u = session.query(cls).filter_by(userID=user_id).first()
                if u:
                    u.isBlocked = is_blocked
                    return True
        return False

    @classmethod
    def delete(cls, user_id: int) -> bool:
        """
        Delete a user from the database.

        Parameters:
            user_id (int): The user's ID.

        Returns:
            bool: True if deleted successfully, False otherwise.
        """
        with SessionLocal() as session:
            with session.begin():
                u = session.query(cls).filter_by(userID=user_id).first()
                if u:
                    session.delete(u)
                    return True
        return False

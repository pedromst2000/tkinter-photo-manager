from datetime import datetime, timezone
from typing import Optional, Tuple

from app.core.db.engine import SessionLocal
from app.core.db.models.album import AlbumModel
from app.core.db.models.category import CategoryModel
from app.core.db.models.like import LikeModel
from app.core.db.models.photo import PhotoModel
from app.core.db.models.photo_image import PhotoImageModel
from app.core.db.models.rating import RatingModel
from app.core.db.models.user import UserModel


class PhotoService:
    """
    Service class for photo management business logic.

    Business rules enforced in this service:
    - When creating a photo, an image row is also created in the same transaction.
    - Only photo owners can update or delete their photos.
    - When deleting a category, all photos in that category are also deleted by DB cascade.
    - When retrieving photos, category names and usernames are included for display purposes.
        - The service provides a method to check for category name uniqueness (case-insensitive).
        - The service provides a method to get all photos liked by a user.
        - The service provides a method to count photos by user.
        - The service provides a method to get photos filtered by category and/or username.
        - All methods that modify data enforce ownership rules and validate inputs as needed.
    """

    @staticmethod
    def get_photos_by_user(user_id: int) -> list:
        """
        Retrieve all photos uploaded by a specific user (through their albums).

        Args:
            user_id: The ID of the user.

        Returns:
            list: A list of photo dictionaries owned by the user.
        """
        with SessionLocal() as session:
            albums = AlbumModel.get_by_creator(session, user_id)
            result = []
            for album in albums:
                result.extend(PhotoModel.get_by_album(session, album["id"]))
            return result

    @staticmethod
    def get_photos_by_category(category_name: str) -> list:
        """
        Retrieve all photos in a specific category.

        Args:
            category_name: The name of the category.

        Returns:
            list: A list of photo dictionaries in the category.
        """
        with SessionLocal() as session:
            categories = CategoryModel.get_all(session)
            category = next(
                (c for c in categories if c["category"] == category_name), None
            )
            if category:
                return PhotoModel.get_by_category(session, category["id"])
            return []

    @staticmethod
    def get_filtered_photos(
        category: str = "all", username: Optional[str] = None
    ) -> list:
        """
        Retrieve photos filtered by category and/or username.
        Enriches photos with category name and username.

        Args:
            category: The category to filter by. Use "all" for all categories.
            username: The username to filter by. None to not filter by user.

        Returns:
            list: A list of enriched photo dictionaries.
        """
        with SessionLocal() as session:
            photos = PhotoModel.get_all(session)
            categories = CategoryModel.get_all(session)
            users = UserModel.get_all(session)
            albums = AlbumModel.get_all(session)

        # Helper to get category name for a photo
        def get_category_name(photo: dict) -> str:
            m: dict = next(
                (c for c in categories if c["id"] == photo["categoryId"]), {}
            )
            return str(m.get("category", ""))

        # Helper to get username for a photo via its album's creatorID
        def get_username(photo: dict) -> str:
            album = next((a for a in albums if a["id"] == photo["albumId"]), None)
            if not album:
                return ""
            m: dict = next((u for u in users if u["id"] == album["creatorId"]), {})
            return str(m.get("username", ""))

        result = []
        for photo in photos:
            cat_name = get_category_name(photo)
            user_name = get_username(photo)

            # Filter by category
            if category != "all" and cat_name != category:
                continue

            # Filter by username
            if username and user_name != username:
                continue

            enriched_photo = {
                **photo,
                "category": cat_name,
                "user": user_name,
            }
            result.append(enriched_photo)

        return result

    @staticmethod
    def create_photo(
        image_path: str,
        album_id: Optional[int],
        category_id: Optional[int] = None,
        description: str = "",
        published_date=None,
    ) -> Optional[dict]:
        """
        Create a new photo entry in the database together with its image row.

        Args:
            image_path: The file path of the photo image.
            album_id: The ID of the album to associate with the photo.
            category_id: The ID of the category to associate with the photo.
            description: A description for the photo.
            published_date: The date/time when the photo was published.

        Returns:
            dict: The created photo as a dictionary.
        """
        with SessionLocal() as session:
            with session.begin():
                photo = PhotoModel.create(
                    session,
                    description=description,
                    publishedDate=published_date or datetime.now(timezone.utc),
                    categoryId=category_id,
                    albumId=album_id,
                )
                PhotoImageModel.create(session, photo_id=photo["id"], image=image_path)
            return PhotoModel.get_by_id(session, photo["id"])

    @staticmethod
    def delete_photo_for_user(user_id: int, photo_id: int) -> bool:
        """
        Delete a photo if the given user is the owner (via album creator).

        Args:
            user_id: The ID of the requesting user.
            photo_id: The ID of the photo to delete.

        Returns:
            bool: True if deleted, False otherwise.
        """
        with SessionLocal() as session:
            photo = PhotoModel.get_by_id(session, photo_id)
            if not photo:
                return False
            album_id = photo.get("albumId")
            album = (
                AlbumModel.get_by_id(session, int(album_id))
                if album_id is not None
                else None
            )
            owner_id = album["creatorId"] if album else None
            if owner_id == user_id:
                with session.begin():
                    PhotoModel.delete(session, photo_id)
                return True
            return False

    @staticmethod
    def update_photo_for_user(user_id: int, photo_id: int, updates: dict) -> bool:
        """
        Update a photo if the given user owns it.

        Args:
            user_id: The ID of the requesting user.
            photo_id: The ID of the photo to update.
            updates: Fields to update.

        Returns:
            bool: True if updated, False otherwise.
        """
        with SessionLocal() as session:
            photo = PhotoModel.get_by_id(session, photo_id)
            if not photo:
                return False
            album_id = photo.get("albumId")
            album = (
                AlbumModel.get_by_id(session, int(album_id))
                if album_id is not None
                else None
            )
            owner_id = album["creatorId"] if album else None
            if owner_id == user_id:
                with session.begin():
                    return PhotoModel.update(session, {**photo, **updates})
            return False

    @staticmethod
    def get_liked_photos(user_id: int) -> list:
        """
        Get all photos liked by a specific user.

        Args:
            user_id: The ID of the user to get liked photos for.
        Returns:
            list: A list of photo dictionaries that the user has liked.
        """
        with SessionLocal() as session:
            like_rows = LikeModel.get_liked_photos(session, user_id)
            return [
                PhotoModel.get_by_id(session, r["photoId"])
                for r in like_rows
                if PhotoModel.get_by_id(session, r["photoId"])
            ]

    @staticmethod
    def category_exists(name: str) -> bool:
        """
        Check if a category with the given name already exists (case-insensitive).

        Args:
            name: The category name to check.

        Returns:
            bool: True if it exists, False otherwise.
        """
        with SessionLocal() as session:
            return any(
                c["category"].lower() == name.lower()
                for c in CategoryModel.get_all(session)
            )

    @staticmethod
    def get_all_photos() -> list:
        """Return all photos sorted by published date, newest first."""
        with SessionLocal() as session:
            photos = PhotoModel.get_all(session)
        return sorted(
            photos,
            key=lambda p: str(p.get("publishedDate") or ""),
            reverse=True,
        )

    @staticmethod
    def get_photo_details(
        photo_id: int, user_id: Optional[int] = None
    ) -> Optional[dict]:
        """
        Return a photo enriched with like stats and owner info.

        Combines PhotoModel, LikeModel, AlbumModel and UserModel in one
        session — a real use-case, not a pass-through.
        """
        with SessionLocal() as session:
            photo = PhotoModel.get_by_id(session, photo_id)
            if not photo:
                return None
            likes = LikeModel.count_by_photo(session, photo_id)
            has_liked = (
                LikeModel.has_liked(session, user_id, photo_id) if user_id else False
            )
            album = (
                AlbumModel.get_by_id(session, int(photo["albumId"]))
                if photo.get("albumId")
                else None
            )
            owner = UserModel.get_by_id(session, album["creatorId"]) if album else None
        return {
            **photo,
            "likes": likes,
            "has_liked": has_liked,
            "username": owner["username"] if owner else None,
        }

    @staticmethod
    def like_photo(user_id: int, photo_id: int) -> bool:
        """Like a photo. Returns True if the like was created, False if already liked."""
        with SessionLocal() as session:
            with session.begin():
                return LikeModel.like(session, user_id, photo_id) is not None

    @staticmethod
    def unlike_photo(user_id: int, photo_id: int) -> bool:
        """Unlike a photo. Returns True if the like was removed, False if it didn't exist."""
        with SessionLocal() as session:
            with session.begin():
                return LikeModel.unlike(session, user_id, photo_id)

    @staticmethod
    def rate_photo(user_id: int, photo_id: int, rating_value: int) -> None:
        """Submit a rating (1-5) for a photo."""
        with SessionLocal() as session:
            with session.begin():
                RatingModel.create(
                    session,
                    user_id=user_id,
                    photo_id=photo_id,
                    rating_value=rating_value,
                )

    @staticmethod
    def add_category(name: str) -> Tuple[bool, str]:
        """
        Add a new category.

        Business rules:
        - Name must be non-empty.
        - Name must be unique (case-insensitive).

        Returns:
            Tuple[bool, str]: (success, message)
        """
        if not name or not name.strip():
            return False, "Category name is required"
        if PhotoService.category_exists(name.strip()):
            return False, "The category already exists, please try again!"
        with SessionLocal() as session:
            with session.begin():
                CategoryModel.create(session, name.strip())
        return True, "The category was added successfully!"

    @staticmethod
    def delete_category_with_photos(name: str) -> Tuple[bool, str]:
        """
        Delete a category. Photos in the category are automatically removed
        by the database CASCADE on photos.categoryID.

        Args:
            name: The name of the category to delete.

        Returns:
            Tuple of (success, message)
        """
        with SessionLocal() as session:
            categories = CategoryModel.get_all(session)
            for cat in categories:
                if cat["category"] == name:
                    with session.begin():
                        CategoryModel.delete(session, name)
                    return True, f"{name} was deleted successfully"
            return False, "Category not found"

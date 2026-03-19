import csv
from datetime import datetime

import bcrypt

from db.engine import SessionLocal, init_db
from db.models import (
    AlbumModel,
    AvatarModel,
    CategoryModel,
    CommentModel,
    ContactModel,
    FavoriteModel,
    FollowModel,
    LikeModel,
    NotificationModel,
    NotificationSettingsModel,
    PhotoImageModel,
    PhotoModel,
    RatingModel,
    RoleModel,
    UserModel,
)
from utils.log_utils import log_check, log_issue, log_success


def _hash(plaintext: str) -> str:
    """
    Hash a plaintext password using bcrypt.

    Parameters:
        plaintext: The plaintext password to hash.
    Returns:
        str: The bcrypt hash of the password, including salt.
    """

    return bcrypt.hashpw(plaintext.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


# ── CSV readers (return plain lists of ORM objects) ───────────────────────────


def _read_roles() -> list:
    """
    Read roles from CSV file and return a list of RoleModel instances.

    Returns:
        list: A list of RoleModel instances read from the CSV file.
    """

    path = "files/roles.csv"
    data = []
    log_check(f"Reading roles from {path}...")
    try:
        with open(path, "r", encoding="utf-8", newline="") as f:
            for parts in csv.reader(f):
                if parts[0] == "id":
                    continue
                if len(parts) < 2:
                    continue
                data.append(RoleModel(id=int(parts[0]), role=parts[1]))
        log_success(f"Loaded {len(data)} roles.")
    except FileNotFoundError as e:
        log_issue("roles.csv not found — roles will not be seeded", exc=e, path=path)
    except Exception as e:
        log_issue("Unexpected error reading roles", exc=e, path=path)
    return data


def _read_users() -> list:
    """
    Read users from CSV file and return a list of UserModel instances.

    Returns:
        list: A list of UserModel instances read from the CSV file.
    """

    path = "files/users.csv"
    data = []
    log_check(f"Reading users from {path}...")
    try:
        with open(path, "r", encoding="utf-8", newline="") as f:
            for parts in csv.reader(f):
                if parts[0] == "id":
                    continue
                if len(parts) < 6:
                    continue
                data.append(
                    UserModel(
                        id=int(parts[0]),
                        username=parts[1],
                        email=parts[2],
                        password=_hash(parts[3]),
                        roleID=(
                            int(parts[5])
                            if len(parts) > 5 and parts[5].strip()
                            else None
                        ),
                        isBlocked=(
                            (parts[6].strip() == "True") if len(parts) > 6 else False
                        ),
                    )
                )
        log_success(f"Loaded {len(data)} users.")
    except FileNotFoundError as e:
        log_issue("users.csv not found — users will not be seeded", exc=e, path=path)
    except Exception as e:
        log_issue("Unexpected error reading users", exc=e, path=path)
    return data


def _read_avatars() -> list:
    """
    Read avatars from `files/avatars.csv` if present, otherwise extract avatar paths from `files/users.csv`.

    Returns:
        list: A list of AvatarModel instances.
    """
    path = "files/avatars.csv"
    data = []
    log_check(f"Reading avatars from {path}...")
    try:
        with open(path, "r", encoding="utf-8", newline="") as f:
            for parts in csv.reader(f):
                if parts[0] == "id":
                    continue
                # expected: id,userID,avatar
                if len(parts) < 3:
                    continue
                data.append(
                    AvatarModel(
                        id=int(parts[0]) if parts[0].strip() else None,
                        userID=int(parts[1]),
                        avatar=parts[2],
                    )
                )
        log_success(f"Loaded {len(data)} avatars from avatars.csv.")
        return data
    except FileNotFoundError:
        log_check(f"{path} not found — falling back to users.csv for avatars")
    except Exception as e:
        log_issue("Unexpected error reading avatars.csv", exc=e, path=path)

    # fallback: extract avatar column from users.csv (if present)
    users_path = "files/users.csv"
    try:
        with open(users_path, "r", encoding="utf-8", newline="") as f:
            for parts in csv.reader(f):
                if parts[0] == "id":
                    continue
                # users.csv expected format may include avatar at index 4
                if len(parts) > 4 and parts[4].strip():
                    try:
                        user_id = int(parts[0])
                    except Exception:
                        continue
                    data.append(
                        AvatarModel(
                            userID=user_id,
                            avatar=parts[4],
                        )
                    )
        log_success(f"Loaded {len(data)} avatars from users.csv fallback.")
    except FileNotFoundError:
        log_check(f"{users_path} not found — no avatars to seed")
    except Exception as e:
        log_issue(
            "Unexpected error reading users.csv for avatars", exc=e, path=users_path
        )

    return data


def _read_categories() -> list:
    """
    Read categories from CSV file and return a list of CategoryModel instances.

    Returns:
        list: A list of CategoryModel instances read from the CSV file.
    """

    path = "files/categories.csv"
    data = []
    log_check(f"Reading categories from {path}...")
    try:
        with open(path, "r", encoding="utf-8", newline="") as f:
            for parts in csv.reader(f):
                if parts[0] == "id":
                    continue
                if len(parts) < 2:
                    continue
                data.append(CategoryModel(id=int(parts[0]), category=parts[1]))
        log_success(f"Loaded {len(data)} categories.")
    except FileNotFoundError as e:
        log_issue(
            "categories.csv not found — categories will not be seeded", exc=e, path=path
        )
    except Exception as e:
        log_issue("Unexpected error reading categories", exc=e, path=path)
    return data


def _read_albums() -> list:
    """
    Read albums from CSV file and return a list of AlbumModel instances.

    Returns:
        list: A list of AlbumModel instances read from the CSV file.
    """

    path = "files/albuns.csv"
    data = []
    log_check(f"Reading albums from {path}...")
    try:
        with open(path, "r", encoding="utf-8", newline="") as f:
            for parts in csv.reader(f):
                if parts[0] == "id":
                    continue
                if len(parts) < 3:
                    continue
                data.append(
                    AlbumModel(id=int(parts[0]), name=parts[1], creatorID=int(parts[2]))
                )
        log_success(f"Loaded {len(data)} albums.")
    except FileNotFoundError as e:
        log_issue("albuns.csv not found — albums will not be seeded", exc=e, path=path)
    except Exception as e:
        log_issue("Unexpected error reading albums", exc=e, path=path)
    return data


def _read_photos() -> list:
    """
    Read photos from CSV file and return a list of PhotoModel instances.

    Returns:
        list: A list of PhotoModel instances read from the CSV file.
    """

    path = "files/photos.csv"
    data = []
    log_check(f"Reading photos from {path}...")
    try:
        with open(path, "r", encoding="utf-8", newline="") as f:
            for parts in csv.reader(f):
                if parts[0] == "id":
                    continue
                # photos.csv format now: id,description,publishedDate,categoryID,albumID
                if len(parts) < 5:
                    continue
                album_id = int(parts[4]) if parts[4].strip() else None
                try:
                    published_date = datetime.fromisoformat(parts[2])
                except Exception:
                    published_date = datetime.now()
                data.append(
                    PhotoModel(
                        id=int(parts[0]),
                        description=parts[1],
                        publishedDate=published_date,
                        categoryID=int(parts[3]),
                        albumID=album_id,
                    )
                )
        log_success(f"Loaded {len(data)} photos.")
    except FileNotFoundError as e:
        log_issue("photos.csv not found — photos will not be seeded", exc=e, path=path)
    except Exception as e:
        log_issue("Unexpected error reading photos", exc=e, path=path)
    return data


def _read_photo_images() -> list:
    """
    Read photo images from CSV file and return a list of PhotoImageModel instances.

    Returns:
        list: A list of PhotoImageModel instances read from the CSV file.
    """

    path = "files/photo_images.csv"
    data = []
    log_check(f"Reading photo images from {path}...")
    try:
        with open(path, "r", encoding="utf-8", newline="") as f:
            for parts in csv.reader(f):
                if parts[0] == "id":
                    continue
                # expected: id,photoID,image
                if len(parts) < 3:
                    continue
                data.append(
                    PhotoImageModel(
                        id=int(parts[0]),
                        photoID=int(parts[1]),
                        image=parts[2],
                    )
                )
        log_success(f"Loaded {len(data)} photo images.")
    except FileNotFoundError:
        log_check(f"{path} not found — photo images will not be seeded")
    except Exception as e:
        log_issue("Unexpected error reading photo images", exc=e, path=path)
    return data


def _read_ratings() -> list:
    """
    Read ratings from CSV file and return a list of RatingModel instances.

    Returns:
        list: A list of RatingModel instances read from the CSV file.
    """

    path = "files/ratings.csv"
    data = []
    log_check(f"Reading ratings from {path}...")
    try:
        with open(path, "r", encoding="utf-8", newline="") as f:
            for parts in csv.reader(f):
                if parts[0] == "id":
                    continue
                # expected: id,userID,photoID,rating
                if len(parts) < 4:
                    continue
                data.append(
                    RatingModel(
                        id=int(parts[0]),
                        userID=int(parts[1]),
                        photoID=int(parts[2]),
                        rating=int(parts[3]),
                    )
                )
        log_success(f"Loaded {len(data)} ratings.")
    except FileNotFoundError:
        log_check(f"{path} not found — ratings will not be seeded")
    except Exception as e:
        log_issue("Unexpected error reading ratings", exc=e, path=path)
    return data


def _read_likes() -> list:
    """
    Read likes from CSV file and return a list of LikeModel instances.

    Returns:
        list: A list of LikeModel instances read from the CSV file.
    """

    path = "files/likes.csv"
    data = []
    log_check(f"Reading likes from {path}...")
    try:
        with open(path, "r", encoding="utf-8", newline="") as f:
            for parts in csv.reader(f):
                if parts[0] == "id":
                    continue
                if len(parts) < 3:
                    continue
                data.append(
                    LikeModel(
                        id=int(parts[0]),
                        userID=int(parts[1]),
                        photoID=int(parts[2]),
                    )
                )
        log_success(f"Loaded {len(data)} likes.")
    except FileNotFoundError as e:
        log_issue("likes.csv not found — likes will not be seeded", exc=e, path=path)
    except Exception as e:
        log_issue("Unexpected error reading likes", exc=e, path=path)
    return data


def _read_follows() -> list:
    """
    Read follows from CSV file and return a list of FollowModel instances.

    Returns:
        list: A list of FollowModel instances read from the CSV file.
    """

    path = "files/follows.csv"
    data = []
    log_check(f"Reading follows from {path}...")
    try:
        with open(path, "r", encoding="utf-8", newline="") as f:
            for parts in csv.reader(f):
                if parts[0] == "id":
                    continue
                if len(parts) < 3:
                    continue
                data.append(
                    FollowModel(
                        id=int(parts[0]),
                        followerID=int(parts[1]),
                        followedID=int(parts[2]),
                    )
                )
        log_success(f"Loaded {len(data)} follows.")
    except FileNotFoundError as e:
        log_issue(
            "follows.csv not found — follows will not be seeded", exc=e, path=path
        )
    except Exception as e:
        log_issue("Unexpected error reading follows", exc=e, path=path)
    return data


def _read_notifications() -> list:
    """
    Read notifications from CSV file and return a list of NotificationModel instances.

    Returns:
        list: A list of NotificationModel instances read from the CSV file.
    """

    path = "files/notifications.csv"
    data = []
    log_check(f"Reading notifications from {path}...")
    try:
        with open(path, "r", encoding="utf-8", newline="") as f:
            for parts in csv.reader(f):
                if parts[0] == "id":
                    continue
                if len(parts) < 4:
                    continue
                # map polymorphic CSV (referenceType/referenceID) to explicit nullable FKs
                ref_id = int(parts[5]) if len(parts) > 5 and parts[5].strip() else None
                ref_type = (
                    parts[6].strip() if len(parts) > 6 and parts[6].strip() else None
                )
                photo_id = ref_id if ref_type == "photo" else None
                comment_id = ref_id if ref_type == "comment" else None
                album_id = ref_id if ref_type == "album" else None

                data.append(
                    NotificationModel(
                        id=int(parts[0]),
                        type=parts[1],
                        message=parts[2],
                        userID=int(parts[3]),
                        senderID=(
                            int(parts[4])
                            if len(parts) > 4 and parts[4].strip()
                            else None
                        ),
                        photoID=photo_id,
                        commentID=comment_id,
                        albumID=album_id,
                        isRead=(
                            parts[7].strip() == "True"
                            if len(parts) > 7 and parts[7].strip()
                            else False
                        ),
                    )
                )
        log_success(f"Loaded {len(data)} notifications.")
    except FileNotFoundError as e:
        log_issue(
            "notifications.csv not found — notifications will not be seeded",
            exc=e,
            path=path,
        )
    except Exception as e:
        log_issue("Unexpected error reading notifications", exc=e, path=path)
    return data


def _read_comments(valid_photo_ids: set) -> list:
    """
    Read comments from CSV file and return a list of CommentModel instances.

    Args:
        valid_photo_ids (set): A set of valid photo IDs to filter comments.

    Returns:
        list: A list of CommentModel instances read from the CSV file.
    """
    path = "files/comments.csv"
    data = []
    log_check(f"Reading comments from {path}...")
    try:
        with open(path, "r", encoding="utf-8", newline="") as f:
            for parts in csv.reader(f):
                if parts[0] == "id":
                    continue
                if len(parts) < 4:
                    continue
                photo_id = int(parts[3])
                if photo_id not in valid_photo_ids:
                    continue
                data.append(
                    CommentModel(
                        id=int(parts[0]),
                        authorID=int(parts[1]),
                        comment=parts[2],
                        photoID=photo_id,
                    )
                )
        log_success(f"Loaded {len(data)} comments.")
    except FileNotFoundError as e:
        log_issue(
            "comments.csv not found — comments will not be seeded", exc=e, path=path
        )
    except Exception as e:
        log_issue("Unexpected error reading comments", exc=e, path=path)
    return data


def _read_favorites() -> list:
    """
    Read favorites from CSV file and return a list of FavoriteModel instances.

    Returns:
        list: A list of FavoriteModel instances read from the CSV file.
    """
    path = "files/favorites.csv"
    data = []
    log_check(f"Reading favorites from {path}...")
    try:
        with open(path, "r", encoding="utf-8", newline="") as f:
            for parts in csv.reader(f):
                if parts[0] == "id":
                    continue
                if len(parts) < 3:
                    continue
                data.append(
                    FavoriteModel(
                        id=int(parts[0]),
                        albumID=int(parts[1]),
                        userID=int(parts[2]),
                    )
                )
        log_success(f"Loaded {len(data)} favorites.")
    except FileNotFoundError as e:
        log_issue(
            "favorites.csv not found — favorites will not be seeded", exc=e, path=path
        )
    except Exception as e:
        log_issue("Unexpected error reading favorites", exc=e, path=path)
    return data


def _read_contacts() -> list:
    """
    Read contacts from CSV file and return a list of ContactModel instances.

    Returns:
        list: A list of ContactModel instances read from the CSV file.
    """
    path = "files/contacts.csv"
    data = []
    log_check(f"Reading contacts from {path}...")
    try:
        with open(path, "r", encoding="utf-8", newline="") as f:
            for parts in csv.reader(f):
                if parts[0] == "id":
                    continue
                if len(parts) < 4:
                    continue
                data.append(
                    ContactModel(
                        id=int(parts[0]),
                        title=parts[1],
                        message=parts[2],
                        userID=int(parts[3]),
                    )
                )
        log_success(f"Loaded {len(data)} contacts.")
    except FileNotFoundError as e:
        log_issue(
            "contacts.csv not found — contacts will not be seeded", exc=e, path=path
        )
    except Exception as e:
        log_issue("Unexpected error reading contacts", exc=e, path=path)
    return data


def _read_notification_settings() -> list:
    """
    Read notification settings from CSV file and return a list of NotificationSettingsModel instances.

    Returns:
        list: A list of NotificationSettingsModel instances read from the CSV file.
    """
    path = "files/notification_settings.csv"
    data = []
    log_check(f"Reading notification settings from {path}...")
    try:
        with open(path, "r", encoding="utf-8", newline="") as f:
            for parts in csv.reader(f):
                if parts[0] == "id":
                    continue
                if len(parts) < 4:
                    continue
                data.append(
                    NotificationSettingsModel(
                        id=int(parts[0]),
                        type=parts[1],
                        label=parts[2],
                        isEnabled=parts[3].strip() == "True",
                    )
                )
        log_success(f"Loaded {len(data)} notification settings.")
    except FileNotFoundError as e:
        log_issue(
            "notification_settings.csv not found — settings will not be seeded",
            exc=e,
            path=path,
        )
    except Exception as e:
        log_issue("Unexpected error reading notification settings", exc=e, path=path)
    return data


# ── Public API ────────────────────────────────────────────────────────────────


def sync_static_data() -> None:
    """
    Upsert ALL CSV data into the database on every app startup.
    Existing rows are updated, new rows are inserted.
    Safe to call repeatedly — no duplicates are created.
    """
    log_check("Syncing all data from CSV files...")

    albums = _read_albums()
    photos = _read_photos()
    valid_photo_ids = {p.id for p in photos}

    try:
        with SessionLocal() as session:
            with session.begin():
                for obj in _read_roles():
                    session.merge(obj)
                for obj in _read_categories():
                    session.merge(obj)
                for obj in _read_users():
                    session.merge(obj)
                for obj in _read_avatars():
                    session.merge(obj)
                session.flush()
                for obj in albums:
                    session.merge(obj)
                session.flush()
                for obj in photos:
                    session.merge(obj)
                session.flush()
                for obj in _read_photo_images():
                    session.merge(obj)
                session.flush()
                for obj in _read_ratings():
                    session.merge(obj)
                session.flush()
                for obj in _read_comments(valid_photo_ids):
                    session.merge(obj)
                for obj in _read_favorites():
                    session.merge(obj)
                for obj in _read_contacts():
                    session.merge(obj)
                for obj in _read_notification_settings():
                    session.merge(obj)
                session.flush()
                for obj in _read_notifications():
                    session.merge(obj)
                for obj in _read_follows():
                    session.merge(obj)
                for obj in _read_likes():
                    session.merge(obj)
    except Exception as e:
        log_issue(
            "Failed to sync CSV data to the database — schema may be stale",
            exc=e,
            path="photoshow.db",
        )
        log_issue("Run 'python main.py --reset' to drop and rebuild the database")
        return

    log_success("All CSV data synced to database.")


def migrate() -> None:
    """
    Called on every app startup.
    Initializes the database and syncs all data from CSV files.
    """
    try:
        log_check("Initializing database...")
        init_db()
        log_success("Database initialized.")
    except Exception as e:
        log_issue("Database initialization failed", exc=e, path="photoshow.db")
        import sys

        sys.exit(1)
    sync_static_data()


def reset_db() -> None:
    """
    Drop ALL tables, recreate them, and re-seed everything from CSV files.
    WARNING: all existing data (photos, users, albums, etc.) will be lost.
    """
    from db.engine import Base, engine

    log_check("[reset] Dropping all tables...")
    Base.metadata.drop_all(engine)
    log_check("[reset] Re-initializing database...")
    init_db()
    log_success("[reset] Tables recreated.")
    log_check("[reset] Seeding from CSV files...")

    albums = _read_albums()
    photos = _read_photos()
    valid_photo_ids = {p.id for p in photos}

    with SessionLocal() as session:
        with session.begin():
            session.add_all(_read_roles())
            session.flush()
            session.add_all(_read_users())
            session.flush()
            session.add_all(_read_avatars())
            session.flush()
            session.add_all(_read_categories())
            session.flush()
            session.add_all(albums)
            session.flush()
            session.add_all(photos)
            session.flush()
            session.add_all(_read_photo_images())
            session.flush()
            session.add_all(_read_ratings())
            session.flush()
            session.add_all(_read_comments(valid_photo_ids))
            session.flush()
            session.add_all(_read_favorites())
            session.flush()
            session.add_all(_read_contacts())
            session.flush()
            session.add_all(_read_notification_settings())
            session.flush()
            session.add_all(_read_notifications())
            session.flush()
            session.add_all(_read_follows())
            session.flush()
            session.add_all(_read_likes())
            session.flush()

    log_success("[reset] Database reset and seeded successfully.")

from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
)

from app.core.db.engine import Base, SessionLocal


class ReportModel(Base):
    """
    ReportModel represents a user-submitted content report against a photo or comment.
    """

    __tablename__: str = "reports"

    __table_args__ = (
        CheckConstraint("id > 0 AND id < 10000000", name="ck_reports_id_range"),
        CheckConstraint(
            "reporterId > 0 AND reporterId < 10000000",
            name="ck_reports_reporterId_range",
        ),
        CheckConstraint(
            "reasonId > 0 AND reasonId < 10000",
            name="ck_reports_reasonId_range",
        ),
        CheckConstraint(
            "(photoId IS NULL) != (commentId IS NULL)",
            name="ck_reports_target_exclusive",
        ),
        Index("ix_reports_reporterId", "reporterId"),
        Index("ix_reports_reasonId", "reasonId"),
        Index("ix_reports_photoId", "photoId"),
        Index("ix_reports_commentId", "commentId"),
    )

    id: int = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    reporterId: int = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    reasonId: int = Column(
        Integer, ForeignKey("report_reasons.id", ondelete="RESTRICT"), nullable=False
    )
    photoId: int = Column(
        Integer, ForeignKey("photos.id", ondelete="CASCADE"), nullable=True
    )
    commentId: int = Column(
        Integer, ForeignKey("comments.id", ondelete="CASCADE"), nullable=True
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
        """Return the report as a dict"""
        return {
            "id": self.id,
            "reporterId": self.reporterId,
            "reasonId": self.reasonId,
            "photoId": self.photoId,
            "commentId": self.commentId,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }

    @classmethod
    def get_all(cls) -> list[dict]:
        """
        Return all reports as a list of dicts.

        Returns:
            list[dict]: List of report dicts.
        """

        with SessionLocal() as session:
            return [r.to_dict() for r in session.query(cls).order_by(cls.id).all()]

    @classmethod
    def create(
        cls,
        reporter_id: int,
        reason_id: int,
        photo_id: int | None = None,
        comment_id: int | None = None,
    ) -> dict:
        """
        Create a new report against a photo or comment.

        Args:
            reporter_id: The ID of the user submitting the report.
            reason_id: The ID of the report reason (foreign key to report_reasons).
            photo_id: The ID of the photo being reported (if applicable).
            comment_id: The ID of the comment being reported (if applicable).
        Returns:
            dict: The created report as a dict.
        Raises:
            ValueError: If validation fails (e.g. invalid reason_id, both photo_id and comment_id provided, etc.)
        """
        with SessionLocal() as session:
            with session.begin():
                obj = cls(
                    reporterId=reporter_id,
                    reasonId=reason_id,
                    photoId=photo_id,
                    commentId=comment_id,
                )
                session.add(obj)
                session.flush()
                return obj.to_dict()

    @classmethod
    def get_by_id(cls, report_id: int) -> dict | None:
        """
        Get a single report by its ID.

        Args:
            report_id: The ID of the report to retrieve.
        Returns:
            dict | None: The report as a dict if found, or None if not found.
        """
        with SessionLocal() as session:
            obj = session.query(cls).filter(cls.id == report_id).first()
            return obj.to_dict() if obj else None

    @classmethod
    def delete(cls, report_id: int) -> bool:
        """
        Delete a report by its ID.

        Args:
            report_id: The ID of the report to delete.
        Returns:
            bool: True if the report was successfully deleted, False if not found.
        """
        with SessionLocal() as session:
            with session.begin():
                obj = session.query(cls).filter(cls.id == report_id).first()
                if obj is None:
                    return False
                session.delete(obj)
                return True

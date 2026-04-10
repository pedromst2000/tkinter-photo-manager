from typing import Optional, Tuple

from app.core.db.engine import SessionLocal
from app.core.db.models.report import ReportModel
from app.core.db.models.report_reason import ReportReasonModel
from app.utils.log_utils import log_issue


class ReportService:
    """
    Service class for content-report business logic.

    Business rules enforced:
    - Reason label must be non-empty and map to a valid report_reasons row.
    - Admins cannot submit reports.
    - Exactly one of photo_id / comment_id must be provided.
    """

    @staticmethod
    def resolve_report(report_id: int) -> bool:
        """Delete (resolve) a report. Returns True if deleted, False if not found."""
        with SessionLocal() as session:
            with session.begin():
                return ReportModel.delete(session, report_id)

    @staticmethod
    def submit_report(
        reporter_id: int,
        reason: str,
        photo_id: Optional[int] = None,
        comment_id: Optional[int] = None,
    ) -> Tuple[bool, str]:
        """
        Submit a content report against a photo or comment.

        Business rules enforced:
        - Reason label must be non-empty and map to a valid report_reasons row.
        - Admins cannot submit reports.
        - Exactly one of photo_id / comment_id must be provided.

        Args:
            reporter_id: The ID of the user submitting the report.
            reason: The reason label chosen by the reporter.
            photo_id: The ID of the photo being reported (if applicable).
            comment_id: The ID of the comment being reported (if applicable).
        Returns:
            Tuple[bool, str]: (success, message)
        """
        if not reason or not reason.strip():
            return False, "A reason is required"

        if (photo_id is None) == (comment_id is None):
            return False, "Exactly one of photo or comment must be specified"

        try:
            with SessionLocal() as session:
                from app.core.db.models.user import UserModel

                reporter = UserModel.get_by_id(session, reporter_id)
                if reporter and reporter.get("roleId") == 1:
                    return False, "Admins cannot submit reports"

                with session.begin():
                    reason_record = ReportReasonModel.get_by_label(session, reason)
                    if not reason_record:
                        return False, "Invalid reason"

                    ReportModel.create(
                        session,
                        reporter_id=reporter_id,
                        reason_id=reason_record["id"],
                        photo_id=photo_id,
                        comment_id=comment_id,
                    )
            return (
                True,
                "Your report has been submitted and will be reviewed by an admin",
            )
        except Exception as e:
            log_issue("ReportService.submit_report failed", exc=e)
            return False, "Failed to submit report. Please try again"

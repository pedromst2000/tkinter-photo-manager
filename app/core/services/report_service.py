from typing import Optional, Tuple

from app.core.db.models import ReportModel
from app.core.db.models.report_reason import ReportReasonModel
from app.utils.log_utils import log_issue


class ReportService:
    """
    Service class for content-report business logic.

    Handles report creation (by regular users), report listing for admin,
    and report resolution / dismissal.
    """

    @staticmethod
    def get_reason_labels() -> list[str]:
        """
        Return the list of valid report-reason labels (Inappropriate content, Spam, Harassment, Other).

        Returns:
            list[str]: Ordered list of reason label strings.
        """
        return ReportReasonModel.get_labels()

    @staticmethod
    def submit_report(
        reporter_id: int,
        reason: str,
        photo_id: Optional[int] = None,
        comment_id: Optional[int] = None,
    ) -> Tuple[bool, str]:
        """
        Submit a content report against a photo or comment.
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

        from app.core.db.models.user import UserModel

        reporter = UserModel.get_by_id(reporter_id)
        if reporter and reporter.get("roleId") == 1:
            return False, "Admins cannot submit reports"

        # map label -> id
        reason_record = ReportReasonModel.get_by_label(reason)
        if not reason_record:
            return False, "Invalid reason"
        reason_id = reason_record["id"]

        if (photo_id is None) == (comment_id is None):
            return False, "Exactly one of photo or comment must be specified"

        try:
            ReportModel.create(
                reporter_id=reporter_id,
                reason_id=reason_id,
                photo_id=photo_id,
                comment_id=comment_id,
            )
            return (
                True,
                "Your report has been submitted and will be reviewed by an admin",
            )
        except ValueError as e:
            return False, str(e)
        except Exception as e:
            # Log the real error for diagnostics; never expose internal details to the user.
            # from app.utils.log_utils import log_issue # import here to avoid circular import!
            log_issue("ReportService.submit_report failed", exc=e)
            return False, "Failed to submit report. Please try again"

    @staticmethod
    def get_all_reports() -> list:
        """
        Return all reports as a list of dicts.

        Returns:
            list[dict]: List of report dicts.
        """

        return ReportModel.get_all()

    @staticmethod
    def get_report_by_id(report_id: int) -> Optional[dict]:
        """
        Return a single report row (plain dict, not enriched).

        Args:
            report_id: The ID of the report.

        Returns:
            dict or None: The report dict if found, None otherwise.
        """
        return ReportModel.get_by_id(report_id)

    @staticmethod
    def resolve_report(report_id: int) -> Tuple[bool, str]:
        """
        Resolve a report by deleting it from the database.

        Args:
            report_id: The ID of the report to resolve.
        Returns:
            Tuple[bool, str]: (success, message)
        """
        if ReportModel.delete(report_id):
            return True, "Report resolved and removed"
        return False, "Report not found"

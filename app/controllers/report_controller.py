from typing import List, Tuple

from app.core.db.engine import SessionLocal
from app.core.db.models.report import ReportModel
from app.core.db.models.report_reason import ReportReasonModel
from app.core.services.report_service import ReportService
from app.core.state.session import session


class ReportController:
    """
    Controller for report operations.

    Coordinates between views and services for:
    - Submitting reports for photos and comments (delegates to service)
    - Listing reports for admin review (direct model access — no business logic)
    - Retrieving a single report's details
    - Resolving (deleting) a report
    """

    @staticmethod
    def get_reason_labels() -> List[str]:
        """
        Return the list of valid report-reason labels for dropdown population.

        Returns:
            list[str]: Ordered list of reason label strings.
        """
        with SessionLocal() as db:
            return ReportReasonModel.get_labels(db)

    @staticmethod
    def report_photo(photo_id: int, reason: str) -> Tuple[bool, str]:
        """
        Submit a report against a photo.

        Args:
            photo_id: The ID of the photo being reported.
            reason: The reason label chosen by the reporter.
        Returns:
            Tuple[bool, str]: (success, message)
        """
        user_id = session.user_id
        if user_id is None:
            return False, "Unable to identify user"

        return ReportService.submit_report(
            reporter_id=user_id, reason=reason, photo_id=photo_id
        )

    @staticmethod
    def report_comment(comment_id: int, reason: str) -> Tuple[bool, str]:
        """
        Submit a report against a comment.

        Args:
            comment_id: The ID of the comment being reported.
            reason: The reason label chosen by the reporter.
        Returns:
            Tuple[bool, str]: (success, message)
        """
        user_id = session.user_id
        if user_id is None:
            return False, "Unable to identify user"

        return ReportService.submit_report(
            reporter_id=user_id, reason=reason, comment_id=comment_id
        )

    @staticmethod
    def get_all_reports() -> List[dict]:
        """
        Admin-only: return all reports (raw rows).

        Returns:
            list[dict]: List of report dicts, or empty list for non-admins.
        """
        with SessionLocal() as db:
            return ReportModel.get_all(db)

    @staticmethod
    def get_report(report_id: int) -> dict | None:
        """
        Admin-only: return a single report's raw data.

        Args:
            report_id: The ID of the report to retrieve.
        Returns:
            dict | None: The report data if found, else None.
        """
        with SessionLocal() as db:
            return ReportModel.get_by_id(db, report_id)

    @staticmethod
    def resolve_report(report_id: int) -> Tuple[bool, str]:
        """
        Admin-only: resolve a report by deleting it.

        Args:
            report_id: The ID of the report to resolve.
        Returns:
            Tuple[bool, str]: (success, message)
        """
        if ReportService.resolve_report(report_id):
            return True, "Report resolved and removed"
        return False, "Report not found"

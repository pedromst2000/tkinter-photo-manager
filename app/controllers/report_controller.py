from typing import List, Tuple

from app.core.services.report_service import ReportService
from app.core.state.session import session


class ReportController:
    """
    Controller for report operations.

    Coordinates between views and services for:
    - Submitting reports for photos and comments
    - Listing reports for admin review
    - Retrieving a single report's details
    """

    @staticmethod
    def get_reason_labels() -> List[str]:
        """
        Return the list of valid report-reason labels (Inappropriate content, Spam, Harassment, Other).

        Returns:
            list[str]: Ordered list of reason label strings.
        """

        return ReportService.get_reason_labels()

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
        Admin-only: return all reports (raw rows). Admin UI will request details separately.

        Returns:
            list[dict]: List of report dicts.
        """
        if not session.is_admin:
            return []
        return ReportService.get_all_reports()

    @staticmethod
    def get_report(report_id: int) -> dict | None:
        """Admin-only: return a single report's raw data.

        Args:
            report_id: The ID of the report to retrieve.
        Returns:
            dict | None: The report data if found, else None.
        """
        if not session.is_admin:
            return None
        return ReportService.get_report_by_id(report_id)

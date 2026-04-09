from sqlalchemy import (
    CheckConstraint,
    Column,
    Integer,
    String,
    UniqueConstraint,
)

from app.core.db.engine import Base, SessionLocal


class ReportReasonModel(Base):
    """
    ReportReasonModel stores canonical report reason categories.

    This table is the authoritative source for the reason labels used by the UI.
    The `reports` table stores `reasonId` as a foreign key to this table.

    Minimal helpers are provided for the UI/service layer:
    - `get_labels()` for populating dropdowns
    - `get_by_label()` for mapping a label to its DB row (used by services)
    - `to_dict()` for row serialization
    """

    __tablename__: str = "report_reasons"

    __table_args__ = (
        UniqueConstraint("label", name="uq_report_reasons_label"),
        CheckConstraint("id > 0 AND id < 10000", name="ck_report_reasons_id_range"),
        CheckConstraint(
            "length(trim(label)) > 0", name="ck_report_reasons_label_not_empty"
        ),
        CheckConstraint("length(label) <= 50", name="ck_report_reasons_label_maxlen"),
    )

    id: int = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    label: str = Column(String(50), unique=True, nullable=False)

    def to_dict(self) -> dict:
        """
        Return a dict representation of the report reason.

         Returns:
            dict: A dict with keys 'id' and 'label'.
        """

        return {"id": self.id, "label": self.label}

    @classmethod
    def get_labels(cls) -> list[str]:
        """Return a list of report reason labels ordered by id."""
        with SessionLocal() as session:
            return [r.label for r in session.query(cls).order_by(cls.id).all()]

    @classmethod
    def get_by_label(cls, label: str) -> dict | None:
        """
        Return the report reason row matching the given label, or None if not found.

        Args:
            label: The reason label to look up.
        Returns:
            dict | None: The report reason row as a dict if found, else None.
        """
        with SessionLocal() as session:
            r = session.query(cls).filter_by(label=label).first()
            return r.to_dict() if r else None

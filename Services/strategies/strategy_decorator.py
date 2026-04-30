from datetime import datetime
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from Entities.attendance import AttendanceRow, AttendanceReport
from strategies.strategy_base import BaseTransformationStrategy, TransformationError


class ValidatingStrategyDecorator(BaseTransformationStrategy):
    """
    Decorator that wraps any BaseTransformationStrategy and validates its output.
    If validation fails, raises TransformationError so the service can fall back
    to the original row. Delegates enrich_report to the inner strategy.
    """

    def __init__(self, inner: BaseTransformationStrategy):
        self._inner = inner

    def transform_row(self, row: AttendanceRow) -> AttendanceRow:
        result = self._inner.transform_row(row)
        self._validate(result)
        return result

    def enrich_report(self, report: AttendanceReport) -> AttendanceReport:
        return self._inner.enrich_report(report)

    def _validate(self, row: AttendanceRow):
        if row.is_shabbat or row.is_holiday or not row.start or not row.end:
            return

        start = datetime.strptime(row.start, "%H:%M")
        end = datetime.strptime(row.end, "%H:%M")

        if end <= start:
            raise TransformationError(
                f"Exit time {row.end} is before entry time {row.start} on {row.date}"
            )

        duration_hours = (end - start).seconds / 3600
        if duration_hours < 2 or duration_hours > 12:
            raise TransformationError(
                f"Unreasonable work duration: {duration_hours:.1f} hours on {row.date}"
            )
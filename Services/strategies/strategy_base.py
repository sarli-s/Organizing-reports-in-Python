from abc import ABC, abstractmethod
from Entities.attendance import AttendanceRow, AttendanceReport


class TransformationError(Exception):
    pass


class BaseTransformationStrategy(ABC):
    @abstractmethod
    def transform_row(self, row: AttendanceRow) -> AttendanceRow:
        """Receives an original row and returns a transformed variant."""
        pass

    @abstractmethod
    def enrich_report(self, report: AttendanceReport) -> AttendanceReport:
        """Fills missing data based on report-wide statistics."""
        pass
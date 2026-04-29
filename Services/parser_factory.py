import re
import sys
import os
from abc import ABC, abstractmethod

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from Entities.attendance import AttendanceRow, AttendanceReport


class BaseParser(ABC):
    def __init__(self):
        self.date_pattern = r'(\d{1,2}/\d{1,2}/\d{2,4})'
        self.time_pattern = r'(\d{1,2}:\d{2})'

    def parse(self, raw_text: str) -> AttendanceReport:
        """
        Template Method: defines the skeleton of the parsing algorithm.
        Subclasses override _is_header_line, _parse_row, and _parse_summary.
        """
        lines = raw_text.split('\n')
        rows = []
        for line in lines:
            clean = line.strip()
            if not clean:
                continue
            if self._is_header_line(clean):
                continue
            row = self._parse_row(clean)
            if row:
                rows.append(row)

        summary = self._parse_summary(raw_text)
        return AttendanceReport(rows=tuple(rows), **summary)

    @abstractmethod
    def _is_header_line(self, line: str) -> bool:
        """Returns True if the line is a header or summary line to be skipped."""
        pass

    @abstractmethod
    def _parse_row(self, line: str) -> AttendanceRow | None:
        """Parses a single data line and returns an AttendanceRow, or None if not applicable."""
        pass

    @abstractmethod
    def _parse_summary(self, raw_text: str) -> dict:
        """Extracts report-level metadata: employee name, month, year, report type."""
        pass
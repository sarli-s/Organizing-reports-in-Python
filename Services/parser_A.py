import re
import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from parser_factory import BaseParser
from Entities.attendance import AttendanceRow, AttendanceReport

HEADER_KEYWORDS = ["כניסה", "יציאה", "הפסקה", "תאריך", "סה\"כ", "100%", "125%", "150%", "שבת", "ימים", "בונוס", "נסיעות"]
DAYS_HE = {
    "ראשון": "Sunday",
    "שני": "Monday",
    "שלישי": "Tuesday",
    "רביעי": "Wednesday",
    "חמישי": "Thursday",
    "שישי": "Friday",
    "שבת": "Saturday",
}

class ParserA(BaseParser):

    def _is_header_line(self, line: str) -> bool:
        return any(kw in line for kw in HEADER_KEYWORDS)

    def _parse_row(self, line: str) -> AttendanceRow | None:
        return None

    def _parse_summary(self, raw_text: str) -> dict:
        dates = re.findall(self.date_pattern, raw_text)
        if dates:
            anchor = datetime.strptime(dates[0], "%d/%m/%Y")
            return {
                "employee_name": "",
                "month": anchor.strftime("%m"),
                "year": anchor.strftime("%Y"),
                "report_type": "A",
            }
        return {
            "employee_name": "",
            "month": "",
            "year": "",
            "report_type": "A",
        }

    def parse(self, raw_text: str) -> AttendanceReport:
        """
        Overrides the Template Method to handle Type A reports.
        OCR does not preserve a date on every line, so dates are reconstructed
        by anchoring to the one visible date and counting time-pairs before it.
        """
        dates_found = re.findall(self.date_pattern, raw_text)
        all_times = re.findall(self.time_pattern, raw_text)
        work_times = [t for t in all_times if t != "00:30"]
        num_rows = len(work_times) // 2

        if not dates_found or num_rows == 0:
            return AttendanceReport(rows=(), **self._parse_summary(raw_text))

        anchor_date = datetime.strptime(dates_found[0], "%d/%m/%Y")
        lines = raw_text.split('\n')
        anchor_line_idx = 0
        for i, line in enumerate(lines):
            if dates_found[0] in line:
                anchor_line_idx = i
                break

        rows_before_anchor = 0
        for line in lines[:anchor_line_idx]:
            times_in_line = [t for t in re.findall(self.time_pattern, line) if t != "00:30"]
            if len(times_in_line) >= 2:
                rows_before_anchor += 1

        start_date = anchor_date - timedelta(days=rows_before_anchor)
        rows = []
        date_cursor = start_date

        for i in range(num_rows):
            idx = i * 2
            start_time = work_times[idx]
            end_time = work_times[idx + 1]
            day_name = DAYS_HE.get(date_cursor.strftime("%A"), date_cursor.strftime("%A"))

            rows.append(AttendanceRow(
                date=date_cursor.strftime("%d/%m/%Y"),
                day_of_week=day_name,
                start=start_time,
                end=end_time,
                break_minutes=30,
                is_shabbat=(date_cursor.weekday() == 5),
            ))
            date_cursor += timedelta(days=1)

        summary = self._parse_summary(raw_text)
        return AttendanceReport(rows=tuple(rows), **summary)
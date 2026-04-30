import re
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from parser_factory import BaseParser
from Entities.attendance import AttendanceRow, AttendanceReport

HEADER_KEYWORDS = ["שם העובד", "כרטיס עובד", "סה\"כ ימי", "סה\"כ שעות", "מחיר לשעה", "סה\"כ לתשלום", "שעת כניסה", "שעת יציאה", "הערות", "יום"]
HOLIDAY_KEYWORDS = ["ראש השנה", "יום כיפור", "סוכות", "פסח", "שבועות", "עצמאות", "חג"]

DAYS_HE = {
    "ראשון": "Sunday",
    "שני": "Monday",
    "שלישי": "Tuesday",
    "רביעי": "Wednesday",
    "חמישי": "Thursday",
    "שישי": "Friday",
    "שבת": "Saturday",
}

class ParserB(BaseParser):

    def _is_header_line(self, line: str) -> bool:
        return any(kw in line for kw in HEADER_KEYWORDS)

    def _parse_row(self, line: str) -> AttendanceRow | None:
        date_match = re.search(self.date_pattern, line)
        if not date_match:
            return None

        date_str = date_match.group(1)
        # Normalize date format
        try:
            from datetime import datetime
            d = datetime.strptime(date_str, "%d/%m/%Y")
        except ValueError:
            try:
                from datetime import datetime
                d = datetime.strptime(date_str, "%d/%m/%y")
            except ValueError:
                return None
        date_str = d.strftime("%d/%m/%Y")

        times = re.findall(self.time_pattern, line)

        day_of_week = ""
        for he, en in DAYS_HE.items():
            if he in line:
                day_of_week = en
                break

        is_shabbat = "שבת" in line
        is_holiday = any(kw in line for kw in HOLIDAY_KEYWORDS)
        notes = ""
        for kw in HOLIDAY_KEYWORDS:
            if kw in line:
                notes = kw
                break

        if is_shabbat or is_holiday or len(times) < 2:
            return AttendanceRow(
                date=date_str,
                day_of_week=day_of_week,
                start="",
                end="",
                is_shabbat=is_shabbat,
                is_holiday=is_holiday,
                notes=notes,
            )

        start_time = times[0]
        end_time = times[1]
        total = self._calc_hours(start_time, end_time)

        return AttendanceRow(
            date=date_str,
            day_of_week=day_of_week,
            start=start_time,
            end=end_time,
            total_hours=total,
            is_shabbat=is_shabbat,
            is_holiday=is_holiday,
            notes=notes,
        )

    def _parse_summary(self, raw_text: str) -> dict:
        employee_name = ""
        month = ""
        year = ""

        for line in raw_text.split('\n'):
            date_match = re.search(self.date_pattern, line)
            if date_match:
                from datetime import datetime
                date_str = date_match.group(1)
                # Handle both 2-digit and 4-digit year formats
                try:
                    d = datetime.strptime(date_str, "%d/%m/%Y")
                except ValueError:
                    try:
                        d = datetime.strptime(date_str, "%d/%m/%y")
                    except ValueError:
                        continue
                month = d.strftime("%m")
                year = d.strftime("%Y")
                break

        return {
            "employee_name": employee_name,
            "month": month,
            "year": year,
            "report_type": "N",
        }

    def _calc_hours(self, start: str, end: str) -> float:
        from datetime import datetime
        s = datetime.strptime(start, "%H:%M")
        e = datetime.strptime(end, "%H:%M")
        total_min = (e - s).seconds // 60
        return round(total_min / 60, 2)
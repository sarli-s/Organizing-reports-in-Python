from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from Entities.attendance import AttendanceRow, AttendanceReport
from strategies.strategy_base import BaseTransformationStrategy


class TypeNTransformationStrategy(BaseTransformationStrategy):
    """
    Produces a deterministic variation of a Type N attendance row.
    Entry and exit times are shifted by ±5 minutes based on the date.
    Shabbat and holiday rows are returned unchanged.
    """

    def transform_row(self, row: AttendanceRow) -> AttendanceRow:
        if row.is_shabbat or row.is_holiday or not row.start or not row.end:
            return row

        start, end = self._fix_order(row.start, row.end)
        offset = self._calc_offset(row.date)
        new_start = self._shift_time(start, offset)
        new_end = self._shift_time(end, offset)
        total = self._calc_hours(new_start, new_end)

        return AttendanceRow(
            date=row.date,
            day_of_week=row.day_of_week,
            start=new_start,
            end=new_end,
            total_hours=total,
            notes=row.notes,
            is_shabbat=row.is_shabbat,
            is_holiday=row.is_holiday,
        )

    def enrich_report(self, report: AttendanceReport) -> AttendanceReport:
        """
        Fills missing rows using the average daily hours from existing rows.
        Calculates hourly rate from total hours and a default monthly salary.
        """
        DEFAULT_MONTHLY_SALARY = 3000.0

        # Calculate average hours from rows that have data
        valid_rows = [r for r in report.rows if r.total_hours and r.total_hours > 0]
        avg_hours = (
            round(sum(r.total_hours for r in valid_rows) / len(valid_rows), 2)
            if valid_rows else 3.0
        )
        avg_start = self._most_common_start(valid_rows) or "08:00"

        enriched = []
        for row in report.rows:
            if row.is_shabbat or row.is_holiday:
                enriched.append(row)
                continue

            if not row.start or not row.end:
                # Fill missing row with average values
                new_end = self._shift_time(avg_start, int(avg_hours * 60))
                enriched.append(AttendanceRow(
                    date=row.date,
                    day_of_week=row.day_of_week,
                    start=avg_start,
                    end=new_end,
                    total_hours=avg_hours,
                    notes=row.notes,
                    is_shabbat=False,
                    is_holiday=False,
                ))
            else:
                enriched.append(row)

        total_hours = round(sum(r.total_hours for r in enriched if r.total_hours), 2)
        total_days = len([r for r in enriched if not r.is_shabbat and not r.is_holiday and r.total_hours])
        hourly_rate = round(DEFAULT_MONTHLY_SALARY / total_hours, 2) if total_hours else 0.0
        total_payment = round(hourly_rate * total_hours, 2)

        return AttendanceReport(
            employee_name=report.employee_name,
            month=report.month,
            year=report.year,
            report_type=report.report_type,
            rows=tuple(enriched),
            total_days=total_days,
            total_hours_100=total_hours,
            hourly_rate=hourly_rate,
            total_payment=total_payment,
        )

    def _most_common_start(self, rows: list) -> str | None:
        starts = [r.start for r in rows if r.start]
        return max(set(starts), key=starts.count) if starts else None

    def _fix_order(self, start: str, end: str) -> tuple[str, str]:
        s = datetime.strptime(start, "%H:%M")
        e = datetime.strptime(end, "%H:%M")
        if s > e:
            return end, start
        return start, end

    def _calc_offset(self, date_str: str) -> int:
        seed = int(date_str.replace("/", ""))
        return (seed % 11) - 5

    def _shift_time(self, time_str: str, minutes: int) -> str:
        t = datetime.strptime(time_str, "%H:%M")
        t += timedelta(minutes=minutes)
        return t.strftime("%H:%M")

    def _calc_hours(self, start: str, end: str) -> float:
        s = datetime.strptime(start, "%H:%M")
        e = datetime.strptime(end, "%H:%M")
        total_min = (e - s).seconds // 60
        return round(total_min / 60, 2)
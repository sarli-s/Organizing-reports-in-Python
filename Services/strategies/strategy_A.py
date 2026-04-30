from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from Entities.attendance import AttendanceRow, AttendanceReport
from strategies.strategy_base import BaseTransformationStrategy


class TypeATransformationStrategy(BaseTransformationStrategy):
    """
    Produces a deterministic variation of a Type A attendance row.
    Entry and exit times are shifted by ±5 minutes based on the date,
    while preserving a fixed work duration.
    """

    def transform_row(self, row: AttendanceRow) -> AttendanceRow:
        if row.is_shabbat or not row.start or not row.end:
            return row

        start, end = self._fix_order(row.start, row.end)
        offset = self._calc_offset(row.date)
        new_start = self._shift_time(start, offset)
        new_end = self._shift_time(end, offset)
        total = self._calc_hours(new_start, new_end, row.break_minutes or 30)

        return AttendanceRow(
            date=row.date,
            day_of_week=row.day_of_week,
            start=new_start,
            end=new_end,
            break_minutes=row.break_minutes,
            total_hours=total,
            hours_100=total,
            hours_125=row.hours_125,
            hours_150=row.hours_150,
            hours_shabbat=row.hours_shabbat,
            location=row.location,
            is_shabbat=row.is_shabbat,
            is_holiday=row.is_holiday,
        )

    def enrich_report(self, report: AttendanceReport) -> AttendanceReport:
        """
        Fills missing location and calculates 125%/150% overtime.
        Location: uses most common non-empty value across all rows.
        Overtime: hours beyond 8.0 on a regular day go to 125%.
        """
        # Find most common location
        locations = [r.location for r in report.rows if r.location and r.location.strip()]
        default_location = max(set(locations), key=locations.count) if locations else "גליליון"

        enriched = []
        total_100 = 0.0
        total_125 = 0.0
        total_150 = 0.0
        total_shabbat = 0.0

        for row in report.rows:
            if row.is_shabbat:
                shabbat_hours = row.total_hours or 0.0
                total_shabbat += shabbat_hours
                enriched.append(AttendanceRow(
                    date=row.date,
                    day_of_week=row.day_of_week,
                    start=row.start,
                    end=row.end,
                    break_minutes=row.break_minutes,
                    total_hours=shabbat_hours,
                    hours_100=0.0,
                    hours_125=0.0,
                    hours_150=0.0,
                    hours_shabbat=shabbat_hours,
                    location=row.location or default_location,
                    is_shabbat=True,
                ))
                continue

            total = row.total_hours or 0.0
            hours_100 = min(total, 8.0)
            hours_125 = max(0.0, min(total - 8.0, 2.0))
            hours_150 = max(0.0, total - 10.0)

            total_100 += hours_100
            total_125 += hours_125
            total_150 += hours_150

            enriched.append(AttendanceRow(
                date=row.date,
                day_of_week=row.day_of_week,
                start=row.start,
                end=row.end,
                break_minutes=row.break_minutes,
                total_hours=total,
                hours_100=round(hours_100, 2),
                hours_125=round(hours_125, 2),
                hours_150=round(hours_150, 2),
                hours_shabbat=0.0,
                location=row.location or default_location,
                is_shabbat=False,
                is_holiday=row.is_holiday,
            ))

        return AttendanceReport(
            employee_name=report.employee_name,
            month=report.month,
            year=report.year,
            report_type=report.report_type,
            rows=tuple(enriched),
            total_days=len([r for r in enriched if not r.is_shabbat and r.total_hours]),
            total_hours_100=round(total_100, 2),
            total_hours_125=round(total_125, 2),
            total_hours_150=round(total_150, 2),
            total_hours_shabbat=round(total_shabbat, 2),
        )

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

    def _calc_hours(self, start: str, end: str, break_min: int) -> float:
        s = datetime.strptime(start, "%H:%M")
        e = datetime.strptime(end, "%H:%M")
        total_min = (e - s).seconds // 60 - break_min
        return round(total_min / 60, 2)
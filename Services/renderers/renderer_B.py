import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from Entities.attendance import AttendanceReport, AttendanceRow
from renderers.renderer_base import BaseRenderer


class RendererN(BaseRenderer):
    """
    Renders a Type N attendance report as HTML and PDF.
    Mirrors the structure of the original monthly employee card format.
    """

    def _build_html(self, report: AttendanceReport) -> str:
        return f"""
<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            font-size: 12px;
            direction: rtl;
            margin: 20px;
        }}
        h2 {{
            text-align: right;
            font-size: 14px;
        }}
        .meta-table {{
            width: 300px;
            border-collapse: collapse;
            margin-bottom: 15px;
            margin-right: auto;
        }}
        .meta-table td {{
            border: 1px solid #000;
            padding: 4px 8px;
            text-align: right;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th {{
            background-color: #c0c0c0;
            border: 1px solid #000;
            padding: 4px 6px;
            text-align: center;
        }}
        td {{
            border: 1px solid #000;
            padding: 4px 6px;
            text-align: center;
        }}
        tr.shabbat, tr.holiday {{
            background-color: #d3d3d3;
        }}
    </style>
</head>
<body>
    <h2>כרטיס עובד לחודש</h2>
    {self._build_meta(report)}
    <table>
        <thead>
            <tr>
                <th>תאריך</th>
                <th>יום בשבוע</th>
                <th>שעת כניסה</th>
                <th>שעת יציאה</th>
                <th>סה"כ שעות</th>
                <th>הערות</th>
            </tr>
        </thead>
        <tbody>
            {self._build_rows(report)}
        </tbody>
    </table>
</body>
</html>
"""

    def _build_meta(self, report: AttendanceReport) -> str:
        total_hours = sum(r.total_hours for r in report.rows if r.total_hours)
        total_days = len([r for r in report.rows if not r.is_shabbat and not r.is_holiday and r.start])
        return f"""
        <table class="meta-table">
            <tr><td>סה"כ ימי עבודה לחודש</td><td>{total_days}</td></tr>
            <tr><td>סה"כ שעות חודשיות</td><td>{total_hours:.2f}</td></tr>
            <tr><td>מחיר לשעה</td><td>{report.hourly_rate or 0:.2f} ₪</td></tr>
            <tr><td>סה"כ לתשלום</td><td>{report.total_payment or 0:.2f} ₪</td></tr>
        </table>"""

    def _build_rows(self, report: AttendanceReport) -> str:
        html = ""
        for row in report.rows:
            if row.is_shabbat or row.is_holiday:
                css = "shabbat" if row.is_shabbat else "holiday"
                html += f"""
                <tr class="{css}">
                    <td>{row.date}</td>
                    <td>{row.day_of_week}</td>
                    <td></td><td></td><td></td>
                    <td>{row.notes or ""}</td>
                </tr>"""
            else:
                total = f"{row.total_hours:.2f}" if row.total_hours else ""
                html += f"""
                <tr>
                    <td>{row.date}</td>
                    <td>{row.day_of_week}</td>
                    <td>{row.start}</td>
                    <td>{row.end}</td>
                    <td>{total}</td>
                    <td>{row.notes or ""}</td>
                </tr>"""
        return html
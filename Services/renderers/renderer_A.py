import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from Entities.attendance import AttendanceReport, AttendanceRow
from Services.renderers.renderer_base import BaseRenderer


class RendererA(BaseRenderer):
    """
    Renders a Type A attendance report as HTML and PDF.
    Mirrors the structure of the original Nasher report format.
    """

    def _build_html(self, report: AttendanceReport) -> str:
        rows_html = self._build_rows(report)
        totals_html = self._build_totals(report)

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
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
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
        tr.shabbat {{
            background-color: #d3d3d3;
        }}
        tr.total {{
            background-color: #e8e8e8;
            font-weight: bold;
        }}
        .summary-table {{
            width: 250px;
            margin-top: 20px;
            margin-right: auto;
        }}
        .summary-table td {{
            padding: 3px 8px;
        }}
    </style>
</head>
<body>
    <h2>נ.ע. הנשר כח אדם בע"מ</h2>
    <table>
        <thead>
            <tr>
                <th>תאריך</th>
                <th>יום</th>
                <th>מקום</th>
                <th>כניסה</th>
                <th>יציאה</th>
                <th>הפסקה</th>
                <th>סה"כ</th>
                <th>100%</th>
                <th>125%</th>
                <th>150%</th>
                <th>שבת</th>
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
        <tfoot>
            {totals_html}
        </tfoot>
    </table>
    {self._build_summary(report)}
</body>
</html>
"""

    def _build_rows(self, report: AttendanceReport) -> str:
        html = ""
        for row in report.rows:
            if row.is_shabbat:
                html += f"""
                <tr class="shabbat">
                    <td>{row.date}</td>
                    <td>שבת</td>
                    <td></td><td></td><td></td><td></td>
                    <td></td><td></td><td></td><td></td>
                    <td>{row.hours_shabbat or ""}</td>
                </tr>"""
            else:
                total = f"{row.total_hours:.2f}" if row.total_hours else ""
                html += f"""
                <tr>
                    <td>{row.date}</td>
                    <td>{row.day_of_week}</td>
                    <td>{row.location or ""}</td>
                    <td>{row.start}</td>
                    <td>{row.end}</td>
                    <td>00:30</td>
                    <td>{total}</td>
                    <td>{row.hours_100 or total}</td>
                    <td>{row.hours_125 or "0.00"}</td>
                    <td>{row.hours_150 or "0.00"}</td>
                    <td>0.00</td>
                </tr>"""
        return html

    def _build_totals(self, report: AttendanceReport) -> str:
        total_hours = sum(r.total_hours for r in report.rows if r.total_hours)
        total_days = len([r for r in report.rows if not r.is_shabbat])
        return f"""
        <tr class="total">
            <td>{total_days}</td>
            <td></td><td></td><td></td><td></td><td></td>
            <td>{total_hours:.2f}</td>
            <td>{total_hours:.2f}</td>
            <td>0.00</td>
            <td>0.00</td>
            <td>{report.total_hours_shabbat or "0.00"}</td>
        </tr>"""

    def _build_summary(self, report: AttendanceReport) -> str:
        total_hours = sum(r.total_hours for r in report.rows if r.total_hours)
        total_days = len([r for r in report.rows if not r.is_shabbat])
        return f"""
        <table class="summary-table">
            <tr><td>ימים</td><td>{total_days}</td></tr>
            <tr><td>סה"כ שעות</td><td>{total_hours:.2f}</td></tr>
            <tr><td>שעות 100%</td><td>{total_hours:.2f}</td></tr>
            <tr><td>שעות 125%</td><td>0</td></tr>
            <tr><td>שעות 150%</td><td>0</td></tr>
            <tr><td>שבת 150%</td><td>{report.total_hours_shabbat or 0}</td></tr>
            <tr><td>בונוס</td><td>0</td></tr>
            <tr><td>נסיעות</td><td>0</td></tr>
        </table>"""
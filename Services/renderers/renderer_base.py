import sys
import os
from abc import ABC, abstractmethod

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from Entities.attendance import AttendanceReport


class BaseRenderer(ABC):
    """
    Base class for all renderers.
    Defines the template method: render() calls _build_html() and then converts to PDF.
    """

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def render(self, report: AttendanceReport) -> tuple[str, str]:
        """
        Template Method: builds HTML, saves it, then converts to PDF.
        Returns (html_path, pdf_path).
        """
        html_content = self._build_html(report)
        html_path = self._save_html(html_content, report)
        pdf_path = self._convert_to_pdf(html_path, report)
        return html_path, pdf_path

    @abstractmethod
    def _build_html(self, report: AttendanceReport) -> str:
        """Builds and returns the full HTML string for the report."""
        pass

    def _filename_base(self, report: AttendanceReport) -> str:
        return f"output_{report.report_type}_{report.month}_{report.year}"

    def _save_html(self, html_content: str, report: AttendanceReport) -> str:
        path = os.path.join(self.output_dir, f"{self._filename_base(report)}.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"[Renderer] HTML saved: {path}")
        return path

    def _convert_to_pdf(self, html_path: str, report: AttendanceReport) -> str:
        import pdfkit
        pdf_path = os.path.join(self.output_dir, f"{self._filename_base(report)}.pdf")
        config = pdfkit.configuration(
            wkhtmltopdf=r"C:\Program Files\לימוד שיטה עיורת\RapidTyping\wkhtmltopdf.exe"
        )
        pdfkit.from_file(html_path, pdf_path, configuration=config)
        print(f"[Renderer] PDF saved: {pdf_path}")
        return pdf_path
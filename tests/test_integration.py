"""
Integration tests — run the real pipeline (real Tesseract + Poppler OCR)
against the actual PDF samples in Repositories/.
Only pdfkit is mocked so wkhtmltopdf is not required to run these tests.
"""
import sys
import os
import pytest
from unittest.mock import patch, MagicMock

ROOT = os.path.join(os.path.dirname(__file__), '..')
SERVICES = os.path.join(ROOT, 'Services')
sys.path.insert(0, ROOT)
sys.path.insert(0, SERVICES)

REPOS = os.path.join(ROOT, 'Repositories')


# ── helpers ───────────────────────────────────────────────────────────────────

def _pdf(name: str) -> str:
    return os.path.join(REPOS, name)


def _run(pdf_path: str, tmp_path):
    """Runs steps 1-5 of the pipeline and returns (html_path, transformed_report)."""
    from transform import PDFToTextExtractor
    from clasification import DocumentClassifier
    from parser_A import ParserA
    from parser_B import ParserB
    from strategies.strategy_A import TypeATransformationStrategy
    from strategies.startegy_B import TypeNTransformationStrategy
    from strategies.strategy_decorator import ValidatingStrategyDecorator
    from transformation_service import TransformationService
    from renderers.renderer_A import RendererA
    from renderers.renderer_B import RendererN

    raw_text = PDFToTextExtractor().process_pdf(pdf_path)
    doc_type = DocumentClassifier().classify(raw_text)

    parser = ParserA() if doc_type == "A" else ParserB()
    report = parser.parse(raw_text)

    registry = {
        "A": ValidatingStrategyDecorator(TypeATransformationStrategy()),
        "N": ValidatingStrategyDecorator(TypeNTransformationStrategy()),
    }
    transformed = TransformationService(registry).transform(report)

    renderer = RendererA(str(tmp_path)) if doc_type == "A" else RendererN(str(tmp_path))
    with patch("pdfkit.configuration", return_value=MagicMock()), \
         patch("pdfkit.from_file"):
        html_path, _ = renderer.render(transformed)

    return html_path, transformed, doc_type


# ── 1. Type A PDF is classified and parsed correctly ─────────────────────────

def test_type_a_pipeline_classifies_and_parses(tmp_path):
    html_path, report, doc_type = _run(_pdf("a_r_9.pdf"), tmp_path)

    assert doc_type == "A"
    assert len(report.rows) > 0
    assert report.month != ""
    assert report.year != ""


# ── 2. Type N PDF is classified and parsed correctly ─────────────────────────

def test_type_n_pipeline_classifies_and_parses(tmp_path):
    html_path, report, doc_type = _run(_pdf("n_r_5_n.pdf"), tmp_path)

    assert doc_type == "N"
    assert len(report.rows) > 0
    assert report.month != ""
    assert report.year != ""


# ── 3. Transformed rows have valid time order ─────────────────────────────────

def test_transformed_rows_have_valid_times(tmp_path):
    from datetime import datetime
    _, report, _ = _run(_pdf("a_r_9.pdf"), tmp_path)

    for row in report.rows:
        if row.is_shabbat or row.is_holiday or not row.start or not row.end:
            continue
        start = datetime.strptime(row.start, "%H:%M")
        end = datetime.strptime(row.end, "%H:%M")
        assert end > start, f"Invalid times on {row.date}: {row.start} → {row.end}"


# ── 4. HTML output file is created and contains report data ──────────────────

def test_html_output_is_created_with_content(tmp_path):
    html_path, report, _ = _run(_pdf("a_r_9.pdf"), tmp_path)

    assert os.path.exists(html_path)
    content = open(html_path, encoding="utf-8").read()
    assert report.month in content
    assert report.year in content
    # At least one row date appears in the HTML
    assert any(row.date in content for row in report.rows)


# ── 5. Full pipeline runs on all 4 PDFs without crashing ─────────────────────

@pytest.mark.parametrize("pdf_name", [
    "a_r_9.pdf",
    "a_r_25.pdf",
    "n_r_5_n.pdf",
    "n_r_10_n.pdf",
])
def test_full_pipeline_all_pdfs(tmp_path, pdf_name):
    html_path, report, doc_type = _run(_pdf(pdf_name), tmp_path)

    assert doc_type in ("A", "N")
    assert len(report.rows) > 0
    assert os.path.exists(html_path)

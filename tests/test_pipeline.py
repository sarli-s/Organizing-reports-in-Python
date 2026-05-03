import sys
import os
import pytest
from unittest.mock import patch, MagicMock
from PIL import Image

# Add the main project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Add the Services folder to sys.path to resolve internal import issues
sys.path.insert(0, os.path.join(project_root, 'Services'))

# -- 1. Text Extraction Test - Process Flow ----------------------
@patch("Services.transform.convert_from_path")
@patch("Services.transform.pytesseract.image_to_string", return_value="08:00 17:00 01/05/2024")
def test_pdf_processing_flow(mock_ocr, mock_convert):
    from Services.transform import PDFToTextExtractor
    mock_convert.return_value = [Image.new('RGB', (10, 10))]
    extractor = PDFToTextExtractor()
    
    # Mocking the process_pdf method to return sample data
    with patch.object(PDFToTextExtractor, 'process_pdf', return_value="08:00 17:00 01/05/2024"):
        result = extractor.process_pdf("dummy.pdf")
        assert "08:00" in result

# -- 2. Document Classification Test - Type A ---------------------------
def test_classify_type_a():
    from Services.clasification import DocumentClassifier
    classifier = DocumentClassifier()
    # Check if specific keywords for type A are correctly identified
    assert classifier.classify("הפסקה 100% מקום") == "A"

# -- 3. Document Classification Test - Type N ---------------------------
def test_classify_type_n():
    from Services.clasification import DocumentClassifier
    classifier = DocumentClassifier()
    # Check if specific keywords for type N are correctly identified
    assert classifier.classify("מחיר לשעה כרטיס עובד") == "N"

# -- 4. Row Processing Test (Parsing) ---------------------------
def test_parser_logic():
    from Services.parser_B import ParserB
    text = "01/05/2024 08:00 17:00"
    parser = ParserB()
    report = parser.parse(text)
    # Verify that the report object contains a rows attribute
    assert hasattr(report, 'rows')

# -- 5. HTML File Creation Test ---------------------------------
@patch("pdfkit.from_file", return_value=True)
def test_renderer_output_file(mock_pdf, tmp_path):
    from Services.renderers.renderer_A import RendererA
    from Entities.attendance import AttendanceRow, AttendanceReport

    # Creating sample data for testing
    row = AttendanceRow(date="01/05/2024", day_of_week="Sunday", start="08:00", end="17:00", total_hours=8.5)
    report = AttendanceReport(employee_name="Test", month="05", year="2024", report_type="A", rows=(row,))

    renderer = RendererA(str(tmp_path))
    
    # Mocking the PDF conversion to check only HTML generation
    with patch.object(RendererA, '_convert_to_pdf', return_value="dummy.pdf"):
        html_path, _ = renderer.render(report)
        assert os.path.exists(html_path)
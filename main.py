import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
services_path = os.path.join(current_dir, "Services")
sys.path.insert(0, services_path)
sys.path.insert(0, current_dir)

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


def build_registry(output_dir: str) -> dict:
    return {
        "A": ValidatingStrategyDecorator(TypeATransformationStrategy()),
        "N": ValidatingStrategyDecorator(TypeNTransformationStrategy()),
    }


def run_pipeline(file_name: str):
    pdf_path = os.path.join(current_dir, "Repositories", file_name)
    if not os.path.exists(pdf_path):
        print(f"Error: file {file_name} not found in Repositories/")
        return

    output_dir = os.path.join(current_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    print(f"--- Starting pipeline for: {file_name} ---")

    # Step 1: OCR
    extractor = PDFToTextExtractor()
    raw_text = extractor.process_pdf(pdf_path)

    # Step 2: Classify
    classifier = DocumentClassifier()
    doc_type = classifier.classify(raw_text)
    print(f"Detected report type: {doc_type}")

    # Step 3: Parse
    parser = ParserA() if doc_type == "A" else ParserB()
    report = parser.parse(raw_text)
    print(f"Parsed {len(report.rows)} rows")

    # Step 4: Transform
    registry = build_registry(output_dir)
    service = TransformationService(strategy_registry=registry)
    transformed_report = service.transform(report)
    print(f"Transformed {len(transformed_report.rows)} rows")

    # Step 5: Render
    renderer = RendererA(output_dir) if doc_type == "A" else RendererN(output_dir)
    html_path, pdf_path_out = renderer.render(transformed_report)

    print(f"--- Done ---")
    print(f"HTML: {html_path}")
    print(f"PDF:  {pdf_path_out}")


if __name__ == "__main__":
    for f in ["a_r_9.pdf", "a_r_25.pdf", "n_r_5_n.pdf", "n_r_10_n.pdf"]:
        run_pipeline(f)
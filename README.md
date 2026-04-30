# Attendance Report Processor

A Python CLI tool that reads employee attendance PDF reports, applies deterministic
transformations to produce a realistic variation, and outputs new HTML and PDF files
that mirror the original format.

## Supported Report Types

- **Type A** – Nasher HR format (נ.ע. הנשר כח אדם בע"מ)
- **Type N** – Monthly employee card format (כרטיס עובד לחודש)

## Architecture

The pipeline follows a clean layered architecture using several design patterns:

```
PDF file
│
▼ PDFToTextExtractor      — OCR via Tesseract (image preprocessing with OpenCV)
│
▼ DocumentClassifier      — Keyword scoring → "A" or "N"
│
▼ ParserFactory           — Template Method pattern
  ParserA / ParserB       — Build AttendanceReport domain objects
│
▼ TransformationService   — Strategy pattern with registry
  ValidatingStrategyDecorator  — Decorator pattern: validates every transformed row
  TypeAStrategy / TypeNStrategy — Deterministic time shifts (±5 min based on date)
│
▼ RendererA / RendererN   — Template Method pattern: HTML → PDF output
```

## Design Patterns Used

- **Template Method** – `BaseParser.parse()` defines the algorithm skeleton;
  subclasses override `_parse_row`, `_is_header_line`, `_parse_summary`.
  Same pattern used in `BaseRenderer.render()`.

- **Strategy** – `TransformationService` holds a registry mapping report type
  to a strategy object. Adding a new report type requires only one new class
  and one registry entry — nothing else changes.

- **Decorator** – `ValidatingStrategyDecorator` wraps any strategy and validates
  its output. If validation fails, the service falls back to the original row.
  The service cannot distinguish a raw strategy from a decorated one.

- **Shared Domain Model** – `AttendanceRow` is a single dataclass shared by both
  report types. Type-specific fields use `Optional` with `None` defaults.

## Project Structure

```
03/
├── Entities/
│   └── attendance.py              # AttendanceRow, AttendanceReport dataclasses
├── Repositories/                  # Input PDF samples
├── Services/
│   ├── transform.py               # OCR extraction
│   ├── clasification.py           # Document classifier
│   ├── parser_factory.py          # BaseParser (Template Method)
│   ├── parser_A.py                # Type A parser
│   ├── parser_B.py                # Type B/N parser
│   ├── transformation_service.py  # TransformationService
│   ├── strategies/
│   │   ├── strategy_base.py       # BaseTransformationStrategy interface
│   │   ├── strategy_A.py          # Type A transformation + enrichment
│   │   ├── strategy_N.py          # Type N transformation + enrichment
│   │   └── strategy_decorator.py  # ValidatingStrategyDecorator
│   └── renderers/
│       ├── renderer_base.py       # BaseRenderer (Template Method)
│       ├── renderer_A.py          # Type A HTML/PDF renderer
│       └── renderer_N.py          # Type N HTML/PDF renderer
├── output/                        # Generated files
├── main.py                        # CLI entry point
├── requirements.txt               # Project dependencies
├── Dockerfile                     # Docker container configuration
└── README.md                      # Project documentation
```

## Running Locally

### Prerequisites

- Python 3.11+
- Tesseract OCR with Hebrew language pack
- Poppler
- wkhtmltopdf

### Installation

```bash
pip install -r requirements.txt
```

### Usage

```bash
python main.py <path_to_pdf> -o <output_directory>
```

#### Examples

```bash
python main.py Repositories/a_r_9.pdf -o output/
python main.py Repositories/n_r_5_n.pdf -o output/
```

## Running with Docker

### Build

```bash
docker build -t attendance-report .
```

### Run

```bash
docker run --rm -v $(pwd)/samples:/data attendance-report /data/sample.pdf -o /data/
```

The output HTML and PDF files will appear in the mounted directory.

## Transformation Logic

### Type A
- Entry and exit times shifted by ±5 minutes deterministically based on the date
- Overtime calculated: hours beyond 8.0 → 125%, beyond 10.0 → 150%
- Missing location filled with the most common location in the report

### Type N
- Entry and exit times shifted by ±5 minutes deterministically based on the date
- Missing rows filled with the report's average daily hours
- Hourly rate and total payment calculated from total monthly hours

## Output

Each input PDF produces two output files:

- `output_<type>_<month>_<year>.html`
- `output_<type>_<month>_<year>.pdf`

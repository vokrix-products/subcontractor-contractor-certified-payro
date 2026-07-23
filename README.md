# WH-347 Certified Payroll Auto-Compiler & Submission Prep Tool

This backend pipeline automates the conversion of subcontractor and contractor CSV timesheets into pre‑filled WH‑347 certified payroll reports. It is designed for construction payroll compliance under Davis‑Bacon and related prevailing wage regulations.

## Archetype

- **Purpose**: Reduce manual data entry and validation for multi‑employee weekly payroll submissions.
- **Input**: CSV timesheets placed in the `./input` directory.
- **Output**: WH‑347 PDF reports in `./output/pdfs` and structured JSON records in `./output/records`.
- **Statuses**:
  - `ready_for_submission:good` — all data valid and prevailing wage compliant.
  - `needs_review:warning` — missing county or rates below prevailing wage thresholds.
  - `error:critical` — missing required fields or invalid numeric values.

## Input Format

Each CSV file should contain one row per employee with the following columns (names are case‑insensitive and flexible; the system maps them automatically):

| Column              | Description                                      |
|---------------------|--------------------------------------------------|
| Employee Name       | Full name of the worker                          |
| SSN                 | Social Security Number                           |
| Classification      | Trade classification (e.g. Carpenter)            |
| Hours               | Total hours worked that week                     |
| Rate                | Base hourly wage                                 |
| Fringe Rate         | Hourly fringe benefit contribution               |
| Project             | Project or job name                              |
| Week Ending         | Date of the week ending (e.g. 2025-06-01)       |
| County              | Work location county (optional, enables prevailing wage check) |

## Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Place CSV files in ./input, then run:
python3 poller.py

# Run the demo:
python3 run_demo.py

# Run tests:
python3 run_tests.py
```

## Architecture

- `poller.py` — watches `./input`, processes new CSVs, orchestrates the pipeline.
- `csv_mapper.py` — maps raw CSV headers to standardized fields (fallback header‑matching or AI extractor).
- `prevailing_wage_lookup.py` — provides hardcoded demo prevailing wage dataset per county/classification.
- `fringe_benefit_calculator.py` — computes fringe dollar amount.
- `wh347_pdf_generator.py` — generates WH‑347 PDF using ReportLab.
- `run_demo.py` — end‑to‑end example.
- `run_tests.py` — unit tests.

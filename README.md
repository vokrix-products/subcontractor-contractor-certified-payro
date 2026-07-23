# WH-347 Auto-Compiler & Submission Prep Tool

## 🏗️ Archetype: Document Automation Pipeline

This product is a **back‑end document automation pipeline** that converts raw CSV timesheets into pre‑filled WH‑347 certified payroll reports, ready for submission under the Davis‑Bacon and related Acts.

---

## How It Works

1. **Drop CSV timesheets** into `./input/`.
2. **Run `python3 poller.py`** — the poller watches for new `.csv` files, processes each one, and generates:
   - A WH‑347 PDF report in `./output/pdfs/`
   - A record JSON with status and employee data in `./output/records/`
3. **Check status per file:**
   - `ready_for_submission:good` — all checks pass
   - `needs_review:warning` — minor issues (e.g., rate below prevailing, unclassified worker)
   - `error:critical` — missing required data

---

## Input CSV Format

The poller expects a CSV with the following columns (names are flexible — the system maps headers automatically):

| Standard Field | Common Header Examples |
|---------------|------------------------|
| `employee_name` | Employee Name, Name, Worker |
| `ssn` | SSN, Social Security Number |
| `classification` | Classification, Job Class |
| `county` | County, Location |
| `hours_worked` | Hours, Total Hours |
| `base_rate` | Rate, Hourly Rate |
| `fringe_rate` | Fringe Rate |
| `project` | Project, Job Name |
| `week_end_date` | Week Ending, End Date |

**Example row:**

```csv
Employee Name,SSN,Classification,Hours,Rate,Fringe Rate,Project,Week Ending
John Doe,123-45-6789,Carpenter,40,45.00,10.00,Highway Bridge,2025-06-01
```

---

## Prevailing Wage Lookup

For demo purposes, rates are hardcoded for **Cook County** and **DuPage County** (carpenter, electrician, laborer).  
If no matching rate is found, the system uses the submitted rates and flags a warning.

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the demo (creates sample CSV, processes it, prints PDF path)
python3 run_demo.py

# Run tests
python3 run_tests.py

# Process your own CSV files (place them in ./input first)
python3 poller.py
```

---

## Output

- **PDF reports** in `./output/pdfs/` — formatted like WH‑347 with project info, employee rows, and totals.
- **Record JSON files** in `./output/records/` — each contains the full processing result, status, warnings, and errors.

---

## Testing

`python3 run_tests.py` runs unit tests against:
- CSV column mapping (fallback header matching)
- Prevailing wage lookup
- Fringe benefit calculation
- Full processing pipeline (happy path & edge cases)

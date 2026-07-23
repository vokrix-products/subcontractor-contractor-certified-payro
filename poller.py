import os
import json
import csv
import datetime
from csv_mapper import map_columns, EXTRACTION_PROMPT
from prevailing_wage_lookup import get_prevailing_wage
from fringe_benefit_calculator import calculate_fringe
from wh347_pdf_generator import generate_wh347_pdf

INPUT_DIR = "./input"
OUTPUT_DIR = "./output"
RECORDS_DIR = os.path.join(OUTPUT_DIR, "records")
PDF_DIR = os.path.join(OUTPUT_DIR, "pdfs")

REQUIRED_FIELDS = ["employee_name", "classification", "hours_worked",
                   "base_rate", "fringe_rate", "project", "week_end_date"]
# county is optional – if missing, prevailing wage lookup is skipped

STATUS_READY = "ready_for_submission:good"
STATUS_WARNING = "needs_review:warning"
STATUS_ERROR = "error:critical"

def ensure_dirs():
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(RECORDS_DIR, exist_ok=True)
    os.makedirs(PDF_DIR, exist_ok=True)

def process_csv(filepath, extractor=None):
    """
    Reads a CSV timesheet, maps columns, validates data, computes wages,
    generates WH-347 PDF, and writes a record JSON with status.
    """
    with open(filepath, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        headers = reader.fieldnames if reader.fieldnames else []

    # Map columns
    mapped_rows, warnings = map_columns(headers, rows, extractor=extractor)

    # Validate required fields and gather per‑employee data
    employees = []
    status = STATUS_READY
    critical_errors = []
    warning_events = list(warnings)  # start with mapping warnings

    for i, row in enumerate(mapped_rows):
        missing = [f for f in REQUIRED_FIELDS if f not in row or not row[f].strip()]
        if missing:
            critical_errors.append(f"Row {i+1}: missing fields {missing}")
            continue

        # Convert numeric values
        try:
            hours = float(row["hours_worked"])
            base_rate = float(row["base_rate"])
            fringe_rate = float(row["fringe_rate"])
        except ValueError as e:
            critical_errors.append(f"Row {i+1}: invalid numeric value - {e}")
            continue

        county = row.get("county", "").strip()
        classification = row["classification"].strip()
        underpaid = False
        prevailing_base = base_rate
        prevailing_fringe = fringe_rate

        if county:
            prevailing = get_prevailing_wage(county, classification)
            if prevailing is None:
                warning_events.append(f"Row {i+1}: No prevailing wage data for {classification} in {county}")
            else:
                prevailing_base = prevailing["base_rate"]
                prevailing_fringe = prevailing["fringe_rate"]
                if base_rate < prevailing_base:
                    warning_events.append(
                        f"Row {i+1}: Base rate ${base_rate:.2f} below prevailing ${prevailing_base:.2f}"
                    )
                    underpaid = True
                if fringe_rate < prevailing_fringe:
                    warning_events.append(
                        f"Row {i+1}: Fringe rate ${fringe_rate:.2f} below prevailing ${prevailing_fringe:.2f}"
                    )
                    underpaid = True
        else:
            warning_events.append(f"Row {i+1}: No county specified, prevailing wage check skipped")

        fringe_amount = calculate_fringe(hours, fringe_rate)

        employee = {
            "employee_name": row["employee_name"],
            "ssn": row.get("ssn", ""),
            "classification": classification,
            "county": county,
            "hours_worked": hours,
            "base_rate": base_rate,
            "fringe_rate": fringe_rate,
            "fringe_amount": fringe_amount,
            "total_pay": hours * base_rate + fringe_amount,
            "project": row["project"],
            "week_end_date": row["week_end_date"],
            "under_prevailing": underpaid,
        }
        employees.append(employee)

    if critical_errors:
        status = STATUS_ERROR
    elif warning_events:
        status = STATUS_WARNING

    # Use first employee's name as the title (or concatenate if multiple)
    title = employees[0]["employee_name"] if employees else "unknown"
    if len(employees) > 1:
        title += " et al."

    # Generate unique record ID
    base_name = os.path.splitext(os.path.basename(filepath))[0]
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d%H%M%S%f")
    record_id = f"{base_name}_{stamp}"

    # Build record JSON
    record = {
        "id": record_id,
        "title": title,
        "status": status,
        "original_file": filepath,
        "employees": employees,
        "warnings": warning_events,
        "critical_errors": critical_errors,
        "pdf_path": os.path.join(PDF_DIR, f"{record_id}.pdf"),
    }

    # Generate PDF (even if errors, to show what could be produced)
    generate_wh347_pdf(record, record["pdf_path"])

    # Write record JSON
    record_path = os.path.join(RECORDS_DIR, f"{record_id}.json")
    with open(record_path, 'w') as f:
        json.dump(record, f, indent=2)

    return record

def poll_once():
    """
    Single-pass directory check for new CSV files.
    In a production service this would run in a loop.
    """
    ensure_dirs()
    for fname in os.listdir(INPUT_DIR):
        if fname.lower().endswith('.csv'):
            fpath = os.path.join(INPUT_DIR, fname)
            process_csv(fpath)

if __name__ == "__main__":
    poll_once()

import csv
import io
import re

# The extraction prompt explicitly states the title is the employee name.
EXTRACTION_PROMPT = """
You are an expert in payroll document processing.

Given a CSV header row, identify which column corresponds to each of the following fields.
The title (primary entity tracked by the buyer) is the full name of the EMPLOYEE.
Return a JSON object with keys: employee_name, ssn, classification, county, hours_worked,
base_rate, fringe_rate, project, week_end_date, and the values must be the exact column names
from the CSV header (case‑sensitive). If a field is not present, set its value to null.

CSV header: {header}

Return ONLY the JSON object, no extra text.
"""


def fallback_map(headers, rows):
    """
    Simple header matching based on common column names.
    Returns (mapped_rows, warnings)
    """
    # Normalize header names to lower case with underscores
    norm_to_orig = {h.lower().replace(' ', '_').replace('-', '_'): h for h in headers}

    field_map = {
        'employee_name': ['employee_name', 'name', 'worker', 'employee'],
        'ssn': ['ssn', 'social_security_number', 'social_security'],
        'classification': ['classification', 'job_class', 'class'],
        'county': ['county', 'location'],
        'hours_worked': ['hours_worked', 'hours', 'total_hours'],
        'base_rate': ['base_rate', 'rate', 'hourly_rate'],
        'fringe_rate': ['fringe_rate', 'fringe'],
        'project': ['project', 'job_name', 'project_name'],
        'week_end_date': ['week_end_date', 'week_ending', 'end_date'],
    }

    mapping = {}
    warnings = []
    for field, candidates in field_map.items():
        found = None
        for c in candidates:
            if c in norm_to_orig:
                found = norm_to_orig[c]
                break
        if found:
            mapping[field] = found
        else:
            mapping[field] = None
            warnings.append(f"Could not map field '{field}' from headers {headers}")

    # Map each row
    mapped_rows = []
    for original_row in rows:
        new_row = {}
        for field, col in mapping.items():
            new_row[field] = original_row.get(col, '') if col else ''
        mapped_rows.append(new_row)

    return mapped_rows, warnings


def map_columns(headers, rows, extractor=None):
    """
    Map columns using the provided extractor function (e.g., DeepSeek) or fallback.
    The extractor receives the CSV header string and returns a JSON string with field->column mapping.
    Returns (mapped_rows, warnings)
    """
    if extractor is None:
        # Use fallback without AI
        return fallback_map(headers, rows)

    # Call AI extractor
    header_str = ",".join(headers) if headers else ""
    prompt = EXTRACTION_PROMPT.format(header=header_str)
    try:
        mapping_json = extractor(prompt)  # Should return a JSON string
        import json
        mapping = json.loads(mapping_json)
    except Exception as e:
        # Fallback if AI fails
        print(f"Extractor error: {e}, using fallback")
        return fallback_map(headers, rows)

    # Map rows based on AI mapping
    mapped_rows = []
    warnings = []
    for i, original_row in enumerate(rows):
        new_row = {}
        for field, col in mapping.items():
            if col and col in original_row:
                new_row[field] = original_row[col]
            else:
                new_row[field] = ''
                if col:  # column specified but not present in row
                    warnings.append(f"Row {i+1}: mapped column '{col}' not found in data")
        mapped_rows.append(new_row)

    return mapped_rows, warnings

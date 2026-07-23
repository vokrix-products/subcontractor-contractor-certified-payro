import os
import tempfile
import shutil
from poller import process_csv, ensure_dirs

# Hardcoded test data: two employees with valid data, one with rate below prevailing
TEST_CSV = """Employee Name,SSN,Classification,Hours,Rate,Fringe Rate,Project,Week Ending,County
John Doe,123-45-6789,Carpenter,40,35.00,10.00,Highway Bridge,2025-06-01,Cook County
Jane Smith,987-65-4321,Electrician,38,45.00,12.00,Substation,2025-06-01,DuPage County
"""

def main():
    # Create input dir and test CSV
    tmpdir = tempfile.mkdtemp()
    original_input = os.path.join(tmpdir, "input")
    os.makedirs(original_input, exist_ok=True)
    csv_path = os.path.join(original_input, "test_timesheet.csv")
    with open(csv_path, 'w', newline='') as f:
        f.write(TEST_CSV)

    # Override dirs to use temp location for this demo
    import poller
    poller.INPUT_DIR = original_input
    poller.OUTPUT_DIR = os.path.join(tmpdir, "output")
    poller.RECORDS_DIR = os.path.join(poller.OUTPUT_DIR, "records")
    poller.PDF_DIR = os.path.join(poller.OUTPUT_DIR, "pdfs")
    poller.ensure_dirs()

    # Process the CSV (with fallback mapper, no AI)
    record = process_csv(csv_path, extractor=None)

    print("Demo complete. Record status:", record["status"])
    print("Title (employee name):", record["title"])
    print("PDF saved to:", record["pdf_path"])
    shutil.rmtree(tmpdir)  # cleanup

if __name__ == "__main__":
    main()

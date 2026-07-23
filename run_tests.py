import unittest
import os
import json
import tempfile
import shutil
import csv
from csv_mapper import fallback_map, map_columns
from prevailing_wage_lookup import get_prevailing_wage
from fringe_benefit_calculator import calculate_fringe
from poller import process_csv, ensure_dirs, REQUIRED_FIELDS, STATUS_READY, STATUS_WARNING, STATUS_ERROR

class TestModules(unittest.TestCase):
    def test_prevailing_wage_found(self):
        rate = get_prevailing_wage("Cook County", "Carpenter")
        self.assertIsNotNone(rate)
        self.assertEqual(rate["base_rate"], 42.00)
        self.assertEqual(rate["fringe_rate"], 9.50)

    def test_prevailing_wage_not_found(self):
        rate = get_prevailing_wage("Nowhere", "Carpenter")
        self.assertIsNone(rate)

    def test_fringe_calculation(self):
        self.assertEqual(calculate_fringe(40, 10.0), 400.00)
        self.assertEqual(calculate_fringe(38.5, 12.75), 490.88)  # 38.5*12.75=490.875 rounded 490.88

    def test_fallback_mapper(self):
        headers = ["Employee Name", "SSN", "Classification", "Hours", "Rate", "Fringe Rate", "Project", "Week Ending", "County"]
        rows = [{"Employee Name": "John", "SSN": "123", "Classification": "Carp", "Hours": "40",
                 "Rate": "30", "Fringe Rate": "5", "Project": "Bridge", "Week Ending": "2025-06-01", "County": "Cook"}]
        mapped, warnings = fallback_map(headers, rows)
        self.assertEqual(len(mapped), 1)
        m = mapped[0]
        self.assertEqual(m["employee_name"], "John")
        self.assertEqual(m["hours_worked"], "40")
        self.assertEqual(m["week_end_date"], "2025-06-01")
        self.assertEqual(m["county"], "Cook")

    def test_map_columns_fallback_integration(self):
        headers = ["Employee Name", "Hours"]
        rows = [{"Employee Name": "Alice", "Hours": "35"}]
        mapped, warnings = map_columns(headers, rows, extractor=None)
        self.assertEqual(len(mapped), 1)
        self.assertEqual(mapped[0]["employee_name"], "Alice")

    def test_process_csv_happy_path(self):
        # CSV with all required fields + a real county to test prevailing wage
        csv_content = (
            "Employee Name,SSN,Classification,Hours,Rate,Fringe Rate,Project,Week Ending,County\n"
            "John Doe,123-45-6789,Carpenter,40,45.00,10.00,Highway Bridge,2025-06-01,Cook County\n"
        )
        tmpdir = tempfile.mkdtemp()
        csv_path = os.path.join(tmpdir, "happy.csv")
        with open(csv_path, 'w', newline='') as f:
            f.write(csv_content)
        try:
            import poller
            poller.INPUT_DIR = tmpdir
            poller.OUTPUT_DIR = os.path.join(tmpdir, "output")
            poller.RECORDS_DIR = os.path.join(poller.OUTPUT_DIR, "records")
            poller.PDF_DIR = os.path.join(poller.OUTPUT_DIR, "pdfs")
            poller.ensure_dirs()
            record = process_csv(csv_path, extractor=None)
            self.assertEqual(record["status"], STATUS_READY)
            self.assertEqual(record["title"], "John Doe")
            self.assertTrue(os.path.exists(record["pdf_path"]))
            # Verify record JSON exists
            record_json = os.path.join(poller.RECORDS_DIR, f"{record['id']}.json")
            self.assertTrue(os.path.exists(record_json))
            with open(record_json) as f:
                saved = json.load(f)
            self.assertEqual(saved["status"], STATUS_READY)
        finally:
            shutil.rmtree(tmpdir)

    def test_process_csv_with_missing_field(self):
        # Missing Week Ending (empty) -> critical error
        csv_content = (
            "Employee Name,SSN,Classification,Hours,Rate,Fringe Rate,Project,Week Ending\n"
            "Jane Smith,987-65-4321,Electrician,38,50.00,12.00,Substation,\n"
        )
        tmpdir = tempfile.mkdtemp()
        csv_path = os.path.join(tmpdir, "warn.csv")
        with open(csv_path, 'w', newline='') as f:
            f.write(csv_content)
        try:
            import poller
            poller.INPUT_DIR = tmpdir
            poller.OUTPUT_DIR = os.path.join(tmpdir, "output")
            poller.RECORDS_DIR = os.path.join(poller.OUTPUT_DIR, "records")
            poller.PDF_DIR = os.path.join(poller.OUTPUT_DIR, "pdfs")
            poller.ensure_dirs()
            record = process_csv(csv_path, extractor=None)
            # Required field week_end_date missing -> critical error -> STATUS_ERROR
            self.assertEqual(record["status"], STATUS_ERROR)
            # No employees passed validation -> title should be "unknown"
            self.assertEqual(record["title"], "unknown")
        finally:
            shutil.rmtree(tmpdir)

if __name__ == "__main__":
    unittest.main()

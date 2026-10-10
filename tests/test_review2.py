"""
Unit Test Suite for Review 1 & 2 - Q07 Data Accuracy & CRUD Operations
BBAT104: Fundamentals of Total Quality Management (Session 2026-27)
Student: Anmol Joshi (Roll No: 2410302004, Branch: CSE-B)
"""

import unittest
import os
import sys
from datetime import date, timedelta

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import init_db, seed_db, get_connection
from src.models import MedicineRepository, SupplierRepository, AuditRepository, SalesRepository
from src.validation import DataValidator, ValidationError


class TestReview2PokaYokeValidation(unittest.TestCase):
    """Verifies Q07 Poka-Yoke validation rules and mistake-proofing controls."""

    def test_valid_future_expiry_date(self):
        future_date = (date.today() + timedelta(days=180)).strftime("%Y-%m-%d")
        result = DataValidator.validate_expiry_date(future_date)
        self.assertEqual(result, future_date)

    def test_reject_expired_date(self):
        past_date = (date.today() - timedelta(days=30)).strftime("%Y-%m-%d")
        with self.assertRaises(ValidationError) as ctx:
            DataValidator.validate_expiry_date(past_date, require_future=True)
        self.assertEqual(ctx.exception.defect_code, "DEF-02")

    def test_valid_batch_number(self):
        valid_batch = "BATCH-2026A"
        result = DataValidator.validate_batch_number(valid_batch)
        self.assertEqual(result, valid_batch)

    def test_reject_invalid_batch_syntax(self):
        with self.assertRaises(ValidationError) as ctx:
            DataValidator.validate_batch_number("LOT-99887")
        self.assertEqual(ctx.exception.defect_code, "DEF-03")

    def test_price_margin_enforcement(self):
        cost, sale = DataValidator.validate_prices("100.00", "150.00")
        self.assertEqual(cost, 100.0)
        self.assertEqual(sale, 150.0)

    def test_reject_inverted_price_margin(self):
        with self.assertRaises(ValidationError) as ctx:
            DataValidator.validate_prices("200.00", "150.00")
        self.assertEqual(ctx.exception.defect_code, "DEF-05")

    def test_dropdown_enum_validation(self):
        result = DataValidator.validate_enum("Tablet", DataValidator.VALID_DOSAGE_FORMS, "Dosage Form")
        self.assertEqual(result, "Tablet")

        with self.assertRaises(ValidationError) as ctx:
            DataValidator.validate_enum("InvalidPill", DataValidator.VALID_DOSAGE_FORMS, "Dosage Form")
        self.assertEqual(ctx.exception.defect_code, "DEF-07")

    def test_phone_number_masking_and_validation(self):
        masked_phone = DataValidator.validate_phone("(987) 654-3210")
        self.assertEqual(masked_phone, "(987) 654-3210")

        digits_phone = DataValidator.validate_phone("9876543210")
        self.assertEqual(digits_phone, "(987) 654-3210")


class TestReview2DatabaseAndCRUD(unittest.TestCase):
    """Verifies SQLite database operations, CRUD functions, and audit logging."""

    @classmethod
    def setUpClass(cls):
        init_db()
        seed_db()

    def test_database_connection_and_wal_mode(self):
        conn = get_connection()
        journal_mode = conn.execute("PRAGMA journal_mode;").fetchone()[0]
        fk_status = conn.execute("PRAGMA foreign_keys;").fetchone()[0]
        conn.close()
        self.assertEqual(journal_mode.lower(), "wal")
        self.assertEqual(fk_status, 1)

    def test_medicine_repository_get_all_default_id_asc(self):
        meds = MedicineRepository.get_all()
        self.assertGreater(len(meds), 0)
        # Verify default ID ascending order
        ids = [m["id"] for m in meds]
        self.assertEqual(ids, sorted(ids))

    def test_medicine_autocomplete_search(self):
        results = MedicineRepository.search_autocomplete("Augmentin")
        self.assertGreater(len(results), 0)
        self.assertTrue(any("Augmentin" in r["name"] for r in results))

    def test_audit_logging_integrity(self):
        logs = AuditRepository.get_all(limit=10)
        self.assertIsInstance(logs, list)
        if logs:
            first = logs[0]
            self.assertIn("action_type", first)
            self.assertIn("table_name", first)
            self.assertIn("timestamp", first)


if __name__ == "__main__":
    unittest.main()

"""
Unit Test Suite for Review 1 & 2 - Q07 Data Accuracy & CRUD Operations
BBAT104: Fundamentals of Total Quality Management (Session 2026-27)
Student: Anmol Joshi (Roll No: 2410302004, Branch: CSE-B)
Comprehensive coverage for:
1. Role-based access control
2. Strict Indian phone number validation
3. Differential GST tax rates (0-18%)
4. Manual discount calculation (% and flat Rs.)
5. Automatic customer registration upon sale
6. Supplier deal comparison and procurement ranking
7. Barcode and batch lookup
"""

import unittest
import os
import sys
import re
from datetime import date, timedelta

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import init_db, seed_db, get_connection
from src.models import (
    MedicineRepository, SupplierRepository, AuditRepository,
    SalesRepository, CustomerRepository, SupplierDealRepository
)
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

    def test_strict_phone_number_validation(self):
        # Valid 10-digit Indian numbers starting with 6,7,8,9
        self.assertEqual(DataValidator.validate_phone("9876543210"), "(987) 654-3210")
        self.assertEqual(DataValidator.validate_phone("(876) 543-2109"), "(876) 543-2109")
        self.assertEqual(DataValidator.validate_phone("7001234567"), "(700) 123-4567")

        # Reject dummy repeating numbers
        with self.assertRaises(ValidationError) as ctx:
            DataValidator.validate_phone("1111111111")
        self.assertEqual(ctx.exception.defect_code, "DEF-04")

        with self.assertRaises(ValidationError) as ctx:
            DataValidator.validate_phone("9999999999")
        self.assertEqual(ctx.exception.defect_code, "DEF-04")

        # Reject invalid prefix (e.g. starting with 1, 2, 3, 4, 5)
        with self.assertRaises(ValidationError) as ctx:
            DataValidator.validate_phone("1234567890")
        self.assertEqual(ctx.exception.defect_code, "DEF-04")

        # Reject length mismatch
        with self.assertRaises(ValidationError) as ctx:
            DataValidator.validate_phone("987654321")
        self.assertEqual(ctx.exception.defect_code, "DEF-04")

    def test_gst_tax_rate_validation(self):
        self.assertEqual(DataValidator.validate_tax_rate("0"), 0.0)
        self.assertEqual(DataValidator.validate_tax_rate("5%"), 5.0)
        self.assertEqual(DataValidator.validate_tax_rate(12), 12.0)
        self.assertEqual(DataValidator.validate_tax_rate("18%"), 18.0)

        with self.assertRaises(ValidationError) as ctx:
            DataValidator.validate_tax_rate("7%")
        self.assertEqual(ctx.exception.defect_code, "DEF-08")

    def test_manual_discount_validation(self):
        # Percentage discount
        self.assertEqual(DataValidator.validate_discount("10%", 500.0), 50.0)
        self.assertEqual(DataValidator.validate_discount("20", 500.0), 20.0)

        # Flat Rs. discount with currency prefix
        self.assertEqual(DataValidator.validate_discount("Rs. 75", 500.0), 75.0)
        self.assertEqual(DataValidator.validate_discount("₹ 50", 500.0), 50.0)

        # Zero or empty
        self.assertEqual(DataValidator.validate_discount("", 500.0), 0.0)
        self.assertEqual(DataValidator.validate_discount("0", 500.0), 0.0)

        # Reject discount exceeding gross subtotal
        with self.assertRaises(ValidationError) as ctx:
            DataValidator.validate_discount("600", 500.0)
        self.assertEqual(ctx.exception.defect_code, "DEF-09")

        # Reject negative discount
        with self.assertRaises(ValidationError) as ctx:
            DataValidator.validate_discount("-10", 500.0)
        self.assertEqual(ctx.exception.defect_code, "DEF-09")

    def test_role_based_access_control(self):
        self.assertTrue(DataValidator.validate_role_access("Admin", "DELETE"))
        self.assertTrue(DataValidator.validate_role_access("Pharmacist", "INSERT"))
        self.assertTrue(DataValidator.validate_role_access("Cashier", "CHECKOUT"))

        with self.assertRaises(ValidationError) as ctx:
            DataValidator.validate_role_access("Cashier", "DELETE")
        self.assertEqual(ctx.exception.defect_code, "DEF-10")

        with self.assertRaises(ValidationError) as ctx:
            DataValidator.validate_role_access("Pharmacist", "DELETE")
        self.assertEqual(ctx.exception.defect_code, "DEF-10")


class TestReview2DatabaseAndCRUD(unittest.TestCase):
    """Verifies SQLite database operations, CRUD functions, customer auto-storage, and supplier deals."""

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
        ids = [m["id"] for m in meds]
        self.assertEqual(ids, sorted(ids))

    def test_barcode_and_batch_lookup(self):
        # Search by barcode
        med = MedicineRepository.search_by_barcode_or_batch("890100100101")
        self.assertIsNotNone(med)
        self.assertTrue("Augmentin" in med["name"] or "890100100101" == med.get("barcode"))

        # Search by batch
        med_batch = MedicineRepository.search_by_barcode_or_batch("BATCH-AUG01")
        self.assertIsNotNone(med_batch)
        self.assertEqual(med_batch["batch_no"], "BATCH-AUG01")

    def test_customer_auto_registration_and_upsert(self):
        test_phone = "9811223344"
        test_name = "Sunita Rao"

        # Auto-create customer
        cust = CustomerRepository.get_or_create(test_name, test_phone)
        digits = re.sub(r"\D", "", cust["phone"])
        self.assertEqual(digits, test_phone)
        self.assertEqual(cust["name"], test_name)

        # Record a sale
        CustomerRepository.record_sale(test_phone, 450.0)
        updated = CustomerRepository.get_by_phone(test_phone)
        self.assertGreaterEqual(updated["total_orders"], 1)
        self.assertGreaterEqual(updated["total_spent"], 450.0)

    def test_supplier_deal_comparison_and_ranking(self):
        med = MedicineRepository.get_all()[0]
        deals = SupplierDealRepository.get_deals_for_medicine(med["id"])
        self.assertGreater(len(deals), 0)

        # Verify deals are sorted by highest discount
        discounts = [d["discount_percent"] for d in deals]
        self.assertEqual(discounts, sorted(discounts, reverse=True))

        # Best deal has highest discount
        best_deal = deals[0]
        self.assertTrue(best_deal["is_best_deal"])
        self.assertGreater(best_deal["profit_margin_percent"], 0)

    def test_sales_checkout_with_differential_gst_and_discount(self):
        med = MedicineRepository.get_all()[0]
        items = [{
            "medicine_id": med["id"],
            "unit_price": med["sale_price"],
            "tax_rate": med.get("tax_rate", 5.0),
            "quantity": 1
        }]

        inv_no, net_total = SalesRepository.create_sale(
            customer_name="Vijay Kumar",
            customer_phone="9988776655",
            items=items,
            payment_mode="UPI",
            discount_amount=10.0,
            user_role="Pharmacist"
        )
        self.assertTrue(inv_no.startswith("INV-"))
        self.assertGreater(net_total, 0)

        # Verify customer was automatically upserted
        cust = CustomerRepository.get_by_phone("9988776655")
        self.assertIsNotNone(cust)
        self.assertEqual(cust["name"], "Vijay Kumar")


if __name__ == "__main__":
    unittest.main()

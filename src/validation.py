"""
Poka-Yoke Validation and Error Prevention Engine
BBAT104: Fundamentals of TQM (Academic Session 2026-27)
Student: Anmol Joshi (Roll No: 2410302004, Branch: CSE-B)
Quality Goal [Q07: Improve Data Accuracy]
"""

import re
from datetime import datetime, date
from src.models import DefectRepository


class ValidationError(ValueError):
    """Custom exception raised when a Poka-Yoke constraint is violated."""
    def __init__(self, message, defect_code="DEF-00", category="General Validation", attempted_value=""):
        super().__init__(message)
        self.message = message
        self.defect_code = defect_code
        self.category = category
        self.attempted_value = attempted_value
        # Auto-record defect in SQC logs
        try:
            DefectRepository.log(defect_code, category, attempted_value, message)
        except Exception:
            pass


class DataValidator:
    """Rigorous Poka-Yoke validators enforcing data accuracy at entry point."""

    VALID_DOSAGE_FORMS = [
        "Tablet", "Capsule", "Syrup", "Injection",
        "Ointment", "Drops", "Inhaler", "Suppository"
    ]

    VALID_SCHEDULES = [
        "OTC", "Schedule H", "Schedule H1", "Schedule X"
    ]

    VALID_CATEGORIES = [
        "Antibiotic", "Analgesic", "Antihistamine", "Antidiabetic",
        "Cardiovascular", "Gastrointestinal", "Respiratory", "Dermatological"
    ]

    @staticmethod
    def validate_expiry_date(date_str, require_future=True):
        """Validates that date matches YYYY-MM-DD and is not already expired."""
        if not date_str or not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
            raise ValidationError(
                f"Expiry date '{date_str}' does not match required format 'YYYY-MM-DD'.",
                defect_code="DEF-01",
                category="Date Format Mismatch",
                attempted_value=date_str
            )
        try:
            exp_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError as e:
            raise ValidationError(
                f"Date '{date_str}' is not a valid calendar date: {e}",
                defect_code="DEF-01",
                category="Invalid Calendar Date",
                attempted_value=date_str
            )

        if require_future and exp_date <= date.today():
            raise ValidationError(
                f"Expiry date '{date_str}' must be strictly in the future. (Current date is {date.today()})",
                defect_code="DEF-02",
                category="Expired Batch Entry",
                attempted_value=date_str
            )
        return date_str

    @staticmethod
    def validate_batch_number(batch_str):
        """Validates that batch number matches BATCH-[A-Z0-9]{4,10}."""
        batch_clean = batch_str.strip().upper()
        if not re.match(r"^BATCH-[A-Z0-9]{3,12}$", batch_clean):
            raise ValidationError(
                f"Batch number '{batch_str}' must follow the standard syntax 'BATCH-XXXXX' (alphanumeric uppercase).",
                defect_code="DEF-03",
                category="Batch Code Syntax Violation",
                attempted_value=batch_str
            )
        return batch_clean

    @staticmethod
    def validate_phone(phone_str):
        """Validates customer and supplier telephone numbers."""
        digits = re.sub(r"\D", "", phone_str)
        if len(digits) != 10:
            raise ValidationError(
                f"Phone number '{phone_str}' must contain exactly 10 digits.",
                defect_code="DEF-04",
                category="Malformed Phone Format",
                attempted_value=phone_str
            )
        # Standardize mask: (XXX) XXX-XXXX
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"

    @staticmethod
    def validate_prices(purchase_price, sale_price):
        """Validates financial bounds and ensures non-inverted margin."""
        try:
            cost = float(purchase_price)
            sale = float(sale_price)
        except (ValueError, TypeError):
            raise ValidationError(
                "Price values must be valid numeric floating-point numbers.",
                defect_code="DEF-05",
                category="Non-Numeric Currency",
                attempted_value=f"Cost:{purchase_price}, Sale:{sale_price}"
            )

        if cost < 0 or sale < 0:
            raise ValidationError(
                "Prices cannot be negative.",
                defect_code="DEF-05",
                category="Negative Price Attempt",
                attempted_value=f"Cost:{cost}, Sale:{sale}"
            )

        if sale < cost:
            raise ValidationError(
                f"Retail sale price (Rs. {sale:.2f}) cannot be less than wholesale cost price (Rs. {cost:.2f}).",
                defect_code="DEF-05",
                category="Inverted Profit Margin",
                attempted_value=f"Cost:{cost}, Sale:{sale}"
            )
        return round(cost, 2), round(sale, 2)

    @staticmethod
    def validate_stock_quantity(stock_val):
        """Enforces non-negative integer stock quantity."""
        try:
            stock = int(stock_val)
        except (ValueError, TypeError):
            raise ValidationError(
                f"Stock quantity '{stock_val}' must be a valid integer.",
                defect_code="DEF-06",
                category="Non-Integer Stock",
                attempted_value=stock_val
            )
        if stock < 0:
            raise ValidationError(
                f"Stock quantity ({stock}) cannot be negative.",
                defect_code="DEF-06",
                category="Negative Stock Quantity",
                attempted_value=stock_val
            )
        return stock

    @staticmethod
    def validate_enum(value, valid_choices, field_name):
        """Guarantees value belongs to constrained dropdown list."""
        if value not in valid_choices:
            raise ValidationError(
                f"Invalid {field_name} '{value}'. Allowed options: {', '.join(valid_choices)}.",
                defect_code="DEF-07",
                category=f"Invalid {field_name} Selection",
                attempted_value=value
            )
        return value

# Step 25 milestone update - feat(q07-dropdowns): integrate locked readonly comboboxes for clinical dosage forms and drug schedules

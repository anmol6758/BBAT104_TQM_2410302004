"""
Validation Layer and Poka-Yoke Controls:
Mistake-proofing mechanisms for data accuracy (Q07 Goal):
- Date validation (format, valid calendar dates, future expiration enforcement)
- Batch number validation (standard prefix, alphanumeric syntax, collision rejection)
- Price margins and non-negativity (cost price cannot exceed sale price)
- Dropdown constrained selections (dosage forms, schedules, categories)
- Indian phone number masking and validation (10 digits starting with 6-9, rejecting dummy repeats)
- Differential GST tax slabs (0%, 5%, 12%, 18%, 28%)
- Manual customer discount validation (% or flat Rs.)
- Role-based access control (Admin, Pharmacist, Cashier)
"""

import re
from datetime import datetime, date


class ValidationError(Exception):
    """Custom exception raised when Poka-Yoke validation fails."""
    def __init__(self, message, defect_code=None, category=None, attempted_value=None):
        super().__init__(message)
        self.message = message
        self.defect_code = defect_code or "DEF-GEN"
        self.category = category or "General Input Error"
        self.attempted_value = attempted_value


class DataValidator:
    """Centralized Poka-Yoke Validation Service for Q07 Data Accuracy."""

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

    VALID_TAX_RATES = [0.0, 5.0, 12.0, 18.0, 28.0]

    ROLE_PERMISSIONS = {
        "Admin": {"INSERT", "UPDATE", "DELETE", "CHECKOUT", "VIEW", "COMPARE_DEALS", "EXPORT"},
        "Pharmacist": {"INSERT", "UPDATE", "CHECKOUT", "VIEW", "COMPARE_DEALS"},
        "Cashier": {"CHECKOUT", "VIEW"},
    }

    @staticmethod
    def validate_expiry_date(date_str, require_future=True):
        """Validates YYYY-MM-DD format, calendar validity, and future expiration."""
        if not date_str or not isinstance(date_str, str):
            raise ValidationError(
                "Expiry date is required.",
                defect_code="DEF-01",
                category="Missing Expiry Date",
                attempted_value=date_str
            )

        match = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", date_str.strip())
        if not match:
            raise ValidationError(
                f"Invalid date format '{date_str}'. Expected format is YYYY-MM-DD.",
                defect_code="DEF-01",
                category="Malformed Date Syntax",
                attempted_value=date_str
            )

        year, month, day = map(int, match.groups())
        try:
            parsed_date = date(year, month, day)
        except ValueError as ex:
            raise ValidationError(
                f"Invalid calendar date '{date_str}': {ex}",
                defect_code="DEF-01",
                category="Invalid Calendar Date",
                attempted_value=date_str
            )

        if require_future and parsed_date <= date.today():
            raise ValidationError(
                f"Medicine expiry date ({date_str}) must be in the future. Expired drugs cannot be received or registered.",
                defect_code="DEF-02",
                category="Expired Product Attempt",
                attempted_value=date_str
            )

        return parsed_date.strftime("%Y-%m-%d")

    @staticmethod
    def validate_batch_number(batch_str):
        """Enforces standard BATCH- prefix and alphanumeric format."""
        if not batch_str or not isinstance(batch_str, str):
            raise ValidationError(
                "Batch number is required.",
                defect_code="DEF-03",
                category="Missing Batch Number",
                attempted_value=batch_str
            )

        clean = batch_str.strip().upper()
        if not re.match(r"^BATCH-[A-Z0-9]{3,15}$", clean):
            raise ValidationError(
                f"Invalid batch number '{batch_str}'. Format must be 'BATCH-' followed by 3-15 uppercase alphanumeric characters (e.g., BATCH-2026A).",
                defect_code="DEF-03",
                category="Malformed Batch Syntax",
                attempted_value=batch_str
            )

        return clean

    @staticmethod
    def validate_phone(phone_str):
        """
        Validates authentic 10-digit Indian mobile number format (6-9 prefix).
        Rejects dummy sequences (e.g. 1111111111, 0000000000) and non-numeric junk.
        Formats to standard display mask: (XXX) XXX-XXXX.
        """
        if not phone_str or not isinstance(phone_str, str):
            raise ValidationError(
                "Customer phone number is required.",
                defect_code="DEF-04",
                category="Missing Phone Number",
                attempted_value=phone_str
            )

        # Extract only digits
        digits = re.sub(r"\D", "", phone_str.strip())
        if len(digits) != 10:
            raise ValidationError(
                f"Phone number must contain exactly 10 digits. Found {len(digits)} digits in '{phone_str}'.",
                defect_code="DEF-04",
                category="Malformed Phone Format",
                attempted_value=phone_str
            )

        # Enforce valid mobile starting digit (6, 7, 8, or 9)
        if not re.match(r"^[6-9]\d{9}$", digits):
            raise ValidationError(
                f"Invalid mobile number '{phone_str}'. Must be a valid 10-digit number starting with 6, 7, 8, or 9.",
                defect_code="DEF-04",
                category="Invalid Mobile Prefix",
                attempted_value=phone_str
            )

        # Reject repetitive dummy numbers (e.g. 0000000000, 9999999999, 1111111111)
        if len(set(digits)) == 1:
            raise ValidationError(
                f"Dummy repeating number '{phone_str}' is rejected by Poka-Yoke rule.",
                defect_code="DEF-04",
                category="Dummy Phone Number",
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

    @staticmethod
    def validate_tax_rate(rate_val):
        """Validates GST tax rate matches standard pharmaceutical tax slabs."""
        try:
            r = float(str(rate_val).replace("%", "").strip())
        except (ValueError, TypeError):
            raise ValidationError(
                f"Tax rate '{rate_val}' must be a valid numeric percentage.",
                defect_code="DEF-08",
                category="Invalid Tax Rate Format",
                attempted_value=rate_val
            )
        if r not in DataValidator.VALID_TAX_RATES:
            raise ValidationError(
                f"Tax rate {r}% is not an official GST slab. Allowed slabs: {DataValidator.VALID_TAX_RATES}%.",
                defect_code="DEF-08",
                category="Unsupported GST Slab",
                attempted_value=rate_val
            )
        return r

    @staticmethod
    def validate_discount(discount_input, gross_amount):
        """
        Validates manual customer discount (supports percentage e.g. '10%' or flat amount e.g. '50' or 'Rs. 50').
        Guarantees discount does not exceed subtotal.
        """
        if not discount_input or str(discount_input).strip() == "":
            return 0.0

        val_str = str(discount_input).strip()
        val_str = re.sub(r"(?i)rs\.?|₹|\$", "", val_str).strip()

        try:
            if "%" in val_str:
                pct = float(val_str.replace("%", "").strip())
                if pct < 0.0 or pct > 100.0:
                    raise ValidationError(
                        f"Discount percentage ({pct}%) must be between 0% and 100%.",
                        defect_code="DEF-09",
                        category="Excessive Discount Percentage",
                        attempted_value=discount_input
                    )
                discount_amt = round(gross_amount * (pct / 100.0), 2)
            else:
                flat = float(val_str)
                if flat < 0.0:
                    raise ValidationError(
                        "Discount amount cannot be negative.",
                        defect_code="DEF-09",
                        category="Negative Discount Attempt",
                        attempted_value=discount_input
                    )
                if flat > gross_amount:
                    raise ValidationError(
                        f"Discount amount (Rs. {flat:.2f}) cannot exceed gross bill subtotal (Rs. {gross_amount:.2f}).",
                        defect_code="DEF-09",
                        category="Discount Exceeds Total",
                        attempted_value=discount_input
                    )
                discount_amt = round(flat, 2)
        except ValueError:
            raise ValidationError(
                f"Invalid discount input '{discount_input}'. Enter a number (e.g. 50) or percentage (e.g. 10%).",
                defect_code="DEF-09",
                category="Malformed Discount Format",
                attempted_value=discount_input
            )

        return discount_amt

    @staticmethod
    def validate_role_access(current_role, allowed_roles_or_action, action_name=None):
        """
        Enforces Role-Based Access Control (RBAC) Poka-Yoke gate.
        Supports both:
        - validate_role_access(current_role, "DELETE")
        - validate_role_access(current_role, ["Admin"], "DELETE")
        """
        if action_name is None:
            # 2-arg mode: allowed_roles_or_action is the action name
            action = allowed_roles_or_action
            perms = DataValidator.ROLE_PERMISSIONS.get(current_role, set())
            if action not in perms:
                raise ValidationError(
                    f"Access Denied: Role '{current_role}' does not have permission to execute '{action}'.",
                    defect_code="DEF-10",
                    category="Unauthorized Role Action",
                    attempted_value=f"{current_role}->{action}"
                )
            return True
        else:
            # 3-arg mode: allowed_roles_or_action is a list/set of allowed roles
            allowed_roles = allowed_roles_or_action
            if current_role not in allowed_roles:
                raise ValidationError(
                    f"Access Denied: Role '{current_role}' does not have permission to execute '{action_name}'. "
                    f"Required role(s): {', '.join(allowed_roles)}.",
                    defect_code="DEF-10",
                    category="Unauthorized Role Action",
                    attempted_value=f"{current_role}->{action_name}"
                )
            return True

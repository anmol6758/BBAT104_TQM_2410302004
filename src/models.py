"""
Data Access Layer and Domain Models for Pharmacy Management System
BBAT104: Fundamentals of TQM (Academic Session 2026-27)
Student: Anmol Joshi (Roll No: 2410302004, Branch: CSE-B)
"""

from datetime import datetime, date
from src.database import get_connection


class AuditRepository:
    """Handles querying and logging of immutable audit trails."""

    @staticmethod
    def log(conn, action_type, table_name, record_id, field_name=None, old_value=None, new_value=None, user_role="Pharmacist"):
        conn.execute("""
            INSERT INTO audit_logs (action_type, table_name, record_id, field_name, old_value, new_value, user_role)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (action_type, table_name, record_id, field_name, str(old_value) if old_value is not None else None, str(new_value) if new_value is not None else None, user_role))

    @staticmethod
    def get_all(limit=100, action_type=None, table_name=None):
        conn = get_connection()
        query = "SELECT * FROM audit_logs WHERE 1=1"
        params = []
        if action_type and action_type != "All":
            query += " AND action_type = ?"
            params.append(action_type)
        if table_name and table_name != "All":
            query += " AND table_name = ?"
            params.append(table_name)
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        rows = conn.execute(query, params).fetchall()
        conn.close()
        return [dict(r) for r in rows]


class DefectRepository:
    """Captures intercepted data validation rejections for SQC checksheet analysis."""

    @staticmethod
    def log(defect_code, defect_category, attempted_value, error_message, severity=3):
        conn = get_connection()
        with conn:
            conn.execute("""
                INSERT INTO defect_logs (defect_code, defect_category, attempted_value, error_message, severity)
                VALUES (?, ?, ?, ?, ?)
            """, (defect_code, defect_category, str(attempted_value), error_message, severity))
        conn.close()

    @staticmethod
    def get_summary_counts():
        conn = get_connection()
        rows = conn.execute("""
            SELECT defect_code, defect_category, COUNT(*) as count, MAX(severity) as max_severity
            FROM defect_logs
            GROUP BY defect_code, defect_category
            ORDER BY count DESC
        """).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_recent_defects(limit=50):
        conn = get_connection()
        rows = conn.execute("""
            SELECT * FROM defect_logs ORDER BY id DESC LIMIT ?
        """, (limit,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]


class MedicineRepository:
    """Domain CRUD repository for pharmaceuticals with built-in audit and validation."""

    @staticmethod
    def get_all(search=None, category=None):
        conn = get_connection()
        query = """
            SELECT m.*, s.name as supplier_name 
            FROM medicines m 
            LEFT JOIN suppliers s ON m.supplier_id = s.id 
            WHERE 1=1
        """
        params = []
        if search:
            query += " AND (m.name LIKE ? OR m.generic_name LIKE ? OR m.batch_no LIKE ?)"
            s_term = f"%{search}%"
            params.extend([s_term, s_term, s_term])
        if category and category != "All":
            query += " AND m.category = ?"
            params.append(category)
        query += " ORDER BY m.name ASC"
        rows = conn.execute(query, params).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_by_id(med_id):
        conn = get_connection()
        row = conn.execute("""
            SELECT m.*, s.name as supplier_name 
            FROM medicines m 
            LEFT JOIN suppliers s ON m.supplier_id = s.id 
            WHERE m.id = ?
        """, (med_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def search_autocomplete(query_str, limit=10):
        """Cross-searches Brand Name and Generic Salt for real-time auto-complete dropdown."""
        if not query_str or len(query_str.strip()) < 1:
            return []
        conn = get_connection()
        s = f"%{query_str.strip()}%"
        rows = conn.execute("""
            SELECT id, name, generic_name, dosage_form, batch_no, sale_price, stock_qty, expiry_date
            FROM medicines
            WHERE (name LIKE ? OR generic_name LIKE ?) AND stock_qty > 0
            ORDER BY name ASC
            LIMIT ?
        """, (s, s, limit)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def create(data, user_role="Pharmacist"):
        conn = get_connection()
        with conn:
            cursor = conn.execute("""
                INSERT INTO medicines (
                    name, generic_name, category, dosage_form, schedule_type,
                    batch_no, expiry_date, purchase_price, sale_price, stock_qty,
                    reorder_level, supplier_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data["name"], data["generic_name"], data["category"], data["dosage_form"],
                data.get("schedule_type", "OTC"), data["batch_no"], data["expiry_date"],
                float(data["purchase_price"]), float(data["sale_price"]), int(data["stock_qty"]),
                int(data.get("reorder_level", 15)), data.get("supplier_id")
            ))
            med_id = cursor.lastrowid
            AuditRepository.log(conn, "INSERT", "medicines", med_id, "all_fields", None, f"Created {data['name']}", user_role)
        conn.close()
        return med_id

    @staticmethod
    def update(med_id, new_data, user_role="Pharmacist"):
        conn = get_connection()
        with conn:
            current = conn.execute("SELECT * FROM medicines WHERE id = ?", (med_id,)).fetchone()
            if not current:
                conn.close()
                raise ValueError(f"Medicine ID {med_id} not found.")

            # Identify mutated fields for granular audit logging
            fields = ["name", "generic_name", "category", "dosage_form", "schedule_type",
                      "batch_no", "expiry_date", "purchase_price", "sale_price", "stock_qty", "reorder_level", "supplier_id"]
            
            for f in fields:
                if f in new_data:
                    old_v = current[f]
                    new_v = new_data[f]
                    # Handle type comparisons
                    if f in ("purchase_price", "sale_price"):
                        old_v = float(old_v)
                        new_v = float(new_v)
                    elif f in ("stock_qty", "reorder_level", "supplier_id") and new_v is not None:
                        old_v = int(old_v) if old_v is not None else None
                        new_v = int(new_v)

                    if old_v != new_v:
                        AuditRepository.log(conn, "UPDATE", "medicines", med_id, f, old_v, new_v, user_role)

            conn.execute("""
                UPDATE medicines SET
                    name = ?, generic_name = ?, category = ?, dosage_form = ?,
                    schedule_type = ?, batch_no = ?, expiry_date = ?,
                    purchase_price = ?, sale_price = ?, stock_qty = ?,
                    reorder_level = ?, supplier_id = ?
                WHERE id = ?
            """, (
                new_data["name"], new_data["generic_name"], new_data["category"], new_data["dosage_form"],
                new_data.get("schedule_type", "OTC"), new_data["batch_no"], new_data["expiry_date"],
                float(new_data["purchase_price"]), float(new_data["sale_price"]), int(new_data["stock_qty"]),
                int(new_data.get("reorder_level", 15)), new_data.get("supplier_id"), med_id
            ))
        conn.close()

    @staticmethod
    def delete(med_id, user_role="Pharmacist"):
        conn = get_connection()
        with conn:
            # Check sales foreign key constraint
            sales_count = conn.execute("SELECT COUNT(*) as cnt FROM sale_items WHERE medicine_id = ?", (med_id,)).fetchone()["cnt"]
            if sales_count > 0:
                conn.close()
                raise ValueError(f"Integrity Violation: Cannot delete medicine ID {med_id} because it has {sales_count} historical sales records. Deactivation recommended instead.")

            med = conn.execute("SELECT name FROM medicines WHERE id = ?", (med_id,)).fetchone()
            name = med["name"] if med else str(med_id)
            conn.execute("DELETE FROM medicines WHERE id = ?", (med_id,))
            AuditRepository.log(conn, "DELETE", "medicines", med_id, "all_fields", name, None, user_role)
        conn.close()

    @staticmethod
    def get_stock_alerts():
        conn = get_connection()
        today = date.today().strftime("%Y-%m-%d")
        warning_expiry = (date.today() + __import__("datetime").timedelta(days=90)).strftime("%Y-%m-%d")
        
        low_stock = conn.execute("""
            SELECT * FROM medicines WHERE stock_qty <= reorder_level ORDER BY stock_qty ASC
        """).fetchall()

        expiring = conn.execute("""
            SELECT * FROM medicines WHERE expiry_date <= ? ORDER BY expiry_date ASC
        """, (warning_expiry,)).fetchall()

        conn.close()
        return [dict(r) for r in low_stock], [dict(r) for r in expiring]


class SupplierRepository:
    """Repository for certified pharmaceutical suppliers."""

    @staticmethod
    def get_all():
        conn = get_connection()
        rows = conn.execute("SELECT * FROM suppliers ORDER BY name ASC").fetchall()
        conn.close()
        return [dict(r) for r in rows]


class SalesRepository:
    """Atomic sales transaction engine ensuring inventory deduction and audit logging."""

    @staticmethod
    def create_sale(customer_name, customer_phone, items, payment_mode="Cash", tax_rate=0.05, user_role="Pharmacist"):
        """
        items: list of dicts with keys: {'medicine_id', 'quantity', 'unit_price'}
        """
        conn = get_connection()
        with conn:
            # 1. Validate stock availability for each item
            gross_total = 0.0
            for item in items:
                med = conn.execute("SELECT name, stock_qty FROM medicines WHERE id = ?", (item["medicine_id"],)).fetchone()
                if not med:
                    raise ValueError(f"Medicine ID {item['medicine_id']} not found.")
                if med["stock_qty"] < item["quantity"]:
                    raise ValueError(f"Insufficient stock for '{med['name']}'. Requested: {item['quantity']}, Available: {med['stock_qty']}.")
                gross_total += item["quantity"] * item["unit_price"]

            tax_amount = round(gross_total * tax_rate, 2)
            net_amount = round(gross_total + tax_amount, 2)
            timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")
            invoice_no = f"INV-{timestamp_str}"

            # 2. Insert sales invoice header
            cursor = conn.execute("""
                INSERT INTO sales (invoice_no, customer_name, customer_phone, total_amount, tax_amount, net_amount, payment_mode)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (invoice_no, customer_name, customer_phone, gross_total, tax_amount, net_amount, payment_mode))
            sale_id = cursor.lastrowid

            # 3. Insert sale items & deduct inventory atomically
            for item in items:
                subtotal = round(item["quantity"] * item["unit_price"], 2)
                conn.execute("""
                    INSERT INTO sale_items (sale_id, medicine_id, quantity, unit_price, subtotal)
                    VALUES (?, ?, ?, ?, ?)
                """, (sale_id, item["medicine_id"], item["quantity"], item["unit_price"], subtotal))

                # Decrement stock
                old_stock = conn.execute("SELECT stock_qty, name FROM medicines WHERE id = ?", (item["medicine_id"],)).fetchone()
                new_stock = old_stock["stock_qty"] - item["quantity"]
                conn.execute("UPDATE medicines SET stock_qty = ? WHERE id = ?", (new_stock, item["medicine_id"]))

                # Audit log stock adjustment
                AuditRepository.log(
                    conn, "CHECKOUT", "medicines", item["medicine_id"], "stock_qty",
                    old_stock["stock_qty"], new_stock, f"{user_role} (Invoice {invoice_no})"
                )

            # Audit log sale creation
            AuditRepository.log(conn, "CHECKOUT", "sales", sale_id, "net_amount", None, f"Invoice {invoice_no} | Net: Rs. {net_amount:.2f}", user_role)

        conn.close()
        return invoice_no, net_amount

    @staticmethod
    def get_all_sales(limit=50):
        conn = get_connection()
        rows = conn.execute("""
            SELECT s.*, COUNT(si.id) as item_count 
            FROM sales s 
            LEFT JOIN sale_items si ON s.id = si.sale_id 
            GROUP BY s.id 
            ORDER BY s.id DESC 
            LIMIT ?
        """, (limit,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

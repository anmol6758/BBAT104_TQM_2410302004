"""
Data Access Layer and Domain Models for Pharmacy Management System
BBAT104: Fundamentals of TQM (Academic Session 2026-27)
Student: Anmol Joshi (Roll No: 2410302004, Branch: CSE-B)
Quality Goal [Q07: Improve Data Accuracy]
"""

import re
from datetime import datetime, date, timedelta
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


class CustomerRepository:
    """
    Manages customer and patient master records.
    Automatically upserts records upon medicine sales, avoiding tedious manual 'Add Patient' steps.
    """

    @staticmethod
    def find_by_phone(phone_str):
        if not phone_str:
            return None
        digits = re.sub(r"\D", "", phone_str)
        conn = get_connection()
        row = conn.execute("""
            SELECT * FROM customers 
            WHERE phone LIKE ? OR replace(replace(replace(replace(phone, ' ', ''), '-', ''), '(', ''), ')', '') = ?
        """, (f"%{digits}%", digits)).fetchone()
        conn.close()
        if not row:
            return None
        d = dict(row)
        d["total_orders"] = d.get("total_visits", 1)
        return d

    @staticmethod
    def get_by_phone(phone_str):
        return CustomerRepository.find_by_phone(phone_str)

    @staticmethod
    def get_or_create(name, phone, address=None):
        if not phone:
            return None
        digits = re.sub(r"\D", "", phone)
        standard_phone = f"({digits[:3]}) {digits[3:6]}-{digits[6:]}" if len(digits) == 10 else phone
        cleaned_name = name.strip() if name and name.strip() else "Walk-in Patient"

        conn = get_connection()
        with conn:
            row = conn.execute("""
                SELECT * FROM customers 
                WHERE replace(replace(replace(replace(phone, ' ', ''), '-', ''), '(', ''), ')', '') = ?
            """, (digits,)).fetchone()

            if row:
                cust_id = row["id"]
                # Update visit count and name if provided and not generic
                new_visits = row["total_visits"] + 1
                updated_name = cleaned_name if cleaned_name != "Walk-in Patient" else row["name"]
                conn.execute("""
                    UPDATE customers 
                    SET name = ?, total_visits = ?, last_visit = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, (updated_name, new_visits, cust_id))
            else:
                cursor = conn.execute("""
                    INSERT INTO customers (name, phone, address, total_visits, total_spent)
                    VALUES (?, ?, ?, 1, 0.0)
                """, (cleaned_name, standard_phone, address or "Direct Counter"))
                cust_id = cursor.lastrowid
            
            saved = conn.execute("SELECT * FROM customers WHERE id = ?", (cust_id,)).fetchone()
        conn.close()
        if not saved:
            return None
        d = dict(saved)
        d["total_orders"] = d.get("total_visits", 1)
        return d

    @staticmethod
    def record_sale(phone, amount_spent):
        if not phone:
            return
        digits = re.sub(r"\D", "", phone)
        conn = get_connection()
        with conn:
            conn.execute("""
                UPDATE customers 
                SET total_spent = total_spent + ?, last_visit = CURRENT_TIMESTAMP 
                WHERE replace(replace(replace(replace(phone, ' ', ''), '-', ''), '(', ''), ')', '') = ?
            """, (amount_spent, digits))
        conn.close()

    @staticmethod
    def search(query_str, limit=5):
        if not query_str or len(query_str.strip()) < 2:
            return []
        q = f"%{query_str.strip()}%"
        conn = get_connection()
        rows = conn.execute("""
            SELECT * FROM customers 
            WHERE name LIKE ? OR phone LIKE ? 
            ORDER BY total_visits DESC LIMIT ?
        """, (q, q, limit)).fetchall()
        conn.close()
        return [dict(r) for r in rows]


class SupplierDealRepository:
    """
    Empowers pharmacists to evaluate which supplier offers the best purchase price / highest discount
    for any given medicine, ensuring cost-efficient procurement.
    """

    @staticmethod
    def get_deals_for_medicine(med_id):
        conn = get_connection()
        rows = conn.execute("""
            SELECT 
                d.id as deal_id,
                d.medicine_id,
                d.supplier_id,
                s.name as supplier_name,
                s.contact_person,
                s.phone as supplier_phone,
                s.email as supplier_email,
                d.mrp,
                d.cost_price,
                d.discount_percent,
                d.delivery_days,
                d.min_order_qty,
                d.is_preferred,
                round(d.mrp - d.cost_price, 2) as savings_per_unit,
                round(((d.mrp - d.cost_price) / d.mrp) * 100.0, 1) as profit_margin_percent
            FROM supplier_deals d
            JOIN suppliers s ON d.supplier_id = s.id
            WHERE d.medicine_id = ?
            ORDER BY d.discount_percent DESC, d.cost_price ASC
        """, (med_id,)).fetchall()
        conn.close()

        deals = [dict(r) for r in rows]
        if deals:
            # Highlight top deal
            deals[0]["is_best_deal"] = True
            for d in deals[1:]:
                d["is_best_deal"] = False
        return deals

    @staticmethod
    def assign_supplier_to_medicine(med_id, supplier_id, new_cost=None, user_role="Pharmacist"):
        conn = get_connection()
        with conn:
            # Update preferred status in supplier_deals
            conn.execute("UPDATE supplier_deals SET is_preferred = 0 WHERE medicine_id = ?", (med_id,))
            conn.execute("UPDATE supplier_deals SET is_preferred = 1 WHERE medicine_id = ? AND supplier_id = ?", (med_id, supplier_id))

            # Fetch supplier and deal info
            sup = conn.execute("SELECT name FROM suppliers WHERE id = ?", (supplier_id,)).fetchone()
            sup_name = sup["name"] if sup else f"Supplier #{supplier_id}"
            
            # Update medicine master supplier_id and purchase_price if provided
            if new_cost is not None:
                conn.execute("UPDATE medicines SET supplier_id = ?, purchase_price = ? WHERE id = ?", (supplier_id, float(new_cost), med_id))
            else:
                conn.execute("UPDATE medicines SET supplier_id = ? WHERE id = ?", (supplier_id, med_id))

            AuditRepository.log(
                conn, "UPDATE", "medicines", med_id, "supplier_id",
                None, f"Assigned preferred supplier: {sup_name}", user_role
            )
        conn.close()


class MedicineRepository:
    """Domain CRUD repository for pharmaceuticals with built-in audit, multi-tier tax, and validation."""

    @staticmethod
    def get_all(search=None, category=None, status_filter=None, sort_by="id_asc"):
        conn = get_connection()
        query = """
            SELECT m.*, s.name as supplier_name 
            FROM medicines m 
            LEFT JOIN suppliers s ON m.supplier_id = s.id 
            WHERE 1=1
        """
        params = []
        if search:
            query += " AND (m.name LIKE ? OR m.generic_name LIKE ? OR m.batch_no LIKE ? OR (m.barcode IS NOT NULL AND m.barcode LIKE ?))"
            s_term = f"%{search}%"
            params.extend([s_term, s_term, s_term, s_term])
        if category and category != "All":
            query += " AND m.category = ?"
            params.append(category)
        if status_filter == "Low Stock":
            query += " AND m.stock_qty <= m.reorder_level"
        elif status_filter == "Expiring Soon":
            warning_expiry = (date.today() + timedelta(days=90)).strftime("%Y-%m-%d")
            query += " AND m.expiry_date <= ?"
            params.append(warning_expiry)

        # Dynamic sorting (default ID ascending)
        sort_map = {
            "id_asc": "m.id ASC",
            "id_desc": "m.id DESC",
            "name_asc": "m.name ASC",
            "name_desc": "m.name DESC",
            "stock_asc": "m.stock_qty ASC",
            "stock_desc": "m.stock_qty DESC",
            "expiry_asc": "m.expiry_date ASC",
            "price_asc": "m.sale_price ASC",
            "price_desc": "m.sale_price DESC",
        }
        order_clause = sort_map.get(sort_by, "m.id ASC")
        query += f" ORDER BY {order_clause}"

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
    def search_by_barcode_or_batch(code_str):
        """Unified barcode scanner and batch syntax lookup for fast one-scan POS dispensing."""
        if not code_str or not code_str.strip():
            return None
        clean_code = code_str.strip()
        conn = get_connection()
        
        # Check exact barcode, batch number, or ID
        query = """
            SELECT m.*, s.name as supplier_name 
            FROM medicines m 
            LEFT JOIN suppliers s ON m.supplier_id = s.id 
            WHERE m.barcode = ? OR m.batch_no = ? OR m.batch_no = ?
        """
        params = [clean_code, clean_code, f"BATCH-{clean_code.upper()}"]
        
        if clean_code.isdigit():
            query += " OR m.id = ?"
            params.append(int(clean_code))
            
        row = conn.execute(query, params).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def search_autocomplete(query_str, limit=10):
        """Cross-searches Brand Name, Generic Salt, Barcode, and Batch for real-time auto-complete dropdown."""
        if not query_str or len(query_str.strip()) < 1:
            return []
        conn = get_connection()
        s = f"%{query_str.strip()}%"
        rows = conn.execute("""
            SELECT id, name, generic_name, dosage_form, batch_no, barcode, sale_price, tax_rate, stock_qty, expiry_date
            FROM medicines
            WHERE (name LIKE ? OR generic_name LIKE ? OR batch_no LIKE ? OR (barcode IS NOT NULL AND barcode LIKE ?)) AND stock_qty > 0
            ORDER BY name ASC
            LIMIT ?
        """, (s, s, s, s, limit)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def create(data, user_role="Pharmacist"):
        conn = get_connection()
        with conn:
            tax_rate = float(data.get("tax_rate", 5.0))
            barcode = data.get("barcode", "").strip() or None

            cursor = conn.execute("""
                INSERT INTO medicines (
                    name, generic_name, category, dosage_form, schedule_type,
                    batch_no, barcode, expiry_date, purchase_price, sale_price, tax_rate, stock_qty,
                    reorder_level, supplier_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data["name"], data["generic_name"], data["category"], data["dosage_form"],
                data.get("schedule_type", "OTC"), data["batch_no"], barcode, data["expiry_date"],
                float(data["purchase_price"]), float(data["sale_price"]), tax_rate, int(data["stock_qty"]),
                int(data.get("reorder_level", 15)), data.get("supplier_id")
            ))
            med_id = cursor.lastrowid
            AuditRepository.log(conn, "INSERT", "medicines", med_id, "all_fields", None, f"Created {data['name']} (GST {tax_rate}%)", user_role)
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

            fields = ["name", "generic_name", "category", "dosage_form", "schedule_type",
                      "batch_no", "barcode", "expiry_date", "purchase_price", "sale_price", "tax_rate",
                      "stock_qty", "reorder_level", "supplier_id"]
            
            for f in fields:
                if f in new_data:
                    old_v = current[f] if f in current.keys() else None
                    new_v = new_data[f]
                    if f in ("purchase_price", "sale_price", "tax_rate"):
                        old_v = float(old_v) if old_v is not None else 0.0
                        new_v = float(new_v) if new_v is not None else 0.0
                    elif f in ("stock_qty", "reorder_level", "supplier_id") and new_v is not None:
                        old_v = int(old_v) if old_v is not None else None
                        new_v = int(new_v)

                    if old_v != new_v:
                        AuditRepository.log(conn, "UPDATE", "medicines", med_id, f, old_v, new_v, user_role)

            tax_rate = float(new_data.get("tax_rate", current["tax_rate"] if "tax_rate" in current.keys() else 5.0))
            barcode = new_data.get("barcode", current["barcode"] if "barcode" in current.keys() else "")
            barcode = barcode.strip() if barcode else None

            conn.execute("""
                UPDATE medicines SET
                    name = ?, generic_name = ?, category = ?, dosage_form = ?,
                    schedule_type = ?, batch_no = ?, barcode = ?, expiry_date = ?,
                    purchase_price = ?, sale_price = ?, tax_rate = ?, stock_qty = ?,
                    reorder_level = ?, supplier_id = ?
                WHERE id = ?
            """, (
                new_data["name"], new_data["generic_name"], new_data["category"], new_data["dosage_form"],
                new_data.get("schedule_type", "OTC"), new_data["batch_no"], barcode, new_data["expiry_date"],
                float(new_data["purchase_price"]), float(new_data["sale_price"]), tax_rate, int(new_data["stock_qty"]),
                int(new_data.get("reorder_level", 15)), new_data.get("supplier_id"), med_id
            ))
        conn.close()

    @staticmethod
    def delete(med_id, user_role="Pharmacist"):
        conn = get_connection()
        with conn:
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
        warning_expiry = (date.today() + timedelta(days=90)).strftime("%Y-%m-%d")
        
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
    """
    Atomic sales transaction engine supporting itemized differential GST tax slabs (0%, 5%, 12%, 18%),
    manual customer discounts, and automatic patient record upserting.
    """

    @staticmethod
    def create_sale(customer_name, customer_phone, items, payment_mode="Cash", tax_rate=None, discount_amount=0.0, user_role="Pharmacist"):
        """
        items: list of dicts with keys: {'medicine_id', 'quantity', 'unit_price', optional 'tax_rate'}
        """
        conn = get_connection()
        with conn:
            # 1. Validate stock availability and calculate line-item taxes
            gross_total = 0.0
            prepared_items = []

            for item in items:
                med = conn.execute("SELECT name, stock_qty, tax_rate FROM medicines WHERE id = ?", (item["medicine_id"],)).fetchone()
                if not med:
                    raise ValueError(f"Medicine ID {item['medicine_id']} not found.")
                if med["stock_qty"] < item["quantity"]:
                    raise ValueError(f"Insufficient stock for '{med['name']}'. Requested: {item['quantity']}, Available: {med['stock_qty']}.")
                
                # Use medicine specific tax rate unless overridden
                item_tax_rate = float(item.get("tax_rate", med["tax_rate"] if "tax_rate" in med.keys() and med["tax_rate"] is not None else 5.0))
                item_subtotal = round(item["quantity"] * float(item["unit_price"]), 2)
                gross_total += item_subtotal
                
                prepared_items.append({
                    "medicine_id": item["medicine_id"],
                    "name": med["name"],
                    "quantity": int(item["quantity"]),
                    "unit_price": float(item["unit_price"]),
                    "tax_rate": item_tax_rate,
                    "subtotal": item_subtotal
                })

            gross_total = round(gross_total, 2)
            discount_amount = max(0.0, min(round(float(discount_amount), 2), gross_total))

            # 2. Calculate itemized GST tax amounts (post-discount proportional allocation)
            total_tax_amount = 0.0
            discount_ratio = (gross_total - discount_amount) / gross_total if gross_total > 0 else 1.0

            for p_item in prepared_items:
                taxable_base = round(p_item["subtotal"] * discount_ratio, 2)
                item_tax = round(taxable_base * (p_item["tax_rate"] / 100.0), 2)
                p_item["tax_amount"] = item_tax
                total_tax_amount += item_tax

            total_tax_amount = round(total_tax_amount, 2)
            net_amount = round((gross_total - discount_amount) + total_tax_amount, 2)
            timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")
            invoice_no = f"INV-{timestamp_str}"

            # 3. Automatic Customer / Patient Record Storage
            if customer_phone:
                CustomerRepository.get_or_create(customer_name, customer_phone)
                CustomerRepository.record_sale(customer_phone, net_amount)

            # 4. Insert sales invoice header
            cursor = conn.execute("""
                INSERT INTO sales (invoice_no, customer_name, customer_phone, total_amount, discount_amount, tax_amount, net_amount, payment_mode)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (invoice_no, customer_name, customer_phone, gross_total, discount_amount, total_tax_amount, net_amount, payment_mode))
            sale_id = cursor.lastrowid

            # 5. Insert sale items & deduct inventory atomically
            for item in prepared_items:
                conn.execute("""
                    INSERT INTO sale_items (sale_id, medicine_id, quantity, unit_price, tax_rate, tax_amount, subtotal)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (sale_id, item["medicine_id"], item["quantity"], item["unit_price"], item["tax_rate"], item["tax_amount"], item["subtotal"]))

                # Decrement stock
                old_stock = conn.execute("SELECT stock_qty, name FROM medicines WHERE id = ?", (item["medicine_id"],)).fetchone()
                new_stock = old_stock["stock_qty"] - item["quantity"]
                conn.execute("UPDATE medicines SET stock_qty = ? WHERE id = ?", (new_stock, item["medicine_id"]))

                # Audit log stock adjustment
                AuditRepository.log(
                    conn, "CHECKOUT", "medicines", item["medicine_id"], "stock_qty",
                    old_stock["stock_qty"], new_stock, f"{user_role} (Invoice {invoice_no})"
                )

            # Audit log sale creation with discount and GST summary
            AuditRepository.log(
                conn, "CHECKOUT", "sales", sale_id, "net_amount", None,
                f"Invoice {invoice_no} | Gross: Rs. {gross_total:.2f} | Disc: Rs. {discount_amount:.2f} | GST: Rs. {total_tax_amount:.2f} | Net: Rs. {net_amount:.2f}",
                user_role
            )

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

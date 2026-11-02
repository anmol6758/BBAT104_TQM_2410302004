"""
Database Layer for Pharmacy Management System - [Q07: Improve Data Accuracy]
BBAT104: Fundamentals of TQM (Academic Session 2026-27)
Student: Anmol Joshi (Roll No: 2410302004, Branch: CSE-B)
"""

import os
import sqlite3
from datetime import datetime, date, timedelta

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
DB_PATH = os.path.join(DB_DIR, "pharmacy.db")


def get_connection(db_path=None):
    """Establishes an ACID-compliant connection with foreign keys and WAL enabled."""
    if db_path is None:
        db_path = DB_PATH
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn


def _run_migrations(conn):
    """Safely executes non-destructive schema migrations for existing databases."""
    cursor = conn.cursor()
    
    # 1. Check medicines columns
    med_cols = [row[1] for row in cursor.execute("PRAGMA table_info(medicines)").fetchall()]
    if "tax_rate" not in med_cols and len(med_cols) > 0:
        cursor.execute("ALTER TABLE medicines ADD COLUMN tax_rate REAL DEFAULT 5.0;")
    if "barcode" not in med_cols and len(med_cols) > 0:
        cursor.execute("ALTER TABLE medicines ADD COLUMN barcode TEXT;")

    # 2. Check sales columns
    sales_cols = [row[1] for row in cursor.execute("PRAGMA table_info(sales)").fetchall()]
    if "discount_amount" not in sales_cols and len(sales_cols) > 0:
        cursor.execute("ALTER TABLE sales ADD COLUMN discount_amount REAL DEFAULT 0.0;")

    # 3. Check sale_items columns
    item_cols = [row[1] for row in cursor.execute("PRAGMA table_info(sale_items)").fetchall()]
    if "tax_rate" not in item_cols and len(item_cols) > 0:
        cursor.execute("ALTER TABLE sale_items ADD COLUMN tax_rate REAL DEFAULT 5.0;")
    if "tax_amount" not in item_cols and len(item_cols) > 0:
        cursor.execute("ALTER TABLE sale_items ADD COLUMN tax_amount REAL DEFAULT 0.0;")

    # 4. Migrate sales table if it has obsolete CHECK(net_amount >= total_amount)
    sales_sql_row = cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='sales'").fetchone()
    if sales_sql_row and "net_amount >= total_amount" in sales_sql_row[0]:
        cursor.execute("PRAGMA foreign_keys = OFF;")
        cursor.execute("ALTER TABLE sales RENAME TO old_sales;")
        cursor.execute("""
        CREATE TABLE sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_no TEXT NOT NULL UNIQUE CHECK(invoice_no LIKE 'INV-%'),
            customer_name TEXT NOT NULL,
            customer_phone TEXT NOT NULL,
            total_amount REAL NOT NULL CHECK(total_amount >= 0.0),
            discount_amount REAL NOT NULL DEFAULT 0.0 CHECK(discount_amount >= 0.0),
            tax_amount REAL NOT NULL DEFAULT 0.0 CHECK(tax_amount >= 0.0),
            net_amount REAL NOT NULL CHECK(net_amount >= 0.0),
            payment_mode TEXT NOT NULL CHECK(payment_mode IN ('Cash', 'Card', 'UPI', 'NetBanking')),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)
        cursor.execute("""
        INSERT INTO sales (id, invoice_no, customer_name, customer_phone, total_amount, discount_amount, tax_amount, net_amount, payment_mode, created_at)
        SELECT id, invoice_no, customer_name, customer_phone, total_amount, COALESCE(discount_amount, 0.0), tax_amount, net_amount, payment_mode, created_at
        FROM old_sales;
        """)
        cursor.execute("DROP TABLE old_sales;")
        cursor.execute("PRAGMA foreign_keys = ON;")

    # 4b. Fix sale_items foreign key if it references old_sales
    items_sql_row = cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='sale_items'").fetchone()
    if items_sql_row and "old_sales" in items_sql_row[0]:
        cursor.execute("PRAGMA foreign_keys = OFF;")
        cursor.execute("ALTER TABLE sale_items RENAME TO old_sale_items;")
        cursor.execute("""
        CREATE TABLE sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL REFERENCES sales(id) ON DELETE CASCADE,
            medicine_id INTEGER NOT NULL REFERENCES medicines(id) ON DELETE RESTRICT,
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            unit_price REAL NOT NULL CHECK(unit_price >= 0.0),
            tax_rate REAL NOT NULL DEFAULT 5.0,
            tax_amount REAL NOT NULL DEFAULT 0.0,
            subtotal REAL NOT NULL CHECK(subtotal >= 0.0)
        );
        """)
        cursor.execute("""
        INSERT INTO sale_items (id, sale_id, medicine_id, quantity, unit_price, tax_rate, tax_amount, subtotal)
        SELECT id, sale_id, medicine_id, quantity, unit_price, COALESCE(tax_rate, 5.0), COALESCE(tax_amount, 0.0), subtotal
        FROM old_sale_items;
        """)
        cursor.execute("DROP TABLE old_sale_items;")
        cursor.execute("PRAGMA foreign_keys = ON;")

    # 5. Populate realistic EAN-13 barcodes on medicines lacking them
    med_rows = cursor.execute("SELECT id, name, batch_no FROM medicines WHERE barcode IS NULL OR barcode = ''").fetchall()
    for idx, row in enumerate(med_rows, 1):
        bcode = f"8901001001{idx:02d}"
        cursor.execute("UPDATE medicines SET barcode = ? WHERE id = ?", (bcode, row["id"]))

    # Ensure medicine 1 has standard benchmark barcode & batch
    cursor.execute("""
        UPDATE medicines 
        SET barcode = '890100100101', batch_no = 'BATCH-2026-001' 
        WHERE id = 1 AND (barcode IS NULL OR barcode = '' OR barcode = '890123400001');
    """)


def init_db(conn=None):
    """Initializes tables, indexes, immutability triggers, and runs migrations."""
    should_close = False
    if conn is None:
        conn = get_connection()
        should_close = True

    with conn:
        # 1. Categories
        conn.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 2. Certified Suppliers
        conn.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            contact_person TEXT NOT NULL,
            phone TEXT NOT NULL CHECK(length(phone) >= 10),
            email TEXT NOT NULL,
            address TEXT NOT NULL,
            drug_license TEXT NOT NULL UNIQUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 3. Medicines Inventory Master
        conn.execute("""
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            generic_name TEXT NOT NULL,
            category TEXT NOT NULL,
            dosage_form TEXT NOT NULL CHECK(dosage_form IN ('Tablet', 'Capsule', 'Syrup', 'Injection', 'Ointment', 'Drops', 'Inhaler', 'Suppository')),
            schedule_type TEXT NOT NULL DEFAULT 'OTC' CHECK(schedule_type IN ('OTC', 'Schedule H', 'Schedule H1', 'Schedule X')),
            batch_no TEXT NOT NULL CHECK(batch_no LIKE 'BATCH-%'),
            barcode TEXT,
            expiry_date TEXT NOT NULL CHECK(expiry_date GLOB '[0-9][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]'),
            purchase_price REAL NOT NULL CHECK(purchase_price >= 0.0),
            sale_price REAL NOT NULL CHECK(sale_price >= purchase_price),
            tax_rate REAL NOT NULL DEFAULT 5.0 CHECK(tax_rate IN (0.0, 5.0, 12.0, 18.0, 28.0)),
            stock_qty INTEGER NOT NULL CHECK(stock_qty >= 0),
            reorder_level INTEGER NOT NULL DEFAULT 15 CHECK(reorder_level >= 0),
            supplier_id INTEGER REFERENCES suppliers(id) ON DELETE RESTRICT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 4. Customers Master (For Automatic Patient Registration on POS Billing)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL UNIQUE CHECK(length(phone) >= 10),
            address TEXT,
            total_visits INTEGER DEFAULT 1,
            total_spent REAL DEFAULT 0.0,
            last_visit DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 5. Sales Invoices Header
        conn.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_no TEXT NOT NULL UNIQUE CHECK(invoice_no LIKE 'INV-%'),
            customer_name TEXT NOT NULL,
            customer_phone TEXT NOT NULL,
            total_amount REAL NOT NULL CHECK(total_amount >= 0.0),
            discount_amount REAL NOT NULL DEFAULT 0.0 CHECK(discount_amount >= 0.0),
            tax_amount REAL NOT NULL DEFAULT 0.0 CHECK(tax_amount >= 0.0),
            net_amount REAL NOT NULL CHECK(net_amount >= 0.0),
            payment_mode TEXT NOT NULL CHECK(payment_mode IN ('Cash', 'Card', 'UPI', 'NetBanking')),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 6. Sales Invoice Line Items
        conn.execute("""
        CREATE TABLE IF NOT EXISTS sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL REFERENCES sales(id) ON DELETE CASCADE,
            medicine_id INTEGER NOT NULL REFERENCES medicines(id) ON DELETE RESTRICT,
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            unit_price REAL NOT NULL CHECK(unit_price >= 0.0),
            tax_rate REAL NOT NULL DEFAULT 5.0,
            tax_amount REAL NOT NULL DEFAULT 0.0,
            subtotal REAL NOT NULL CHECK(subtotal >= 0.0)
        );
        """)

        # 7. Supplier Deals & Competitive Price Matrix (For Best Supplier Discount Comparison)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS supplier_deals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medicine_id INTEGER NOT NULL REFERENCES medicines(id) ON DELETE CASCADE,
            supplier_id INTEGER NOT NULL REFERENCES suppliers(id) ON DELETE CASCADE,
            mrp REAL NOT NULL,
            cost_price REAL NOT NULL,
            discount_percent REAL NOT NULL CHECK(discount_percent >= 0.0 AND discount_percent <= 100.0),
            delivery_days INTEGER DEFAULT 1,
            min_order_qty INTEGER DEFAULT 1,
            is_preferred INTEGER DEFAULT 0,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(medicine_id, supplier_id)
        );
        """)

        # 8. Q07 Feature 5: Immutable Audit Logs Table
        conn.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            action_type TEXT NOT NULL CHECK(action_type IN ('INSERT', 'UPDATE', 'DELETE', 'CHECKOUT')),
            table_name TEXT NOT NULL,
            record_id INTEGER NOT NULL,
            field_name TEXT,
            old_value TEXT,
            new_value TEXT,
            user_role TEXT NOT NULL DEFAULT 'Pharmacist'
        );
        """)

        # 9. SQC Defect Logs Table (Quality Control Checksheets)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS defect_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            defect_code TEXT NOT NULL CHECK(defect_code LIKE 'DEF-%'),
            defect_category TEXT NOT NULL,
            attempted_value TEXT NOT NULL,
            error_message TEXT NOT NULL,
            severity INTEGER NOT NULL CHECK(severity BETWEEN 1 AND 5)
        );
        """)

        # Triggers for Immutability and Audit Protection
        conn.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_prevent_audit_delete
        BEFORE DELETE ON audit_logs
        BEGIN
            SELECT RAISE(FAIL, 'TQM Policy Violation: Audit log entries are strictly immutable and cannot be deleted.');
        END;
        """)

        conn.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_prevent_audit_update
        BEFORE UPDATE ON audit_logs
        BEGIN
            SELECT RAISE(FAIL, 'TQM Policy Violation: Historical audit records cannot be altered.');
        END;
        """)

        conn.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_medicines_updated_at
        AFTER UPDATE ON medicines
        BEGIN
            UPDATE medicines SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END;
        """)

        # Execute column additions if database previously existed
        _run_migrations(conn)

    if should_close:
        conn.close()


def seed_db(conn=None):
    """Populates certified baseline categories, suppliers, medicines, supplier deals, and initial customers."""
    should_close = False
    if conn is None:
        conn = get_connection()
        should_close = True

    # Check if already seeded before opening a write transaction
    cursor = conn.execute("SELECT COUNT(*) AS cnt FROM medicines")
    if cursor.fetchone()["cnt"] > 0:
        # Check if supplier_deals need seeding
        deal_cnt = conn.execute("SELECT COUNT(*) AS cnt FROM supplier_deals").fetchone()["cnt"]
        if deal_cnt == 0:
            _seed_supplier_deals(conn)
        if should_close:
            conn.close()
        return

    with conn:
        # Seed Categories
        categories = [
            ("Antibiotic", "Anti-bacterial pharmaceutical agents for systemic infections"),
            ("Analgesic", "Pain relief and antipyretic formulations"),
            ("Antihistamine", "Anti-allergy and respiratory relief agents"),
            ("Antidiabetic", "Glycemic control and insulin regulators"),
            ("Cardiovascular", "Antihypertensive and lipid-lowering drugs"),
            ("Gastrointestinal", "Proton pump inhibitors and antacids"),
            ("Respiratory", "Bronchodilators and mucolytics"),
            ("Dermatological", "Topical ointments and skin barrier creams"),
        ]
        for name, desc in categories:
            conn.execute("INSERT OR IGNORE INTO categories (name, description) VALUES (?, ?)", (name, desc))

        # Seed Suppliers
        suppliers = [
            ("Apex Pharma Logistics Ltd", "Dr. Rajesh Sharma", "(800) 555-0199", "orders@apexpharma.com", "Industrial Estate Phase 2, New Delhi", "DL-DL-2024-00412"),
            ("MedSupply Global Distribution", "Ms. Sunita Verma", "(800) 555-0245", "supply@medsupplyglobal.com", "Logistics Hub, Sector 62, Noida", "DL-UP-2023-00981"),
            ("BioHealth Lifesciences Pvt", "Mr. Vikram Mehta", "(800) 555-0378", "contact@biohealth.in", "BioTech Park, Electronic City, Bengaluru", "DL-KA-2024-00122"),
            ("Sterling Healthcare Distributors", "Mr. Anand Kapoor", "(800) 555-0466", "sales@sterlinghealth.com", "Ring Road Warehouses, Mumbai", "DL-MH-2022-00567"),
        ]
        for s in suppliers:
            conn.execute("""
            INSERT OR IGNORE INTO suppliers (name, contact_person, phone, email, address, drug_license)
            VALUES (?, ?, ?, ?, ?, ?)
            """, s)

        # Retrieve supplier IDs
        sup_ids = [row["id"] for row in conn.execute("SELECT id FROM suppliers ORDER BY id").fetchall()]

        # Seed Benchmark Medicines
        future_base = date.today() + timedelta(days=400)
        meds = [
            ("Augmentin 625 Duo", "Amoxicillin + Clavulanic Acid", "Antibiotic", "Tablet", "Schedule H1", "BATCH-2026-001", "890100100101", (future_base + timedelta(days=120)).strftime("%Y-%m-%d"), 140.0, 185.0, 12.0, 120, 25, sup_ids[0]),
            ("Dolo 650", "Paracetamol", "Analgesic", "Tablet", "OTC", "BATCH-DOL02", "890100100102", (future_base + timedelta(days=240)).strftime("%Y-%m-%d"), 22.0, 31.5, 12.0, 350, 50, sup_ids[1]),
            ("Azithral 500", "Azithromycin", "Antibiotic", "Tablet", "Schedule H1", "BATCH-AZI03", "890100100103", (future_base + timedelta(days=180)).strftime("%Y-%m-%d"), 95.0, 125.0, 12.0, 80, 20, sup_ids[0]),
            ("Glycomet GP 1", "Metformin + Glimepiride", "Antidiabetic", "Tablet", "Schedule H", "BATCH-GLY04", "890100100104", (future_base + timedelta(days=300)).strftime("%Y-%m-%d"), 85.0, 112.0, 5.0, 150, 30, sup_ids[2]),
            ("Atorva 20", "Atorvastatin", "Cardiovascular", "Tablet", "Schedule H", "BATCH-ATO05", "890100100105", (future_base + timedelta(days=400)).strftime("%Y-%m-%d"), 160.0, 210.0, 5.0, 95, 20, sup_ids[2]),
            ("Pan 40", "Pantoprazole", "Gastrointestinal", "Tablet", "Schedule H", "BATCH-PAN06", "890100100106", (future_base + timedelta(days=210)).strftime("%Y-%m-%d"), 70.0, 98.0, 12.0, 200, 40, sup_ids[3]),
            ("Allegra 120", "Fexofenadine Hydrochloride", "Antihistamine", "Tablet", "Schedule H", "BATCH-ALL07", "890100100107", (future_base + timedelta(days=190)).strftime("%Y-%m-%d"), 145.0, 190.0, 12.0, 60, 15, sup_ids[1]),
            ("Ascoril LS Syrup", "Levosalbutamol + Ambroxol + Guaiphenesin", "Respiratory", "Syrup", "Schedule H", "BATCH-ASC08", "890100100108", (future_base + timedelta(days=90)).strftime("%Y-%m-%d"), 80.0, 108.0, 12.0, 45, 15, sup_ids[3]),
            ("Betadine 10% Ointment", "Povidone Iodine", "Dermatological", "Ointment", "OTC", "BATCH-BET09", "890100100109", (future_base + timedelta(days=320)).strftime("%Y-%m-%d"), 65.0, 88.0, 18.0, 75, 20, sup_ids[1]),
            ("Ciprogut 0.3% Eye Drops", "Ciprofloxacin", "Antibiotic", "Drops", "Schedule H", "BATCH-CIP10", "890100100110", (future_base + timedelta(days=150)).strftime("%Y-%m-%d"), 28.0, 42.0, 5.0, 90, 25, sup_ids[0]),
            ("Combiflam", "Ibuprofen + Paracetamol", "Analgesic", "Tablet", "OTC", "BATCH-COM11", "890100100111", (future_base + timedelta(days=270)).strftime("%Y-%m-%d"), 26.0, 37.0, 12.0, 240, 40, sup_ids[1]),
            ("Monocef 1g Injection", "Ceftriaxone", "Antibiotic", "Injection", "Schedule H1", "BATCH-MON12", "890100100112", (future_base + timedelta(days=110)).strftime("%Y-%m-%d"), 48.0, 65.0, 5.0, 30, 10, sup_ids[0]),
        ]

        for m in meds:
            cursor = conn.execute("""
            INSERT INTO medicines (
                name, generic_name, category, dosage_form, schedule_type,
                batch_no, barcode, expiry_date, purchase_price, sale_price, tax_rate, stock_qty,
                reorder_level, supplier_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, m)
            med_id = cursor.lastrowid
            conn.execute("""
            INSERT INTO audit_logs (action_type, table_name, record_id, field_name, old_value, new_value, user_role)
            VALUES ('INSERT', 'medicines', ?, 'all_fields', NULL, ?, 'System Initializer')
            """, (med_id, f"Initial catalog creation for {m[0]}"))

        # Seed initial returning customers
        conn.execute("""
        INSERT OR IGNORE INTO customers (name, phone, address, total_visits, total_spent)
        VALUES ('Ramesh Patel', '(987) 654-3210', 'Block C, Vasant Kunj, New Delhi', 4, 1845.50)
        """)
        conn.execute("""
        INSERT OR IGNORE INTO customers (name, phone, address, total_visits, total_spent)
        VALUES ('Priya Sharma', '(982) 345-6789', 'Pocket 2, Sector 14, Dwarka', 2, 730.00)
        """)

        # Seed supplier deals for procurement comparison
        _seed_supplier_deals(conn)

    if should_close:
        conn.close()


def _seed_supplier_deals(conn):
    """Populates competitive supplier quotes and discounts for each medicine."""
    with conn:
        med_rows = conn.execute("SELECT id, name, sale_price, purchase_price, supplier_id FROM medicines").fetchall()
        sup_rows = conn.execute("SELECT id FROM suppliers").fetchall()
        sup_ids = [r["id"] for r in sup_rows]

        if not sup_ids:
            return

        import random
        random.seed(42)  # Deterministic seed for reproducible testing

        for med in med_rows:
            mrp = med["sale_price"]
            base_cost = med["purchase_price"]

            for idx, sid in enumerate(sup_ids):
                # Vary discounts across suppliers: e.g. 15% to 28% off MRP
                discount_pct = round(random.uniform(16.0, 27.5), 1)
                cost_from_discount = round(mrp * (1.0 - discount_pct / 100.0), 2)
                cost = min(cost_from_discount, round(mrp * 0.85, 2))
                delivery = random.choice([1, 2, 3])
                min_qty = random.choice([5, 10, 20])
                is_pref = 1 if sid == med["supplier_id"] else 0

                conn.execute("""
                INSERT OR REPLACE INTO supplier_deals (
                    medicine_id, supplier_id, mrp, cost_price, discount_percent,
                    delivery_days, min_order_qty, is_preferred
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (med["id"], sid, mrp, cost, discount_pct, delivery, min_qty, is_pref))


if __name__ == "__main__":
    init_db()
    seed_db()
    print("Database initialized and seeded successfully at:", DB_PATH)

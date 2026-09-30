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


def init_db(conn=None):
    """Initializes tables, indexes, and immutability triggers."""
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
            expiry_date TEXT NOT NULL CHECK(expiry_date GLOB '[0-9][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]'),
            purchase_price REAL NOT NULL CHECK(purchase_price >= 0.0),
            sale_price REAL NOT NULL CHECK(sale_price >= purchase_price),
            stock_qty INTEGER NOT NULL CHECK(stock_qty >= 0),
            reorder_level INTEGER NOT NULL DEFAULT 15 CHECK(reorder_level >= 0),
            supplier_id INTEGER REFERENCES suppliers(id) ON DELETE RESTRICT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 4. Sales Invoices Header
        conn.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_no TEXT NOT NULL UNIQUE CHECK(invoice_no LIKE 'INV-%'),
            customer_name TEXT NOT NULL,
            customer_phone TEXT NOT NULL,
            total_amount REAL NOT NULL CHECK(total_amount >= 0.0),
            tax_amount REAL NOT NULL DEFAULT 0.0 CHECK(tax_amount >= 0.0),
            net_amount REAL NOT NULL CHECK(net_amount >= total_amount),
            payment_mode TEXT NOT NULL CHECK(payment_mode IN ('Cash', 'Card', 'UPI', 'NetBanking')),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 5. Sales Invoice Line Items
        conn.execute("""
        CREATE TABLE IF NOT EXISTS sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL REFERENCES sales(id) ON DELETE CASCADE,
            medicine_id INTEGER NOT NULL REFERENCES medicines(id) ON DELETE RESTRICT,
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            unit_price REAL NOT NULL CHECK(unit_price >= 0.0),
            subtotal REAL NOT NULL CHECK(subtotal >= 0.0)
        );
        """)

        # 6. Q07 Feature 5: Immutable Audit Logs Table
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

        # 7. SQC Defect Logs Table (Quality Control Checksheets)
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

    if should_close:
        conn.close()


def seed_db(conn=None):
    """Populates certified baseline categories, suppliers, and benchmark medicines."""
    should_close = False
    if conn is None:
        conn = get_connection()
        should_close = True

    # Check if already seeded before opening a write transaction
    cursor = conn.execute("SELECT COUNT(*) AS cnt FROM medicines")
    if cursor.fetchone()["cnt"] > 0:
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

        # Seed Medicines with standard formatting
        future_base = date.today() + timedelta(days=365)
        meds = [
            ("Augmentin 625 Duo", "Amoxicillin + Clavulanic Acid", "Antibiotic", "Tablet", "Schedule H1", "BATCH-AUG01", (future_base + timedelta(days=120)).strftime("%Y-%m-%d"), 140.0, 185.0, 120, 25, sup_ids[0]),
            ("Dolo 650", "Paracetamol", "Analgesic", "Tablet", "OTC", "BATCH-DOL02", (future_base + timedelta(days=240)).strftime("%Y-%m-%d"), 22.0, 31.5, 350, 50, sup_ids[1]),
            ("Azithral 500", "Azithromycin", "Antibiotic", "Tablet", "Schedule H1", "BATCH-AZI03", (future_base + timedelta(days=180)).strftime("%Y-%m-%d"), 95.0, 125.0, 80, 20, sup_ids[0]),
            ("Glycomet GP 1", "Metformin + Glimepiride", "Antidiabetic", "Tablet", "Schedule H", "BATCH-GLY04", (future_base + timedelta(days=300)).strftime("%Y-%m-%d"), 85.0, 112.0, 150, 30, sup_ids[2]),
            ("Atorva 20", "Atorvastatin", "Cardiovascular", "Tablet", "Schedule H", "BATCH-ATO05", (future_base + timedelta(days=400)).strftime("%Y-%m-%d"), 160.0, 210.0, 95, 20, sup_ids[2]),
            ("Pan 40", "Pantoprazole", "Gastrointestinal", "Tablet", "Schedule H", "BATCH-PAN06", (future_base + timedelta(days=210)).strftime("%Y-%m-%d"), 70.0, 98.0, 200, 40, sup_ids[3]),
            ("Allegra 120", "Fexofenadine Hydrochloride", "Antihistamine", "Tablet", "Schedule H", "BATCH-ALL07", (future_base + timedelta(days=190)).strftime("%Y-%m-%d"), 145.0, 190.0, 60, 15, sup_ids[1]),
            ("Ascoril LS Syrup", "Levosalbutamol + Ambroxol + Guaiphenesin", "Respiratory", "Syrup", "Schedule H", "BATCH-ASC08", (future_base + timedelta(days=90)).strftime("%Y-%m-%d"), 80.0, 108.0, 45, 15, sup_ids[3]),
            ("Betadine 10% Ointment", "Povidone Iodine", "Dermatological", "Ointment", "OTC", "BATCH-BET09", (future_base + timedelta(days=320)).strftime("%Y-%m-%d"), 65.0, 88.0, 75, 20, sup_ids[1]),
            ("Ciprogut 0.3% Eye Drops", "Ciprofloxacin", "Antibiotic", "Drops", "Schedule H", "BATCH-CIP10", (future_base + timedelta(days=150)).strftime("%Y-%m-%d"), 28.0, 42.0, 90, 25, sup_ids[0]),
            ("Combiflam", "Ibuprofen + Paracetamol", "Analgesic", "Tablet", "OTC", "BATCH-COM11", (future_base + timedelta(days=270)).strftime("%Y-%m-%d"), 26.0, 37.0, 240, 40, sup_ids[1]),
            ("Monocef 1g Injection", "Ceftriaxone", "Antibiotic", "Injection", "Schedule H1", "BATCH-MON12", (future_base + timedelta(days=110)).strftime("%Y-%m-%d"), 48.0, 65.0, 30, 10, sup_ids[0]),
        ]

        for m in meds:
            cursor = conn.execute("""
            INSERT INTO medicines (
                name, generic_name, category, dosage_form, schedule_type,
                batch_no, expiry_date, purchase_price, sale_price, stock_qty,
                reorder_level, supplier_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, m)
            med_id = cursor.lastrowid
            # Seed audit log for initial baseline insertion
            conn.execute("""
            INSERT INTO audit_logs (action_type, table_name, record_id, field_name, old_value, new_value, user_role)
            VALUES ('INSERT', 'medicines', ?, 'all_fields', NULL, ?, 'System Initializer')
            """, (med_id, f"Initial catalog creation for {m[0]}"))

    if should_close:
        conn.close()


if __name__ == "__main__":
    init_db()
    seed_db()
    print("Database initialized and seeded successfully at:", DB_PATH)

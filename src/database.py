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



# SQLite Relational Database Schema & Constraint Matrix
## Pharmacy Management System - [Q07: Improve Data Accuracy]
### Course: BBAT104 - Fundamentals of TQM | Academic Session: 2026–27
**Author:** Anmol Joshi (Roll No: 2410302004, Branch: CSE-B)

---

## 1. Database Design Philosophy
The database layer serves as the ultimate line of defense for data accuracy (Poka-Yoke). Beyond application-level input masks, the relational schema enforces structural integrity through **CHECK constraints**, **FOREIGN KEY cascades**, **UNIQUE indexes**, and **immutable audit triggers**.

---

## 2. Complete Data Definition Language (DDL) Script

```sql
-- Enable Foreign Key Constraint Enforcement
PRAGMA foreign_keys = ON;

-- 1. Therapeutic Categories Table
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Certified Suppliers Table
CREATE TABLE IF NOT EXISTS suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    contact_person TEXT NOT NULL,
    phone TEXT NOT NULL CHECK(length(phone) >= 10),
    email TEXT NOT NULL CHECK(email LIKE '%_@__%.__%'),
    address TEXT NOT NULL,
    drug_license TEXT NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 3. Medicines Inventory Master Table
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

-- 4. Sales Invoices Header Table
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

-- 5. Sales Invoice Line Items Table
CREATE TABLE IF NOT EXISTS sale_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_id INTEGER NOT NULL REFERENCES sales(id) ON DELETE CASCADE,
    medicine_id INTEGER NOT NULL REFERENCES medicines(id) ON DELETE RESTRICT,
    quantity INTEGER NOT NULL CHECK(quantity > 0),
    unit_price REAL NOT NULL CHECK(unit_price >= 0.0),
    subtotal REAL NOT NULL CHECK(subtotal >= 0.0)
);

-- 6. Q07 Feature 5: Immutable Audit Logs Table
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

-- 7. SQC Defect Logs Table (Quality Control Checksheets)
CREATE TABLE IF NOT EXISTS defect_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    defect_code TEXT NOT NULL CHECK(defect_code LIKE 'DEF-%'),
    defect_category TEXT NOT NULL,
    attempted_value TEXT NOT NULL,
    error_message TEXT NOT NULL,
    severity INTEGER NOT NULL CHECK(severity BETWEEN 1 AND 5)
);
```

---

## 3. Schema Security & Immutability Triggers

To uphold the TQM principle of **Fact-Based Decision Making** and prevent retrospective tampering:

```sql
-- Trigger: Prevent DELETE operations on audit_logs
CREATE TRIGGER IF NOT EXISTS trg_prevent_audit_delete
BEFORE DELETE ON audit_logs
BEGIN
    SELECT RAISE(FAIL, 'TQM Policy Violation: Audit log entries are strictly immutable and cannot be deleted.');
END;

-- Trigger: Prevent UPDATE operations on audit_logs
CREATE TRIGGER IF NOT EXISTS trg_prevent_audit_update
BEFORE UPDATE ON audit_logs
BEGIN
    SELECT RAISE(FAIL, 'TQM Policy Violation: Historical audit records cannot be altered.');
END;

-- Trigger: Automatically update timestamp on medicine modifications
CREATE TRIGGER IF NOT EXISTS trg_medicines_updated_at
AFTER UPDATE ON medicines
BEGIN
    UPDATE medicines SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
```

---

## 4. Integrity Constraint Matrix

| Constraint Identifier | Target Entity / Attribute | Rule Logic | Poka-Yoke Purpose |
| :--- | :--- | :--- | :--- |
| `CHK_MED_PRICE` | `medicines.sale_price` | `sale_price >= purchase_price` | Prevents dispensing drugs at an unintended loss |
| `CHK_MED_STOCK` | `medicines.stock_qty` | `stock_qty >= 0` | Physically prohibits negative stock balances |
| `CHK_MED_DATE` | `medicines.expiry_date` | `GLOB '[0-9]{4}-[0-9]{2}-[0-9]{2}'` | Eliminates date formatting ambiguity |
| `CHK_MED_FORM` | `medicines.dosage_form` | Explicit Enum membership | Eradicates spelling errors in dosage classes |
| `CHK_MED_BATCH` | `medicines.batch_no` | `LIKE 'BATCH-%'` | Enforces manufacturer batch tracking consistency |
| `FK_SALE_MED` | `sale_items.medicine_id`| `REFERENCES medicines(id)` | Prohibits selling non-cataloged drugs |
| `TRG_AUDIT_LOCK`| `audit_logs` | Block `UPDATE` & `DELETE` | Guarantees legally admissible data trail |

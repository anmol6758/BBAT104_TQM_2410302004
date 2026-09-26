# Software Requirements Specification (SRS)
## Pharmacy Management System - [Q07: Improve Data Accuracy]
### Course: BBAT104 - Fundamentals of TQM | Academic Session: 2026–27
**Author:** Anmol Joshi (Roll No: 2410302004, Branch: CSE-B)

---

## 1. INTRODUCTION

### 1.1 Purpose
This Software Requirements Specification (SRS) document details the functional, non-functional, domain-specific, and quality assurance requirements for the **Pharmacy Management System - [Q07: Improve Data Accuracy]**. The primary objective is to engineer a dependable, error-proofed pharmaceutical inventory, sales dispensing, and audit management platform governed by Total Quality Management (TQM) principles.

### 1.2 Document Scope
This document covers:
- System boundaries spanning procurement, batch inventory, dispensing, and transaction auditing.
- Implementation specifications for the assigned **Q07 Quality Goal (Improve Data Accuracy)**.
- Integration requirements for Poka-Yoke mistake proofing, automated audit trails, and Statistical Quality Control (SQC) modules.
- Verification and acceptance criteria for Review 1 through Review 4.

### 1.3 Definitions, Acronyms, and Abbreviations
- **TQM:** Total Quality Management
- **Q07:** Quality Goal 07 - Improve Data Accuracy
- **Poka-Yoke:** A Japanese quality control concept meaning "mistake-proofing" or "inadvertent error prevention"
- **FMEA:** Failure Mode and Effects Analysis
- **RPN:** Risk Priority Number ($RPN = \text{Severity} \times \text{Occurrence} \times \text{Detection}$)
- **SIPOC:** Suppliers, Inputs, Process, Outputs, Customers mapping
- **CTQ:** Critical to Quality
- **PDCA:** Plan-Do-Check-Act iterative continuous improvement cycle
- **CRUD:** Create, Read, Update, Delete database transactions
- **LASA:** Look-Alike / Sound-Alike medications
- **SKU:** Stock Keeping Unit / Medicine Identification Code

### 1.4 References
- IEEE Std 830-1998: *Recommended Practice for Software Requirements Specifications*.
- ISO 9001:2015: *Quality Management Systems — Requirements*.
- BBAT104 Course Project Guidelines, Allotment & Marking Scheme (Session 2026–27).
- WHO Good Pharmacy Practice (GPP) Standards for Data Integrity and Patient Safety.

### 1.5 System Overview
The software provides a desktop GUI interface built in Python with Tkinter and SQLite3. Beyond standard inventory and billing functionalities, the system embeds five specialized Poka-Yoke data accuracy mechanisms:
1. Hardened input masks for format conformance.
2. Controlled drop-down selections to prevent arbitrary string inputs.
3. Live auto-complete search to eradicate nomenclature typos.
4. Two-step confirmation modals before state-altering transactions.
5. Tamper-evident automated audit logs capturing every row-level mutation.

---

## 2. OVERALL SYSTEM DESCRIPTION

### 2.1 Product Perspective
The Pharmacy Management System operates as an autonomous, self-contained desktop information system designed for community and hospital retail pharmacies. It directly interacts with a local, ACID-compliant relational SQLite database (`pharmacy.db`) and exports reports/charts in PNG and CSV formats.

```
+-------------------------------------------------------------------+
|               Pharmacy Management System (GUI Layer)             |
|   [Inventory Management]  [Billing & Dispense]  [Audit & QC View]  |
+---------------------------------+---------------------------------+
                                  |
               [Q07 Data Accuracy & Poka-Yoke Layer]
      - Input Masking Engine       - Pre-validated Dropdown Lists
      - Real-time Auto-Complete    - Delta Confirmation Modals
      - Automated Audit Logger     - Defect Interception Engine
                                  |
+---------------------------------+---------------------------------+
|               SQLite3 ACID Persistence Engine                     |
|  [medicines]   [categories]   [suppliers]   [sales]   [audit_logs] |
+-------------------------------------------------------------------+
```

### 2.2 Product Functions
1. **Inventory Management (CRUD):** Catalog medicines with brand name, generic salt, batch number, expiry date, category, manufacturer, unit purchase price, unit sale price, reorder threshold, and quantity in stock.
2. **Sales & Dispensing (Billing):** Select medicines via auto-complete, validate stock sufficiency, compute line-item totals, apply tax brackets, deduct inventory atomically, and generate receipts.
3. **Poka-Yoke Data Accuracy (Q07):** Active interceptors preventing invalid dates, negative stock entries, mismatched drug schedules, and unformatted batch codes.
4. **Audit Trail & Traceability:** Immutable historical logging of all database modifications with timestamps and before/after values.
5. **Quality Metrics & SQC Reporting:** Real-time generation of defect checksheets, Pareto 80/20 analysis charts, and Ishikawa root-cause diagrams.

### 2.3 User Classes and Characteristics
- **Chief Pharmacist (Admin):** Manages medicine catalogs, updates prices, reviews audit logs, oversees SQC reports, and authorizes stock write-offs. High technical and pharmaceutical competence.
- **Dispensing Clerk / Cashier:** Conducts daily counter sales, adds customer details, prints invoices, and reviews stock alerts. Requires an intuitive, mistake-proofed interface to prevent fast-paced counter errors.
- **Inventory Controller:** Enters incoming supplier batches, validates expiry dates, performs physical-to-digital reconciliations.
- **Academic / TQM Quality Auditor:** Evaluates system compliance against FMEA models, inspects RPN reduction, reviews checksheets, and audits Git commits.

### 2.4 Operating Environment
- **Operating System:** Windows 10 / Windows 11 (tested on Windows 64-bit).
- **Runtime Environment:** Python 3.10+ (Current runtime: Python 3.14).
- **GUI Framework:** Standard Tkinter / TTK styling.
- **Database Engine:** Embedded SQLite 3.x with Foreign Key support enabled.
- **Reporting Dependencies:** Matplotlib 3.10+, Pandas 2.2+, NumPy 2.0+, Pillow 11.0+.

### 2.5 Design and Implementation Constraints
- **Zero Third-Party Database Servers:** Must run self-contained on SQLite without requiring network database daemon configuration.
- **Real-Time Responsiveness:** Auto-complete search latencies must not exceed 50ms for smooth typing.
- **Strict Data Validation:** Free-text fields must be restricted to non-critical descriptions; all medical and pricing fields must be strictly typed and masked.
- **Immutable Audit Trail:** Deleting an audit record is programmatically prohibited at the database schema level.

### 2.6 Assumptions and Dependencies
- The local host machine possesses write permissions in the application directory for SQLite database storage and chart rendering.
- A single cashier/pharmacist accesses the local desktop station concurrently.

---

## 3. SPECIFIC FUNCTIONAL REQUIREMENTS & DATA DICTIONARY

### 3.1 Functional Requirements Specification

#### 3.1.1 Inventory & Medicine Master CRUD Module
- **FR-01 (Create Medicine):** The system shall allow authorized users to register new pharmaceutical products with mandatory fields: Brand Name, Generic Salt, Category, Dosage Form, Batch Number, Expiry Date, Purchase Price, Sale Price, Current Stock, Reorder Level, and Supplier.
- **FR-02 (Read Medicine Catalog):** The system shall display inventory items in a sortable, paginated data grid with color-coded alerts for low stock ($\le \text{reorder level}$) and imminent expiry ($\le 90\text{ days}$).
- **FR-03 (Update Medicine):** The system shall permit updates to medicine pricing, supplier, and stock quantities, requiring confirmation for deviations exceeding 20% of previous values.
- **FR-04 (Delete Medicine):** The system shall prevent hard deletions of medicines linked to prior sales records (referential integrity enforcement) and require an explicit confirmation modal before soft-deactivating records.

#### 3.1.2 Q07 Data Accuracy & Poka-Yoke Modules
- **FR-05 (Input Masking Engine):**
  - **FR-05.1:** Expiry dates shall be automatically formatted and validated against pattern `YYYY-MM-DD` and must represent a date strictly in the future.
  - **FR-05.2:** Batch numbers shall adhere to format `BATCH-[A-Z0-9]{5}` to avoid clerical variance.
  - **FR-05.3:** Customer/Supplier telephone numbers shall adhere to standard 10-digit masked pattern `(XXX) XXX-XXXX`.
  - **FR-05.4:** Currency entries must conform to non-negative 2-decimal floats (`0.00`).
- **FR-06 (Restricted Dropdown Lists):**
  - **FR-06.1:** Dosage forms must be selected strictly from predefined values: `Tablet`, `Capsule`, `Syrup`, `Injection`, `Ointment`, `Drops`, `Inhaler`, `Suppository`.
  - **FR-06.2:** Drug schedules must be chosen from: `Over-the-Counter (OTC)`, `Schedule H (Prescription Only)`, `Schedule H1 (Narcotic/Antibiotic)`, `Schedule X`.
  - **FR-06.3:** Suppliers must be selected from active verified supplier records.
- **FR-07 (Dynamic Auto-Complete Search):**
  - **FR-07.1:** The billing and search interfaces shall offer dynamic auto-complete popup lists upon typing $\ge 2$ characters.
  - **FR-07.2:** Auto-complete shall query across both Brand Trade Names (e.g., *Augmentin 625*) and Active Generic Salts (e.g., *Amoxicillin + Clavulanic Acid*).
- **FR-08 (Two-Stage Confirmation Modals):**
  - **FR-08.1:** Before executing any destructive deletion or major price change, a modal dialog must display the entity name, old values, new values, and require explicit confirmation.
  - **FR-08.2:** During invoice generation, a confirmation modal shall show bill summary, total items, discount, net amount, and inventory deduction breakdown before finalizing.
- **FR-09 (Automated Immutable Audit Logging):**
  - **FR-09.1:** The system shall automatically record every row insert, update, or deletion in the `audit_logs` table.
  - **FR-09.2:** Log entries must record `log_id`, `timestamp`, `action_type`, `table_affected`, `record_id`, `field_name`, `old_value`, `new_value`, and `user_role`.

#### 3.1.3 Billing & Point of Sale (POS) Module
- **FR-10 (Cart Building & Stock Validation):** The system shall prohibit adding quantities greater than available inventory and shall alert the user immediately.
- **FR-11 (Invoice Generation & Atomic Stock Deduction):** On confirmed checkout, the system shall atomically record the sale, insert sale line items, decrement stock in `medicines`, and log the transactions in the audit trail within a single atomic database transaction.

#### 3.1.4 Statistical Quality Control (SQC) Module
- **FR-12 (Defect Checksheet Recording):** The system shall maintain an event log of rejected inputs, validation failures, and operational data anomalies.
- **FR-13 (Pareto 80/20 Generation):** The system shall aggregate defect counts by category and generate a Pareto chart displaying frequency bars and cumulative percentage curves.
- **FR-14 (Ishikawa Fishbone Generation):** The system shall programmatically render a cause-and-effect fishbone diagram mapping root causes across People, Process, Software Code, Machine, and Environment.

---

### 3.2 Data Dictionary

#### 3.2.1 Table: `medicines`
| Attribute | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique internal medicine identifier |
| `name` | TEXT | NOT NULL, UNIQUE | Commercial/Brand name of medicine |
| `generic_name` | TEXT | NOT NULL | Active pharmaceutical ingredient/salt |
| `category` | TEXT | NOT NULL | Therapeutic category (e.g., Antibiotic, Analgesic) |
| `dosage_form` | TEXT | NOT NULL | Form (Tablet, Syrup, Injection, etc.) |
| `schedule_type` | TEXT | NOT NULL DEFAULT 'OTC' | Regulatory schedule (OTC, Schedule H, H1, X) |
| `batch_no` | TEXT | NOT NULL | Manufacturer batch identifier (`BATCH-XXXXX`) |
| `expiry_date` | TEXT | NOT NULL | Expiry date formatted as `YYYY-MM-DD` |
| `purchase_price`| REAL | NOT NULL, CHECK(`purchase_price` >= 0) | Wholesale cost price per unit |
| `sale_price` | REAL | NOT NULL, CHECK(`sale_price` >= `purchase_price`) | Retail price charged to customer |
| `stock_qty` | INTEGER | NOT NULL, CHECK(`stock_qty` >= 0) | Quantity available in inventory |
| `reorder_level` | INTEGER | NOT NULL DEFAULT 15 | Threshold below which alert triggers |
| `supplier_id` | INTEGER | REFERENCES `suppliers`(`id`) | Foreign key linking to supplier |
| `created_at` | TEXT | DEFAULT CURRENT_TIMESTAMP | Timestamp of initial record creation |
| `updated_at` | TEXT | DEFAULT CURRENT_TIMESTAMP | Timestamp of latest record update |

#### 3.2.2 Table: `suppliers`
| Attribute | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique supplier identifier |
| `name` | TEXT | NOT NULL, UNIQUE | Registered supplier/distributor firm name |
| `contact_person`| TEXT | NOT NULL | Authorized sales representative name |
| `phone` | TEXT | NOT NULL | Formatted telephone number `(XXX) XXX-XXXX` |
| `email` | TEXT | NOT NULL | Valid electronic mail address |
| `address` | TEXT | NOT NULL | Warehouse / business physical location |
| `drug_license` | TEXT | NOT NULL, UNIQUE | Statutory Drug License Number |

#### 3.2.3 Table: `sales`
| Attribute | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique sales invoice number |
| `invoice_no` | TEXT | NOT NULL, UNIQUE | Formatted serial invoice code (`INV-YYYYMMDD-XXXX`) |
| `customer_name` | TEXT | NOT NULL | Name of purchasing patient/customer |
| `customer_phone`| TEXT | NOT NULL | Contact telephone number |
| `total_amount` | REAL | NOT NULL | Gross total of all line items |
| `tax_amount` | REAL | NOT NULL DEFAULT 0.0 | Calculated GST / Sales Tax amount |
| `net_amount` | REAL | NOT NULL | Final billable amount payable |
| `payment_mode` | TEXT | NOT NULL | Payment method (`Cash`, `Card`, `UPI`, `NetBanking`) |
| `created_at` | TEXT | DEFAULT CURRENT_TIMESTAMP | Date and time invoice was executed |

#### 3.2.4 Table: `sale_items`
| Attribute | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique sale item entry ID |
| `sale_id` | INTEGER | NOT NULL, REFERENCES `sales`(`id`) | Foreign key linking to parent sale |
| `medicine_id` | INTEGER | NOT NULL, REFERENCES `medicines`(`id`) | Foreign key linking to dispensed medicine |
| `quantity` | INTEGER | NOT NULL, CHECK(`quantity` > 0) | Number of units sold |
| `unit_price` | REAL | NOT NULL | Unit sale price charged at time of sale |
| `subtotal` | REAL | NOT NULL | Subtotal computed as (`quantity` $\times$ `unit_price`) |

#### 3.2.5 Table: `audit_logs` (Q07 Dedicated Table)
| Attribute | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Monotonically increasing audit log ID |
| `timestamp` | TEXT | DEFAULT CURRENT_TIMESTAMP | Exact UTC timestamp of database mutation |
| `action_type` | TEXT | NOT NULL | `INSERT`, `UPDATE`, `DELETE`, `CHECKOUT` |
| `table_name` | TEXT | NOT NULL | Table affected (`medicines`, `suppliers`, `sales`) |
| `record_id` | INTEGER | NOT NULL | Primary key of affected row |
| `field_name` | TEXT | NULLABLE | Specific column altered (for updates) |
| `old_value` | TEXT | NULLABLE | Prior stored value |
| `new_value` | TEXT | NULLABLE | New updated value |
| `user_role` | TEXT | NOT NULL DEFAULT 'Pharmacist' | System operator performing the action |

#### 3.2.6 Table: `defect_logs` (SQC Tracking Table)
| Attribute | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Defect event identifier |
| `timestamp` | TEXT | DEFAULT CURRENT_TIMESTAMP | Event recording time |
| `defect_code` | TEXT | NOT NULL | Standard classification code (`DEF-01` to `DEF-08`) |
| `defect_category`| TEXT | NOT NULL | Defect family (e.g., `Format Mismatch`, `Bounds Violation`) |
| `attempted_value`| TEXT | NOT NULL | Bad input value intercepted by Poka-Yoke |
| `error_message` | TEXT | NOT NULL | System alert message presented to user |
| `severity` | INTEGER | NOT NULL CHECK(`severity` BETWEEN 1 AND 5) | Operational risk ranking (1=Minor to 5=Critical) |

---


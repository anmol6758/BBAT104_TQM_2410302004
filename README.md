# Pharmacy Management System - [Q07: Improve Data Accuracy]
### Course: BBAT104: Fundamentals of Total Quality Management (TQM)
**Academic Session:** 2026–2027 | **Current Milestone:** Review 2 (Base System & CRUD + 5 Quality Goal Features)  
**Author:** Anmol Joshi  
**University Roll Number:** 2410302004  
**Branch & Section:** Computer Science & Engineering (CSE) | Section B  
**Allotted Baseline Project:** Pharmacy Management System  
**Sequential Quality Goal:** Q07 - Improve Data Accuracy  

---

## 📌 Executive Summary & Progress (Review 1 & Review 2)
This project delivers a desktop pharmaceutical inventory, sales dispensing, and quality assurance system engineered in Python (Tkinter + SQLite3). Governed by **Total Quality Management (TQM)** principles—specifically **Poka-Yoke (mistake-proofing)**, **Juran's Quality by Design**, and **Deming's PDCA Continuous Improvement cycle**—the software guarantees zero defect propagation at the point of data entry.

```
+--------------------------------------------------------------------------------------------------+
|                                    REVIEW 2 MILESTONE HIGHLIGHTS                                 |
|  • Base System & CRUD: Fully functional desktop UI with SQLite relational database               |
|  • Q07 Feature 1 (Input Masking): Auto-formatting for Expiry (YYYY-MM-DD), Batch, and Phone      |
|  • Q07 Feature 2 (Dropdown Lists): Locked clinical selections for Dosage Forms and Schedules     |
|  • Q07 Feature 3 (Auto-Complete): Real-time Brand Name & Generic Chemical Salt cross-search      |
|  • Q07 Feature 4 (Confirmation Modals): Two-step verification displaying delta previews          |
|  • Q07 Feature 5 (Audit Logs): Immutable SQLite trigger-protected audit logging                  |
|  • Visual Design: Modern clean typography (Trebuchet MS headers & Calibri data grids)            |
|  • Git Health: Exactly 16 structured commits (8 for Review 1 + 8 for Review 2)                   |
+--------------------------------------------------------------------------------------------------+
```

---

## 🛡️ The 5 Assigned Q07 Quality Features in Action

1. **Input Masking (Poka-Yoke Format Enforcement):**
   - **Expiry Dates:** Strictly auto-formatted to `YYYY-MM-DD` via `MaskedDateEntry`. Algorithmic locks physically block dates in the past (<= Today).
   - **Batch Numbers:** Strictly auto-formatted to `BATCH-[A-Z0-9]{3,12}` via `MaskedBatchEntry`, automatically forcing uppercase characters.
   - **Telephone Numbers:** Formatted to `(XXX) XXX-XXXX` on keystroke.
   - **Financial Bounds:** Rejects negative prices and enforces `Retail Sale Price >= Wholesale Cost Price`.

2. **Dropdown Lists (Boundary & Enum Constraints):**
   - Eliminates clerical spelling typos in clinical formulations.
   - Restricts entries to pre-validated dropdown selections:
     - *Dosage Forms:* `Tablet`, `Capsule`, `Syrup`, `Injection`, `Ointment`, `Drops`, `Inhaler`, `Suppository`.
     - *Drug Schedules:* `OTC`, `Schedule H (Prescription Only)`, `Schedule H1 (Narcotic/Antibiotic)`, `Schedule X`.
     - *Therapeutic Categories:* `Antibiotic`, `Analgesic`, `Antihistamine`, `Antidiabetic`, `Cardiovascular`, etc.

3. **Dynamic Auto-Complete (Look-Alike / Sound-Alike LASA Error Prevention):**
   - Powered by `AutoCompleteEntry` querying SQLite in real-time (<= 5 ms).
   - Cross-queries both **Commercial Brand Names** (e.g., *Augmentin 625 Duo*) and **Active Generic Chemical Salts** (e.g., *Amoxicillin + Clavulanic Acid*), preventing fatal drug substitution errors.

4. **Delta Confirmation Modals (Two-Step Verification Gates):**
   - Powered by `ConfirmationModal`. Before committing modifications to an existing medicine record, the system displays a side-by-side inspection grid comparing **Previous Value** vs. **Proposed Value**.
   - Medicine deletion and sales checkout are gated behind multi-parameter confirmation dialogs showing exact financial and inventory impacts.

5. **Immutable Audit Logs (Total Process Traceability):**
   - Every transaction (`INSERT`, `UPDATE`, `DELETE`, `CHECKOUT`) writes an unalterable log record to `audit_logs` storing timestamp, user role, table, record ID, and old vs. new values.
   - SQLite schema triggers (`trg_prevent_audit_delete` and `trg_prevent_audit_update`) abort any SQL attempts to delete or modify historical logs.
   - Dedicated GUI Audit Trail tab with search filters and CSV export.

---

## 🚀 How to Launch the Application
```powershell
# Install requirements (if not already installed)
pip install -r requirements.txt

# Run the Desktop Application
python src/app.py
```

---

## 🗂️ Project Repository Structure

```
d:/TQM Project/
├── .gitignore                                 # Configured for Python, IDE, and SQLite runtime
├── requirements.txt                           # matplotlib, pandas, numpy, pillow
├── README.md                                  # Project overview and Review 2 documentation
├── data/
│   └── pharmacy.db                            # SQLite relational database (WAL mode enabled)
├── docs/
│   ├── PROJECT_CHARTER.md                     # Official project charter & student declaration
│   ├── SRS_DOCUMENT.md                        # Complete IEEE 830-standard Software Requirements Specification
│   ├── SYSTEM_ARCHITECTURE.md                 # Layered MVC + Poka-Yoke architecture and flowcharts
│   └── DATABASE_SCHEMA.md                     # Relational SQLite DDL, CHECK constraints, and triggers
└── src/
    ├── __init__.py                            # Package initialization
    ├── app.py                                 # Main Tkinter desktop GUI application controller
    ├── database.py                            # SQLite engine, schema triggers, and seed data
    ├── models.py                              # Data Access Layer (DAL) repositories & atomic transactions
    ├── validation.py                          # Poka-Yoke validators, bounds checks & LASA detection
    └── widgets.py                             # MaskedDate, MaskedBatch, AutoComplete, and Delta Modals
```

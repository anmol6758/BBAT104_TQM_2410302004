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


# Review 2 Submission Dossier & Quality Goal Implementation Report
## Course: BBAT104 Fundamentals of TQM | Maximum Marks: 15 (CO1, CO2)
### Project: Pharmacy Management System - [Q07: Improve Data Accuracy]
**Student:** Anmol Joshi (Roll No: 2410302004, Branch: CSE, Section B)

---

## 1. Executive Summary & Review 2 Objectives
The primary objective of **Review 2 (Base System & CRUD + 5 Quality Goal Features)** is to deliver a fully functional, ACID-compliant desktop software system in Python and verify the end-to-end execution of all **five mandatory quality features** associated with **Quality Goal Q07 (Improve Data Accuracy)**. Mapped to Course Outcomes **CO1** (System Design) and **CO2** (Quality Control Integration), this deliverable proves that software quality can be engineered into the input flow (Poka-Yoke) to achieve zero data entry defects.

---

## 2. Review 2 Evaluation Deliverables Matrix (15 Marks)

| Item | Deliverable Requirement | Implementation Artefact | Verification Status |
| :---: | :--- | :--- | :---: |
| **1** | Fully Functional CRUD Operations | [`src/app.py`](file:///d:/TQM%20Project/src/app.py) & [`src/models.py`](file:///d:/TQM%20Project/src/models.py) | **COMPLETED & TESTED** |
| **2** | Q07 Feature 1: Input Masking | [`src/widgets.py`](file:///d:/TQM%20Project/src/widgets.py) (`MaskedDateEntry`, `MaskedBatchEntry`, `MaskedPhoneEntry`) | **VERIFIED** |
| **3** | Q07 Feature 2: Dropdown Lists | [`src/validation.py`](file:///d:/TQM%20Project/src/validation.py) & Predefined Enum Constraints | **VERIFIED** |
| **4** | Q07 Feature 3: Auto-Complete | [`src/widgets.py`](file:///d:/TQM%20Project/src/widgets.py) (`AutoCompleteEntry` in POS Billing) | **VERIFIED** |
| **5** | Q07 Feature 4: Confirmation Modals | [`src/widgets.py`](file:///d:/TQM%20Project/src/widgets.py) (`ConfirmationModal` with Delta Preview) | **VERIFIED** |
| **6** | Q07 Feature 5: Immutable Audit Logs | [`src/database.py`](file:///d:/TQM%20Project/src/database.py) Triggers & Audit View in GUI | **VERIFIED** |
| **7** | Commit History Requirement (7–10 commits) | 8 structured commits for Review 2 (16 commits cumulative) | **COMPLETED** |

---

## 3. Deep-Dive: Verification of the 5 Q07 Quality Features

### Feature 1: Input Masking (Format Poka-Yoke)
- **Batch Code Enforcement:** Enforces syntax `BATCH-[A-Z0-9]{3,12}`. Keystrokes are automatically converted to uppercase and checked against regular expressions, eliminating non-standard batch notations.
- **Expiry Date Masking:** Uses `MaskedDateEntry` to automatically place hyphens (`YYYY-MM-DD`). Rejects invalid dates (e.g., February 31) and strictly blocks dates $\le \text{Today}$.
- **Telephone Masking:** Automatically formats customer/supplier numbers to `(XXX) XXX-XXXX`.

### Feature 2: Validated Dropdown Lists (Boundary Constraint)
- Eliminates spelling variance in clinical categories.
- Pre-validated sets:
  - **Dosage Forms:** `Tablet`, `Capsule`, `Syrup`, `Injection`, `Ointment`, `Drops`, `Inhaler`, `Suppository`.
  - **Drug Schedules:** `OTC`, `Schedule H`, `Schedule H1`, `Schedule X`.
  - **Categories:** `Antibiotic`, `Analgesic`, `Antihistamine`, `Antidiabetic`, `Cardiovascular`, etc.

### Feature 3: Dynamic Auto-Complete Search (Cognitive Poka-Yoke)
- Traditional POS systems suffer from Look-Alike / Sound-Alike (LASA) medication errors.
- The `AutoCompleteEntry` widget queries SQLite in real time ($\le 5\text{ ms}$) across both **Brand Names** (e.g., *Augmentin 625*) and **Active Generic Salts** (e.g., *Amoxicillin + Clavulanic Acid*).
- Displays stock quantity and price inline, preventing selection of out-of-stock or unverified drugs.

### Feature 4: Delta Confirmation Modals (Double-Check Mechanism)
- Before committing an update to an existing medicine, the `ConfirmationModal` inspects the active database row and displays a side-by-side comparison grid of **Parameter**, **Previous Value**, and **Proposed Value**.
- Deletion is protected with decommissioning verification displaying total inventory value at risk.

### Feature 5: Immutable Audit Trail (Total Traceability)
- Every transaction (`INSERT`, `UPDATE`, `DELETE`, `CHECKOUT`) writes a discrete record to `audit_logs`.
- Database schema triggers (`trg_prevent_audit_delete` and `trg_prevent_audit_update`) raise exceptions if any user attempts to alter historical audit logs.
- Dedicated GUI viewer allows filtering by action type, table, and exporting to CSV.

---

## 4. Commit History for Review 2 Milestone
1. `feat(db): implement SQLite database engine with foreign keys, checks, and sample pharmacy seed data`
2. `feat(models): implement data access layers for medicines, suppliers, inventory, and sales transactions`
3. `feat(ui-core): implement desktop GUI base shell, responsive layout, and navigation sidebar using Tkinter`
4. `feat(crud-inventory): implement full CRUD operations for medicine inventory management`
5. `feat(q07-masking-dropdowns): add input masking engine and validated dropdown lists for dosage forms & categories`
6. `feat(q07-autocomplete): implement real-time auto-complete search widget for medicines and salt compositions`
7. `feat(q07-modals): add smart confirmation modals with delta previews before critical state changes`
8. `feat(q07-audit): implement automated immutable audit logging for all database mutations and review 2 milestone`

---

## 5. Review 2 Viva Readiness Questions & Answers

### Q1: How does Input Masking represent the TQM principle of Poka-Yoke?
**A:** Poka-Yoke aims to make errors physically impossible rather than training operators to be careful. The input mask rejects non-numeric keystrokes in date fields and automatically structures input into `YYYY-MM-DD`. This prevents corrupted data at the source.

### Q2: Why is Auto-Complete critical for pharmaceutical safety?
**A:** Sound-Alike / Look-Alike (LASA) errors represent over 30% of clinical medication errors (e.g., confusing *Celebrex* with *Celexa*). By cross-querying both the commercial brand name and the active chemical salt simultaneously, the system provides active cognitive support to the dispensing pharmacist.

### Q3: What happens when an audit record deletion is attempted?
**A:** The database engine executes the trigger `trg_prevent_audit_delete`, aborts the query, and raises an uncatchable SQL `RAISE(FAIL, ...)` error. This ensures complete legal immutability and compliance with Good Pharmacy Practice (GPP).

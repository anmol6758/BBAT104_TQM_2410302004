# Pharmacy Management System - [Q07: Improve Data Accuracy]
### Course: BBAT104: Fundamentals of Total Quality Management (TQM)
**Academic Session:** 2026–2027 | **Assessment Milestone:** Review 1 (Setup & SRS - 10 Raw Marks)  
**Author:** Anmol Joshi  
**University Roll Number:** 2410302004  
**Branch & Section:** Computer Science & Engineering (CSE) | Section B  
**Allotted Baseline Project:** Pharmacy Management System  
**Sequential Quality Goal:** Q07 - Improve Data Accuracy  

---

## 📌 Review 1 Overview & Scope Definition
This project establishes an engineered, mistake-proofed pharmaceutical inventory and dispensing system governed by **Total Quality Management (TQM)** principles. The primary focus of Quality Goal **Q07 (Improve Data Accuracy)** is to eliminate clinical typographical errors, illegal date formats, and negative profit margins at the source through **Poka-Yoke (mistake-proofing)** mechanisms.

### Core Problem Statement
In retail and hospital pharmacies, manual clerical errors in batch entries, look-alike/sound-alike drug selection, and unmasked expiry dates lead to fatal patient overdoses or severe regulatory liability. Applying TQM principles ensures that quality is structurally designed into the software schema rather than relying on dangerous downstream inspection.

---

## 🛡️ Assigned Quality Goal Features (Q07)
As mandated by course guidelines for Review 1 planning, the system architecture incorporates five foundational data accuracy mechanisms:
1. **Input Masking:** Format enforcement for Expiry Dates (`YYYY-MM-DD`), Batch Codes (`BATCH-XXXXX`), and Phone Numbers (`(XXX) XXX-XXXX`).
2. **Restricted Dropdown Lists:** Elimination of free-text typos in clinical categories, dosage forms, and statutory schedules (`OTC`, `Schedule H`, `H1`, `X`).
3. **Dynamic Auto-Complete Search:** Real-time cross-query of Commercial Brand Names and Active Generic Chemical Salts to eliminate Sound-Alike/Look-Alike (LASA) selection errors.
4. **Delta Confirmation Modals:** Two-step verification dialogs displaying a side-by-side comparison of Previous vs. Proposed values prior to database commit.
5. **Immutable Audit Logging:** Automated, tamper-evident recording of all database row insertions, modifications, and deletions.

---

## 📐 System Architecture & Design
The system employs a layered **Model-View-Controller (MVC)** architecture augmented with a dedicated **Poka-Yoke Quality Filter Layer**:
- **Presentation Layer (Tkinter GUI):** Responsive, modern desktop interface with navigation sidebar and real-time status indicators.
- **Poka-Yoke & Validation Layer:** Keystroke-level input masks and regular expression interceptors blocking corrupted inputs before processing.
- **Business Logic Layer:** Inventory controllers, dispensing transaction coordinators, and audit aggregators.
- **Data Persistence Layer (SQLite3):** Relational engine operating with Write-Ahead Logging (WAL) and foreign key constraint enforcement.

---

## 🗂️ Review 1 Deliverables & Documentation Index
All foundational specifications for Review 1 are documented under the `docs/` directory:
- [`docs/PROJECT_CHARTER.md`](docs/PROJECT_CHARTER.md) - Official project charter, student declaration, problem statement, and milestone timeline.
- [`docs/SRS_DOCUMENT.md`](docs/SRS_DOCUMENT.md) - Complete IEEE 830-standard Software Requirements Specification (Functional requirements FR-01 to FR-15, Data Dictionaries, NFRs, and CTQ parameters).
- [`docs/SYSTEM_ARCHITECTURE.md`](docs/SYSTEM_ARCHITECTURE.md) - Detailed system architecture flowchart, sequence interaction models, and layered component specifications.
- [`docs/DATABASE_SCHEMA.md`](docs/DATABASE_SCHEMA.md) - Relational SQLite DDL schema, CHECK constraints, and immutability triggers.

---

## 🚀 Environment Setup & Prerequisites
- **Python Version:** Python 3.10+ (Current runtime: Python 3.14)
- **GUI Framework:** Standard Tkinter (bundled with Python)
- **Database Engine:** Embedded SQLite3
- **Dependencies:** Listed in [`requirements.txt`](requirements.txt) (`matplotlib`, `pandas`, `numpy`, `pillow`)

```powershell
# Clone the repository
git clone https://github.com/anmol6758/BBAT104_TQM_2410302004.git

# Install required dependencies
pip install -r requirements.txt
```

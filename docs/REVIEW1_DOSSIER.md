# Review 1 Submission Dossier & Evaluation Checklist
## Course: BBAT104 Fundamentals of TQM | Maximum Marks: 10 (CO1)
### Project: Pharmacy Management System - [Q07: Improve Data Accuracy]
**Student:** Anmol Joshi (Roll No: 2410302004, Branch: CSE, Section B)

---

## 1. Executive Summary & Review 1 Objectives
The primary objective of **Review 1 (Setup & SRS)** is to establish a rigorous, disciplined engineering baseline for the semester course project. Grounded in Course Outcome 1 (**CO1: Understand and apply foundational TQM frameworks and requirement analysis to software systems**), this milestone transitions project requirements into an IEEE 830 standard Software Requirements Specification, an architectural flowchart, an ACID-compliant database blueprint, and a verifiable Git version history.

---

## 2. Review 1 Evaluation Deliverables Checklist (10 Marks)

| Item | Evaluation Requirement | Target Document / Artefact | Status |
| :---: | :--- | :--- | :---: |
| **1** | Repository Initialization & Version Control Setup | `.gitignore`, `requirements.txt`, Initialized Git Repo | **COMPLETED** |
| **2** | Official Topic Allocation & Project Charter | [`docs/PROJECT_CHARTER.md`](file:///d:/TQM%20Project/docs/PROJECT_CHARTER.md) | **COMPLETED** |
| **3** | IEEE 830-Compliant SRS Document | [`docs/SRS_DOCUMENT.md`](file:///d:/TQM%20Project/docs/SRS_DOCUMENT.md) | **COMPLETED** |
| **4** | System Architecture Flowchart & Interaction Model | [`docs/SYSTEM_ARCHITECTURE.md`](file:///d:/TQM%20Project/docs/SYSTEM_ARCHITECTURE.md) | **COMPLETED** |
| **5** | Relational SQLite Schema & Integrity Constraint Matrix | [`docs/DATABASE_SCHEMA.md`](file:///d:/TQM%20Project/docs/DATABASE_SCHEMA.md) | **COMPLETED** |
| **6** | Critical to Quality (CTQ) Parameters Definition | Defined in SRS Section 5 & Charter | **COMPLETED** |
| **7** | Commit History Requirement (7–10 commits for Review 1)| 8 granular, atomic, convention-compliant commits | **COMPLETED** |

---

## 3. Commit History for Review 1 Milestone
Review 1 comprises **8 structured commits** documenting every stage of requirement analysis and system design:

1. `chore(init): initialize repository structure and .gitignore for BBAT104 TQM project`
2. `docs(meta): add project charter, student declaration, and topic allocation metadata`
3. `docs(srs): add Section 1 & 2 of SRS - introduction, overall description, user classes, and operational environment`
4. `docs(srs): add Section 3 of SRS - functional requirements, CRUD specifications, and data dictionaries`
5. `docs(srs): add Section 4 & 5 of SRS - non-functional requirements and Q07 Data Accuracy CTQ parameters`
6. `docs(arch): add system architecture flowchart and component interaction specifications`
7. `docs(db): specify SQLite relational database schema and integrity constraint matrix`
8. `docs(review1): finalize Review 1 submission dossier, review checklist, and milestones report`

---

## 4. Key Review 1 Viva Defense Questions & Answers

### Q1: Why was "Improve Data Accuracy" (Q07) paired with a Pharmacy Management System?
**A:** In pharmaceuticals, typographical errors, unmasked dates, or misselected drug dosages lead to catastrophic clinical outcomes (e.g., dispensing ten times the intended dosage or selling an expired antibiotic). Applying TQM Poka-Yoke error prevention eliminates clerical mistakes at the point of origin rather than relying on dangerous downstream inspection.

### Q2: How does the IEEE 830 SRS document align with TQM principles?
**A:** Deming's Point 3 emphasizes *building quality into the product rather than inspecting it in*. The SRS formally establishes Critical-to-Quality (CTQ) metrics and explicit schema boundaries (check constraints, immutable audit triggers) so that non-conforming data is structurally rejected by design.

### Q3: What is the significance of an immutable audit log in quality assurance?
**A:** Total Quality Management relies on **Fact-Based Decision Making** and complete process traceability. By enforcing database triggers that block `UPDATE` and `DELETE` on the `audit_logs` table, the system provides a legally sound, tamper-evident record of all inventory and price modifications.

---

## 5. Next Phase Roadmap: Review 2
In **Review 2 (Base System & CRUD + 5 Quality Goal Features - 15 Marks)**, the software will be implemented in Python:
- Implement `src/database.py` with schema creation, triggers, and certified sample seeds.
- Implement `src/models.py` and data access layers.
- Build the interactive Tkinter GUI (`src/app.py` & `src/widgets.py`).
- Implement full CRUD operations for medicine inventory.
- Implement all **5 Q07 Features**:
  1. Input Masking (regex formatted batch, expiry, phone, price).
  2. Dropdown Lists (constrained forms, schedules, suppliers).
  3. Dynamic Auto-Complete (cross-querying brand name and active salt).
  4. Confirmation Modals (delta preview of price and stock mutations).
  5. Immutable Audit Logs (real-time display tab).
- Execute 8 incremental commits for Review 2.

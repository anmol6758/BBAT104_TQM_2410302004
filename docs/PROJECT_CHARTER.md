# Project Charter & Academic Allocation

## 1. Project Identification & Allocation Details
- **Course Code & Title:** BBAT104: Fundamentals of Total Quality Management (TQM)
- **Academic Session:** 2026–2027
- **Maximum Assessment:** 70 Raw Marks
- **Student Name:** Anmol Joshi
- **University Roll Number:** 2410302004
- **Academic Branch & Section:** Computer Science & Engineering (CSE) | Section B
- **Allotted Serial Number:** S.No. 63 (from Official Master Allotment Sheet)
- **Assigned Baseline System:** **Pharmacy Management System**
- **Sequential Quality Goal:** **Q07 - Improve Data Accuracy**
- **Official Final Project Title:** `Pharmacy Management System - [Q07: Improve Data Accuracy]`

---

## 2. Allotted Quality Features for Q07
As mandated by the course guidelines for Quality Goal **Q07 (Improve Data Accuracy)**, the system incorporates the following five core mechanisms:
1. **Input Masking:** Format enforcement on critical inputs including batch numbers (`BATCH-XXXXX`), expiry dates (`YYYY-MM-DD`), phone numbers (`(XXX) XXX-XXXX`), and drug pricing.
2. **Dropdown Lists:** Elimination of manual free-text errors via constrained, pre-validated options for dosage forms (Tablets, Syrups, Injections, Ointments), schedule types (Schedule H, H1, OTC), and suppliers.
3. **Auto-Complete:** Real-time semantic search and active suggestion dropdowns for medicine trade names and active generic salts to prevent spelling errors.
4. **Confirmation Modals:** Explicit verification modals displaying state changes, price impacts, stock balance deductions, and destructive deletion warnings prior to database commit.
5. **Audit Logs:** Automated, tamper-evident transactional audit trails logging `timestamp`, `user_id`, `action_type`, `table_name`, `record_id`, `field_name`, `old_value`, and `new_value`.

---

## 3. Executive Problem Statement
In healthcare and retail pharmacy environments, data accuracy is a matter of life and death. Traditional manual or poorly validated pharmacy records suffer from:
- Illegible or mistyped medicine names (look-alike / sound-alike medications).
- Incorrect unit dosages (e.g., entering 500mg instead of 50mg, resulting in 10x overdose toxicity).
- Invalid expiry dates or dispensing expired batches due to free-text date formatting discrepancies.
- Stock discrepancies between physical inventory and ledger balances.
- Lack of accountability and historical traceability when inventory counts are altered.

Applying Total Quality Management (TQM) principles—specifically **Poka-Yoke (mistake-proofing)**, **Juran's Quality by Design**, and **Deming's Continuous Improvement cycle**—transforms the pharmacy software from a passive record-keeper into an active quality assurance safeguard.

---

## 4. TQM Methodological Framework
The project adopts a structured four-pillar TQM framework:
- **Poka-Yoke (Error Prevention at Source):** Input masks and drop-down constraints physically block bad data from entering the database pipeline.
- **Process Standardization (SIPOC & CTQ):** Strict operational mapping from supplier order receipts to patient dispensing.
- **Risk Prioritization (FMEA & RPN):** Quantitative failure mode analysis measuring Severity, Occurrence, and Detection before and after mistake-proofing controls.
- **Statistical Quality Control (SQC & Kaizen):** Empirical defect tracking via digital Checksheets, Pareto 80/20 root cause analysis, and Ishikawa (Fishbone) root-cause diagrams driving the PDCA cycle.

---

## 5. Course Outcome (CO) Mapping & Milestone Timeline
| Milestone | Timeline / Focus | Mapped COs | Target Deliverables |
| :--- | :--- | :--- | :--- |
| **Review 1** | Setup, SRS & Architecture | CO1 | Repository init, Charter, IEEE SRS Document, Flowcharts, Scope & CTQ parameters. (7–10 Commits) |
| **Review 2** | Base System & Q07 Features | CO1, CO2 | Working SQLite CRUD system + 5 Q07 features (Masking, Dropdowns, Autocomplete, Modals, Audit Log). (7–10 Commits) |
| **Review 3** | FMEA & Risk Audit | CO2 | SIPOC map, CTQ Tree, Baseline & Post-Mitigation FMEA matrix with RPN calculation. (7–10 Commits) |
| **Review 4** | SQC & Continuous Improvement | CO2, CO3 | Defect Checksheets, Matplotlib Pareto Chart (80/20), Ishikawa Fishbone diagram, PDCA cycle log. (7–10 Commits) |
| **Final Viva** | Demonstration & GitHub Health | CO3 | Live defense, comprehensive README, User Manual, >= 30 commits record. |

---

## 6. Student Undertaking & Declaration
I, **Anmol Joshi (Roll No: 2410302004)**, hereby declare that this project titled *"Pharmacy Management System - [Q07: Improve Data Accuracy]"* is my original work developed in fulfillment of BBAT104 Fundamentals of TQM. All algorithms, database schemas, quality control charts, and documentation have been crafted following academic integrity and the official syllabus guidelines.

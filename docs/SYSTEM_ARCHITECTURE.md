# System Architecture & Flowchart Specification
## Pharmacy Management System - [Q07: Improve Data Accuracy]
### Course: BBAT104 - Fundamentals of TQM | Academic Session: 2026–27
**Author:** Anmol Joshi (Roll No: 2410302004, Branch: CSE-B)

---

## 1. Architectural Style & Layered Model

The Pharmacy Management System is engineered using a **Layered Model-View-Controller (MVC)** pattern infused with an active **Poka-Yoke Quality Assurance Layer**. This architecture ensures that no user input reaches the database persistence layer without passing through multi-stage sanitization, constraint validation, and audit tracking.

```mermaid
flowchart TD
    subgraph UI["Layer 1: Presentation Layer (Tkinter GUI)"]
        UI_Nav["Sidebar Navigation"]
        UI_Inv["Medicine Inventory Tab"]
        UI_Bill["POS Billing & Dispensing Tab"]
        UI_Audit["Audit Trail Inspection Tab"]
        UI_SQC["SQC Quality Analytics Tab"]
    end

    subgraph Q07["Layer 2: Poka-Yoke & Q07 Data Accuracy Engine"]
        F1["Feature 1: Regex Input Masking\n(Batch, Date, Phone, Price)"]
        F2["Feature 2: Dropdown Lists\n(Forms, Schedules, Suppliers)"]
        F3["Feature 3: Dynamic Auto-Complete\n(Brand & Generic Cross-Search)"]
        F4["Feature 4: Confirmation Modals\n(Delta Preview & Deletion Gates)"]
        F5["Feature 5: Immutable Audit Logger\n(Pre/Post Image Capture)"]
        Defect["Defect Interceptor & Checksheet Logger"]
    end

    subgraph BLL["Layer 3: Business Logic & Processing"]
        InvMgr["Inventory & Stock Controller"]
        BillMgr["Billing & Invoicing Engine"]
        FMEAMgr["FMEA & Risk Priority Calculator"]
        SQCMgr["Pareto & Fishbone Chart Generator"]
    end

    subgraph DAL["Layer 4: Data Persistence Layer (SQLite3 Engine)"]
        FK["Foreign Key Enforcer (PRAGMA foreign_keys=ON)"]
        Schema["Relational Tables (medicines, sales, suppliers)"]
        Triggers["Schema Triggers (Audit & Stock Safeguards)"]
        WAL["Write-Ahead Logging (WAL Persistence)"]
    end

    UI --> Q07
    Q07 -->|Validated Inputs| BLL
    Q07 -.->|Intercepted Errors| Defect
    BLL --> DAL
```

---

## 2. Poka-Yoke Data Validation Pipeline

The operational workflow for data entry explicitly enforces zero defect propagation (Deming Point 3: Cease dependence on mass inspection; build quality into the process):

```mermaid
sequenceDiagram
    autonumber
    actor User as Pharmacist / Clerk
    participant UI as Form Input / Field
    participant Mask as Masking & Dropdown Filter
    participant Auto as Auto-Complete Engine
    participant Modal as Confirmation Modal
    participant Logger as Defect / Audit Logger
    participant DB as SQLite3 Database

    User->>UI: Enter raw keystroke / Select item
    UI->>Mask: Check character against mask pattern
    alt Invalid character / format
        Mask-->>UI: Reject keystroke & trigger audible/visual warning
        Mask->>Logger: Record rejection event in defect checksheets
    else Valid format
        Mask-->>UI: Format text dynamically (e.g. YYYY-MM-DD)
    end

    User->>Auto: Type >= 2 characters in medicine search
    Auto->>DB: Query brand and generic salts (< 50ms)
    DB-->>Auto: Return matched candidates
    Auto-->>User: Display filtered dropdown menu

    User->>UI: Click Submit / Alter Price / Checkout
    UI->>Modal: Generate Delta Confirmation Dialog
    Modal-->>User: Display Old vs New Values + Action Impact
    alt User cancels
        User->>Modal: Click Cancel / Dismiss
        Modal-->>UI: Abort transaction (no DB mutation)
    else User confirms
        User->>Modal: Click Confirm
        Modal->>DB: Execute atomic SQL transaction
        DB->>Logger: Capture before/after images into audit_logs
        DB-->>UI: Transaction Committed Successfully
    end
```

---

## 3. High-Level Component Interactions

| Subsystem Component | Primary Responsibility | TQM Principle Alignment |
| :--- | :--- | :--- |
| **`app.py`** | Central Tkinter application orchestrating tabs and UI state | Customer Focus & Ergonomics |
| **`widgets.py`** | Custom input-masked entry widgets, dropdowns, and modal dialogs | Poka-Yoke (Mistake Proofing) |
| **`database.py`** | SQLite relational initialization, foreign keys, and atomic commits | Fact-Based Quality & Standardization |
| **`models.py`** | Entity models with built-in validation rules and business invariants | Process Integrity & Defect Prevention |
| **`defect_logger.py`**| Real-time capture of intercepted errors for checksheet aggregation | Empirical Quality Control (SQC) |
| **`pareto.py`** | Pareto 80/20 frequency analysis and cumulative curve visualization | Juran's Vital Few vs. Trivial Many |
| **`fishbone.py`** | Ishikawa cause-and-effect diagram generator across 6M categories | Root Cause Analysis (Kaizen) |
| **`fmea.py`** | Risk Priority Number (RPN) computation engine ($S \times O \times D$) | Preventive Risk Management (FMEA) |

---

## 4. Hardware and Runtime Environment Flow
1. **Application Launch:** Initializes local SQLite engine (`pharmacy.db`), executes `CREATE TABLE IF NOT EXISTS`, and checks trigger definitions.
2. **Seed Verification:** Populates essential baseline categories, verified suppliers, and benchmark pharmaceuticals if the database is newly created.
3. **Event Loop Execution:** Binds keyboard shortcuts, input validation hooks, and starts Tkinter desktop main loop.

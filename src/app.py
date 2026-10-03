"""
Pharmacy Management System - [Q07: Improve Data Accuracy]
BBAT104: Fundamentals of TQM (Session 2026-27)
Student: Anmol Joshi (Roll No: 2410302004, Branch: CSE-B)
Main Application Shell with Full CRUD Inventory Operations
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import init_db, seed_db
from src.models import (
    MedicineRepository, SupplierRepository, AuditRepository,
    SalesRepository, DefectRepository
)
from src.validation import DataValidator, ValidationError
from src.widgets import (
    MaskedDateEntry, MaskedPhoneEntry, MaskedBatchEntry,
    AutoCompleteEntry, ConfirmationModal,
    PlaceholderEntry, PlaceholderMaskedPhoneEntry, BatchNumberWidget
)




class PharmacyApp(tk.Tk):
    """Primary Application Window for Pharmacy Management System."""

    def __init__(self):
        super().__init__()
        self.title("Pharmacy Management System - [Q07: Improve Data Accuracy]")
        self.geometry("1260x780")
        self.minsize(1100, 700)

        # Initialize and seed database
        init_db()
        seed_db()

        self._configure_styles()
        self._build_header()
        self._build_body()
        self._build_statusbar()

        # Start on Inventory tab
        self.show_inventory_tab()

    def _configure_styles(self):
        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        self.primary_color = "#005f73"
        self.secondary_color = "#0a9396"
        self.accent_color = "#ee9b00"
        self.bg_light = "#f8f9fa"
        self.text_dark = "#212529"

        self.configure(bg=self.bg_light)
        self.style.configure(".", background=self.bg_light, foreground=self.text_dark, font=("Calibri", 11))
        self.style.configure("Header.TFrame", background=self.primary_color)
        self.style.configure("HeaderTitle.TLabel", background=self.primary_color, foreground="#ffffff", font=("Trebuchet MS", 16, "bold"))
        self.style.configure("HeaderSub.TLabel", background=self.primary_color, foreground="#94d2bd", font=("Calibri", 11))

        self.style.configure("Nav.TFrame", background="#e9ecef")
        self.style.configure("Nav.TButton", font=("Calibri", 11, "bold"), padding=8)
        self.style.configure("Action.TButton", font=("Calibri", 11, "bold"), padding=6)
        self.style.configure("Danger.TButton", font=("Calibri", 11, "bold"), padding=6)
        self.style.configure("Success.TButton", font=("Calibri", 11, "bold"), padding=6)

        self.style.configure("Treeview.Heading", font=("Calibri", 11, "bold"), background="#dee2e6")
        self.style.configure("Treeview", rowheight=26, font=("Calibri", 10))
        self.style.map("Treeview", background=[("selected", self.secondary_color)], foreground=[("selected", "#ffffff")])

    def _build_header(self):
        header_frame = ttk.Frame(self, style="Header.TFrame", padding=(20, 12))
        header_frame.pack(side=tk.TOP, fill=tk.X)

        title_box = ttk.Frame(header_frame, style="Header.TFrame")
        title_box.pack(side=tk.LEFT)

        title_lbl = ttk.Label(title_box, text="💊 PHARMACY MANAGEMENT SYSTEM", style="HeaderTitle.TLabel")
        title_lbl.pack(anchor=tk.W)

        sub_lbl = ttk.Label(
            title_box,
            text="Quality Goal [Q07: Improve Data Accuracy]  |  BBAT104 TQM  |  Anmol Joshi (2410302004, CSE-B)",
            style="HeaderSub.TLabel"
        )
        sub_lbl.pack(anchor=tk.W)

        badge_frame = tk.Frame(header_frame, bg="#94d2bd", padx=10, pady=4)
        badge_frame.pack(side=tk.RIGHT, pady=2)
        badge_lbl = tk.Label(
            badge_frame,
            text="Poka-Yoke & Audit Active",
            bg="#94d2bd",
            fg=self.primary_color,
            font=("Calibri", 10, "bold")
        )
        badge_lbl.pack()

    def _build_body(self):
        main_container = ttk.Frame(self)
        main_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.sidebar = ttk.Frame(main_container, style="Nav.TFrame", width=230, padding=10)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        nav_title = ttk.Label(self.sidebar, text="NAVIGATION", font=("Calibri", 10, "bold"), background="#e9ecef", foreground="#6c757d")
        nav_title.pack(anchor=tk.W, pady=(5, 10))

        tabs = [
            ("inventory", "📦 Medicine Inventory", self.show_inventory_tab),
            ("billing", "🧾 Billing & POS", self.show_billing_tab),
            ("audit", "📜 Audit Log (Q07)", self.show_audit_tab),
            ("sqc", "📊 SQC Quality Analytics", self.show_sqc_tab),
        ]

        self.nav_buttons = {}
        for key, label, cmd in tabs:
            btn = ttk.Button(self.sidebar, text=label, style="Nav.TButton", command=cmd)
            btn.pack(fill=tk.X, pady=4)
            self.nav_buttons[key] = btn

        tqm_card = tk.LabelFrame(self.sidebar, text="TQM Quality Focus", bg="#e9ecef", font=("Calibri", 10, "bold"), padx=8, pady=8)
        tqm_card.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        info_text = (
            "Goal: Q07 Data Accuracy\n"
            "• Input Masking\n"
            "• Dropdown Lists\n"
            "• Auto-Complete\n"
            "• Confirmation Modals\n"
            "• Immutable Audit Logs"
        )
        tk.Label(tqm_card, text=info_text, justify=tk.LEFT, bg="#e9ecef", font=("Calibri", 9)).pack(anchor=tk.W)

        self.content_area = ttk.Frame(main_container, padding=15)
        self.content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def _build_statusbar(self):
        self.statusbar = ttk.Frame(self, relief=tk.SUNKEN, padding=(10, 4))
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_lbl = ttk.Label(self.statusbar, text="System Ready | Database: Connected (WAL Mode) | User: Pharmacist", font=("Calibri", 9))
        self.status_lbl.pack(side=tk.LEFT)

        self.time_lbl = ttk.Label(self.statusbar, text=datetime.now().strftime("%Y-%m-%d %H:%M"), font=("Calibri", 9))
        self.time_lbl.pack(side=tk.RIGHT)

    def clear_content(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()

    # =========================================================================
    # TAB 1: MEDICINE INVENTORY (CRUD)
    # =========================================================================
    def show_inventory_tab(self):
        self.clear_content()

        # Top Control Header
        top_bar = ttk.Frame(self.content_area)
        top_bar.pack(fill=tk.X, pady=(0, 10))

        title = ttk.Label(top_bar, text="Medicine Inventory Management", font=("Trebuchet MS", 14, "bold"))
        title.pack(side=tk.LEFT)

        # Alert Summary Badges (Saved to instance for dynamic updates)
        low_stock, expiring = MedicineRepository.get_stock_alerts()
        alert_box = ttk.Frame(top_bar)
        alert_box.pack(side=tk.RIGHT)

        self.low_stock_badge = tk.Label(
            alert_box, text=f"⚠️ Low Stock: {len(low_stock)}",
            bg="#fee2e2", fg="#991b1b", font=("Calibri", 10, "bold"),
            padx=10, pady=3, relief=tk.SOLID, bd=1
        )
        self.low_stock_badge.pack(side=tk.LEFT, padx=5)

        self.exp_badge = tk.Label(
            alert_box, text=f"⏱ Expiring Soon: {len(expiring)}",
            bg="#fef3c7", fg="#92400e", font=("Calibri", 10, "bold"),
            padx=10, pady=3, relief=tk.SOLID, bd=1
        )
        self.exp_badge.pack(side=tk.LEFT, padx=5)

        # Search and Filter Toolbar
        filter_bar = ttk.Frame(self.content_area)
        filter_bar.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(filter_bar, text="Search:").pack(side=tk.LEFT, padx=(0, 4))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(filter_bar, textvariable=self.search_var, width=18)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 8))
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_inventory_data())

        ttk.Label(filter_bar, text="Category:").pack(side=tk.LEFT, padx=(4, 4))
        self.cat_filter_var = tk.StringVar(value="All")
        self.cat_combo = ttk.Combobox(
            filter_bar, textvariable=self.cat_filter_var, state="readonly", width=14,
            values=["All", "Antibiotic", "Analgesic", "Antihistamine", "Antidiabetic", "Cardiovascular", "Gastrointestinal", "Respiratory", "Dermatological"]
        )
        self.cat_combo.pack(side=tk.LEFT, padx=(0, 8))
        self.cat_combo.bind("<<ComboboxSelected>>", lambda e: self.load_inventory_data())

        ttk.Label(filter_bar, text="Filter:").pack(side=tk.LEFT, padx=(4, 4))
        self.status_filter_var = tk.StringVar(value="All")
        self.status_combo = ttk.Combobox(
            filter_bar, textvariable=self.status_filter_var, state="readonly", width=13,
            values=["All", "Low Stock", "Expiring Soon"]
        )
        self.status_combo.pack(side=tk.LEFT, padx=(0, 8))
        self.status_combo.bind("<<ComboboxSelected>>", lambda e: self.load_inventory_data())

        ttk.Label(filter_bar, text="Sort By:").pack(side=tk.LEFT, padx=(4, 4))
        self.sort_var = tk.StringVar(value="ID (Ascending)")
        self.sort_combo = ttk.Combobox(
            filter_bar, textvariable=self.sort_var, state="readonly", width=15,
            values=["ID (Ascending)", "Name (A-Z)", "Name (Z-A)", "Stock (Lowest First)", "Stock (Highest First)", "Expiry (Soonest)", "Price (Lowest First)"]
        )
        self.sort_combo.pack(side=tk.LEFT, padx=(0, 8))
        self.sort_combo.bind("<<ComboboxSelected>>", lambda e: self.load_inventory_data())

        # Action Buttons
        btn_add = ttk.Button(filter_bar, text="➕ Add Medicine", style="Success.TButton", command=self.open_add_medicine_dialog)
        btn_add.pack(side=tk.RIGHT, padx=4)

        btn_edit = ttk.Button(filter_bar, text="✏️ Edit Selected", style="Action.TButton", command=self.open_edit_medicine_dialog)
        btn_edit.pack(side=tk.RIGHT, padx=4)

        btn_del = ttk.Button(filter_bar, text="🗑️ Delete", style="Danger.TButton", command=self.delete_selected_medicine)
        btn_del.pack(side=tk.RIGHT, padx=4)

        btn_refresh = ttk.Button(filter_bar, text="🔄 Refresh", command=self.load_inventory_data)
        btn_refresh.pack(side=tk.RIGHT, padx=4)

        # Inventory Table (Treeview)
        table_frame = ttk.Frame(self.content_area)
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("id", "name", "generic_name", "category", "form", "schedule", "batch", "expiry", "cost", "price", "stock", "supplier")
        self.inv_tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        col_defs = [
            ("id", "ID", 45, tk.CENTER),
            ("name", "Trade Name", 140, tk.W),
            ("generic_name", "Generic Salt Composition", 180, tk.W),
            ("category", "Category", 100, tk.W),
            ("form", "Form", 75, tk.CENTER),
            ("schedule", "Schedule", 90, tk.CENTER),
            ("batch", "Batch No", 100, tk.CENTER),
            ("expiry", "Expiry Date", 90, tk.CENTER),
            ("cost", "Cost (Rs. )", 70, tk.E),
            ("price", "Price (Rs. )", 75, tk.E),
            ("stock", "Stock", 65, tk.CENTER),
            ("supplier", "Supplier", 150, tk.W),
        ]

        for col_id, heading, width, align in col_defs:
            self.inv_tree.heading(col_id, text=heading)
            self.inv_tree.column(col_id, width=width, anchor=align)

        # Scrollbars
        y_scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.inv_tree.yview)
        x_scroll = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.inv_tree.xview)
        self.inv_tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        self.inv_tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Tag styles for stock status matching top badge highlight colors
        self.inv_tree.tag_configure("low_stock", background="#fee2e2", foreground="#991b1b")
        self.inv_tree.tag_configure("expiring", background="#fef3c7", foreground="#92400e")
        self.inv_tree.tag_configure("both_critical", background="#fed7aa", foreground="#9a3412")
        self.inv_tree.tag_configure("normal", background="#ffffff", foreground="#1f2937")

        self.load_inventory_data()

    def load_inventory_data(self):
        # Dynamically update top alert count badges
        low_stock_list, expiring_list = MedicineRepository.get_stock_alerts()
        if hasattr(self, "low_stock_badge") and self.low_stock_badge.winfo_exists():
            self.low_stock_badge.config(text=f"⚠️ Low Stock: {len(low_stock_list)}")
        if hasattr(self, "exp_badge") and self.exp_badge.winfo_exists():
            self.exp_badge.config(text=f"⏱ Expiring Soon: {len(expiring_list)}")

        for item in self.inv_tree.get_children():
            self.inv_tree.delete(item)

        search = self.search_var.get().strip() if hasattr(self, "search_var") else None
        category = self.cat_filter_var.get() if hasattr(self, "cat_filter_var") else None
        status_filter = self.status_filter_var.get() if hasattr(self, "status_filter_var") else "All"

        sort_display = self.sort_var.get() if hasattr(self, "sort_var") else "ID (Ascending)"
        sort_map = {
            "ID (Ascending)": "id_asc",
            "Name (A-Z)": "name_asc",
            "Name (Z-A)": "name_desc",
            "Stock (Lowest First)": "stock_asc",
            "Stock (Highest First)": "stock_desc",
            "Expiry (Soonest)": "expiry_asc",
            "Price (Lowest First)": "price_asc",
        }
        sort_by = sort_map.get(sort_display, "id_asc")

        medicines = MedicineRepository.get_all(
            search=search, category=category, status_filter=status_filter, sort_by=sort_by
        )

        warning_expiry = (date.today() + __import__("datetime").timedelta(days=90)).strftime("%Y-%m-%d")

        for m in medicines:
            is_low = m["stock_qty"] <= m["reorder_level"]
            is_exp = m["expiry_date"] <= warning_expiry
            if is_low and is_exp:
                tag = "both_critical"
            elif is_low:
                tag = "low_stock"
            elif is_exp:
                tag = "expiring"
            else:
                tag = "normal"

            self.inv_tree.insert("", tk.END, values=(
                m["id"], m["name"], m["generic_name"], m["category"], m["dosage_form"],
                m["schedule_type"], m["batch_no"], m["expiry_date"],
                f"{m['purchase_price']:.2f}", f"{m['sale_price']:.2f}",
                m["stock_qty"], m.get("supplier_name") or "Direct"
            ), tags=(tag,))

        self.status_lbl.config(text=f"Loaded {len(medicines)} medicines into inventory view.")

    def open_add_medicine_dialog(self):
        MedicineFormDialog(self, mode="add", on_save=self.load_inventory_data)

    def open_edit_medicine_dialog(self):
        selected = self.inv_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a medicine from the list to edit.")
            return
        med_id = self.inv_tree.item(selected[0])["values"][0]
        med_data = MedicineRepository.get_by_id(med_id)
        if med_data:
            MedicineFormDialog(self, mode="edit", medicine_data=med_data, on_save=self.load_inventory_data)

    def delete_selected_medicine(self):
        selected = self.inv_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a medicine from the list to delete.")
            return
        item_vals = self.inv_tree.item(selected[0])["values"]
        med_id, med_name = item_vals[0], item_vals[1]
        batch, stock = item_vals[6], item_vals[10]

        # Q07 Feature 4: Confirmation Modal with Delta/Decommissioning Details
        def confirm_delete():
            try:
                MedicineRepository.delete(med_id, user_role="Pharmacist")
                messagebox.showinfo("Success", f"Medicine '{med_name}' deleted successfully.")
                self.load_inventory_data()
            except ValueError as ex:
                messagebox.showerror("Deletion Prohibited", str(ex))

        ConfirmationModal(
            self,
            title="Confirm Decommissioning / Deletion",
            action_description=(
                f"You are requesting to permanently delete '{med_name}' (ID: {med_id}) from active catalog.\n"
                f"Batch: {batch} | Active Stock: {stock} units.\n\n"
                f"This action cannot be undone. An immutable audit record will be logged."
            ),
            changes_dict={
                "Record Status": ("Active In Stock", "Permanently Decommissioned"),
                "Medicine Name": (med_name, "REMOVED"),
                "Batch Number": (batch, "DECOMMISSIONED")
            },
            on_confirm=confirm_delete
        )

    # =========================================================================
    # PLACEHOLDERS FOR REMAINING TABS
    # =========================================================================
    # =========================================================================
    # TAB 2: BILLING & POS (Q07 Feature 3: Auto-Complete)
    # =========================================================================

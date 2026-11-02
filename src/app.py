"""
Pharmacy Management System - [Q07: Improve Data Accuracy]
BBAT104: Fundamentals of TQM (Session 2026-27)
Student: Anmol Joshi (Roll No: 2410302004, Branch: CSE-B)
Main Application Shell with Full CRUD Inventory Operations,
Role-Based Access Control, Differential GST Taxes, Unified POS Workspace,
Supplier Deal Comparison, and Automatic Customer Data Storage.
"""

import sys
import os
import re
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, timedelta

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import init_db, seed_db
from src.models import (
    MedicineRepository, SupplierRepository, AuditRepository,
    SalesRepository, DefectRepository, CustomerRepository,
    SupplierDealRepository
)
from src.validation import DataValidator, ValidationError
from src.widgets import (
    MaskedDateEntry, MaskedPhoneEntry, MaskedBatchEntry,
    AutoCompleteEntry, ConfirmationModal,
    PlaceholderEntry, PlaceholderMaskedPhoneEntry, BatchNumberWidget,
    SupplierComparisonDialog
)


class PharmacyApp(tk.Tk):
    """Primary Application Window for Pharmacy Management System."""

    def __init__(self):
        super().__init__()
        self.title("Pharmacy Management System - [Q07: Improve Data Accuracy]")
        self.geometry("1280x800")
        self.minsize(1120, 720)

        # Active User Role (Requirement 1: Admin, Pharmacist, Cashier)
        self.current_user_role = tk.StringVar(value="Admin")

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
        self.style.configure("HeaderTitle.TLabel", background=self.primary_color, foreground="#ffffff", font=("Trebuchet MS", 15, "bold"))
        self.style.configure("HeaderSub.TLabel", background=self.primary_color, foreground="#94d2bd", font=("Calibri", 10))

        self.style.configure("Nav.TFrame", background="#e9ecef")
        self.style.configure("Nav.TButton", font=("Calibri", 11, "bold"), padding=8)
        self.style.configure("Action.TButton", font=("Calibri", 10, "bold"), padding=5)
        self.style.configure("Danger.TButton", font=("Calibri", 10, "bold"), padding=5)
        self.style.configure("Success.TButton", font=("Calibri", 10, "bold"), padding=5)

        self.style.configure("Treeview.Heading", font=("Calibri", 10, "bold"), background="#dee2e6")
        self.style.configure("Treeview", rowheight=26, font=("Calibri", 10))
        self.style.map("Treeview", background=[("selected", self.secondary_color)], foreground=[("selected", "#ffffff")])

    def _build_header(self):
        header_frame = ttk.Frame(self, style="Header.TFrame", padding=(18, 10))
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

        # Right side: Role-Based Access Control Switcher & Poka-Yoke Badge
        right_box = ttk.Frame(header_frame, style="Header.TFrame")
        right_box.pack(side=tk.RIGHT)

        role_box = tk.Frame(right_box, bg="#004654", padx=8, pady=4, relief=tk.GROOVE, bd=1)
        role_box.pack(side=tk.RIGHT, padx=(10, 0))

        tk.Label(role_box, text="👤 Role:", bg="#004654", fg="#94d2bd", font=("Calibri", 10, "bold")).pack(side=tk.LEFT, padx=(0, 4))
        self.role_combo = ttk.Combobox(
            role_box, textvariable=self.current_user_role, state="readonly", width=11,
            values=["Admin", "Pharmacist", "Cashier"], font=("Calibri", 10, "bold")
        )
        self.role_combo.pack(side=tk.LEFT)
        self.role_combo.bind("<<ComboboxSelected>>", self._on_role_change)

        badge_frame = tk.Frame(right_box, bg="#94d2bd", padx=8, pady=4)
        badge_frame.pack(side=tk.RIGHT)
        badge_lbl = tk.Label(
            badge_frame,
            text="🛡️ Poka-Yoke & Audit Active",
            bg="#94d2bd",
            fg=self.primary_color,
            font=("Calibri", 10, "bold")
        )
        badge_lbl.pack()

    def _on_role_change(self, event=None):
        role = self.current_user_role.get()
        if hasattr(self, "status_lbl"):
            self.status_lbl.config(text=f"Active Role: {role} | Permissions: {self._get_role_permission_summary(role)}")
        # Refresh current tab view if inventory is open
        if hasattr(self, "current_tab_name") and self.current_tab_name == "inventory":
            self.load_inventory_data()

    def _get_role_permission_summary(self, role):
        if role == "Admin":
            return "Full Access (Master Inventory CRUD, Deletions, Pricing, Deals, POS Billing, Audits)"
        elif role == "Pharmacist":
            return "Dispensing & Stock Management (Add/Edit Inventory, Compare Deals, POS Billing; Deletions Restricted)"
        elif role == "Cashier":
            return "Point of Sale Billing (Dispensing & Invoice Generation; Inventory Master Read-Only)"
        return "Standard User"

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
            "• Role-Based Access Control\n"
            "• Input Masking (Dates/Phones)\n"
            "• Unified Barcode Scanner Bar\n"
            "• Multi-Slab GST Taxes (0-18%)\n"
            "• Supplier Discount Comparison\n"
            "• Automatic Patient Registration\n"
            "• Immutable Audit Triggers"
        )
        tk.Label(tqm_card, text=info_text, justify=tk.LEFT, bg="#e9ecef", font=("Calibri", 9)).pack(anchor=tk.W)

        self.content_area = ttk.Frame(main_container, padding=14)
        self.content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def _build_statusbar(self):
        self.statusbar = ttk.Frame(self, relief=tk.SUNKEN, padding=(10, 4))
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

        role = self.current_user_role.get()
        self.status_lbl = ttk.Label(
            self.statusbar,
            text=f"System Ready | Database: Connected (WAL Mode) | User Role: {role} ({self._get_role_permission_summary(role)})",
            font=("Calibri", 9)
        )
        self.status_lbl.pack(side=tk.LEFT)

        self.time_lbl = ttk.Label(self.statusbar, text=datetime.now().strftime("%Y-%m-%d %H:%M"), font=("Calibri", 9))
        self.time_lbl.pack(side=tk.RIGHT)

    def clear_content(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()

    # =========================================================================
    # TAB 1: MEDICINE INVENTORY (CRUD + SUPPLIER DEALS COMPARISON)
    # =========================================================================
    def show_inventory_tab(self):
        self.current_tab_name = "inventory"
        self.clear_content()

        # Top Control Header
        top_bar = ttk.Frame(self.content_area)
        top_bar.pack(fill=tk.X, pady=(0, 10))

        title = ttk.Label(top_bar, text="Medicine Inventory Management", font=("Trebuchet MS", 14, "bold"))
        title.pack(side=tk.LEFT)

        # Alert Summary Badges
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
        self.search_entry = ttk.Entry(filter_bar, textvariable=self.search_var, width=15)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 6))
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_inventory_data())

        ttk.Label(filter_bar, text="Category:").pack(side=tk.LEFT, padx=(4, 4))
        self.cat_filter_var = tk.StringVar(value="All")
        self.cat_combo = ttk.Combobox(
            filter_bar, textvariable=self.cat_filter_var, state="readonly", width=12,
            values=["All", "Antibiotic", "Analgesic", "Antihistamine", "Antidiabetic", "Cardiovascular", "Gastrointestinal", "Respiratory", "Dermatological"]
        )
        self.cat_combo.pack(side=tk.LEFT, padx=(0, 6))
        self.cat_combo.bind("<<ComboboxSelected>>", lambda e: self.load_inventory_data())

        ttk.Label(filter_bar, text="Filter:").pack(side=tk.LEFT, padx=(4, 4))
        self.status_filter_var = tk.StringVar(value="All")
        self.status_combo = ttk.Combobox(
            filter_bar, textvariable=self.status_filter_var, state="readonly", width=12,
            values=["All", "Low Stock", "Expiring Soon"]
        )
        self.status_combo.pack(side=tk.LEFT, padx=(0, 6))
        self.status_combo.bind("<<ComboboxSelected>>", lambda e: self.load_inventory_data())

        ttk.Label(filter_bar, text="Sort:").pack(side=tk.LEFT, padx=(4, 4))
        self.sort_var = tk.StringVar(value="ID (Ascending)")
        self.sort_combo = ttk.Combobox(
            filter_bar, textvariable=self.sort_var, state="readonly", width=14,
            values=["ID (Ascending)", "Name (A-Z)", "Name (Z-A)", "Stock (Lowest First)", "Stock (Highest First)", "Expiry (Soonest)", "Price (Lowest First)"]
        )
        self.sort_combo.pack(side=tk.LEFT, padx=(0, 6))
        self.sort_combo.bind("<<ComboboxSelected>>", lambda e: self.load_inventory_data())

        # Action Buttons (Role Protected)
        btn_refresh = ttk.Button(filter_bar, text="🔄 Refresh", command=self.load_inventory_data)
        btn_refresh.pack(side=tk.RIGHT, padx=3)

        btn_del = ttk.Button(filter_bar, text="🗑️ Delete", style="Danger.TButton", command=self.delete_selected_medicine)
        btn_del.pack(side=tk.RIGHT, padx=3)

        btn_compare = ttk.Button(filter_bar, text="🏢 Compare Deals", style="Action.TButton", command=self.open_supplier_comparison_dialog)
        btn_compare.pack(side=tk.RIGHT, padx=3)

        btn_edit = ttk.Button(filter_bar, text="✏️ Edit", style="Action.TButton", command=self.open_edit_medicine_dialog)
        btn_edit.pack(side=tk.RIGHT, padx=3)

        btn_add = ttk.Button(filter_bar, text="➕ Add Medicine", style="Success.TButton", command=self.open_add_medicine_dialog)
        btn_add.pack(side=tk.RIGHT, padx=3)

        # Inventory Table (Treeview)
        table_frame = ttk.Frame(self.content_area)
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("id", "name", "generic_name", "category", "form", "schedule", "batch", "barcode", "expiry", "cost", "price", "tax_rate", "stock", "supplier")
        self.inv_tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        col_defs = [
            ("id", "ID", 40, tk.CENTER),
            ("name", "Trade Name", 130, tk.W),
            ("generic_name", "Generic Salt Composition", 170, tk.W),
            ("category", "Category", 95, tk.W),
            ("form", "Form", 70, tk.CENTER),
            ("schedule", "Schedule", 75, tk.CENTER),
            ("batch", "Batch No", 100, tk.CENTER),
            ("barcode", "Barcode", 95, tk.CENTER),
            ("expiry", "Expiry Date", 85, tk.CENTER),
            ("cost", "Cost (Rs.)", 70, tk.E),
            ("price", "MRP (Rs.)", 70, tk.E),
            ("tax_rate", "GST %", 55, tk.CENTER),
            ("stock", "Stock", 55, tk.CENTER),
            ("supplier", "Supplier", 135, tk.W),
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

        if not hasattr(self, "inv_tree") or not self.inv_tree.winfo_exists():
            return

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

        warning_expiry = (date.today() + timedelta(days=90)).strftime("%Y-%m-%d")

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

            tax_disp = f"{float(m.get('tax_rate', 5.0)):.0f}%"
            barcode_disp = m.get("barcode") or "-"

            self.inv_tree.insert("", tk.END, values=(
                m["id"], m["name"], m["generic_name"], m["category"], m["dosage_form"],
                m["schedule_type"], m["batch_no"], barcode_disp, m["expiry_date"],
                f"{m['purchase_price']:.2f}", f"{m['sale_price']:.2f}",
                tax_disp, m["stock_qty"], m.get("supplier_name") or "Direct"
            ), tags=(tag,))

        role = self.current_user_role.get()
        self.status_lbl.config(text=f"Loaded {len(medicines)} medicines. Role: {role} ({self._get_role_permission_summary(role)})")

    def _check_permission(self, allowed_roles, action_name):
        role = self.current_user_role.get()
        if role not in allowed_roles:
            messagebox.showerror(
                "Access Prohibited [Role Poka-Yoke]",
                f"Action '{action_name}' is restricted.\n\n"
                f"Current Role: {role}\n"
                f"Required Role(s): {', '.join(allowed_roles)}\n\n"
                f"Please switch role in top-right corner if authorized."
            )
            return False
        return True

    def open_add_medicine_dialog(self):
        if not self._check_permission(["Admin", "Pharmacist"], "Add Medicine"):
            return
        MedicineFormDialog(self, mode="add", on_save=self.load_inventory_data)

    def open_edit_medicine_dialog(self):
        if not self._check_permission(["Admin", "Pharmacist"], "Edit Medicine"):
            return
        selected = self.inv_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a medicine from the list to edit.")
            return
        med_id = self.inv_tree.item(selected[0])["values"][0]
        med_data = MedicineRepository.get_by_id(med_id)
        if med_data:
            MedicineFormDialog(self, mode="edit", medicine_data=med_data, on_save=self.load_inventory_data)

    def open_supplier_comparison_dialog(self):
        """User Request 5: Compare suppliers to identify best discount & lowest cost price."""
        if not self._check_permission(["Admin", "Pharmacist"], "Compare Supplier Deals"):
            return
        selected = self.inv_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a medicine to compare supplier discounts and pricing.")
            return
        med_id = self.inv_tree.item(selected[0])["values"][0]
        med_data = MedicineRepository.get_by_id(med_id)
        if med_data:
            SupplierComparisonDialog(self, med_data, on_assigned_callback=self.load_inventory_data)

    def delete_selected_medicine(self):
        """Regulatory Deletion: Strictly restricted to Admin."""
        if not self._check_permission(["Admin"], "Delete / Decommission Medicine"):
            return

        selected = self.inv_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a medicine from the list to delete.")
            return
        item_vals = self.inv_tree.item(selected[0])["values"]
        med_id, med_name = item_vals[0], item_vals[1]
        batch, stock = item_vals[6], item_vals[12]

        def confirm_delete():
            try:
                MedicineRepository.delete(med_id, user_role=self.current_user_role.get())
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
    # TAB 2: UNIFIED BILLING & POS (REQUESTS 2, 3, 4, 6)
    # =========================================================================
    def show_billing_tab(self):
        """
        Unified POS Workspace:
        - Unified search & barcode scanning bar (Request 6)
        - Differential GST tax rates per medicine (Request 3)
        - Manual customer discount in % or flat Rs. (Request 3)
        - Strict phone validation rejecting dummy numbers (Request 2)
        - Automatic patient upsert into database on sale without awkward 'Add Patient' (Request 4)
        """
        self.current_tab_name = "billing"
        self.clear_content()

        self.cart_items = []  # [{medicine_id, name, batch_no, unit_price, tax_rate, quantity, subtotal, tax_amount}]
        self.selected_med_for_cart = None

        # Top Control Header
        top_bar = ttk.Frame(self.content_area)
        top_bar.pack(fill=tk.X, pady=(0, 8))

        title = ttk.Label(top_bar, text="Unified POS Billing & Prescription Dispensing", font=("Trebuchet MS", 14, "bold"))
        title.pack(side=tk.LEFT)

        role = self.current_user_role.get()
        role_badge = tk.Label(
            top_bar, text=f"👤 Operator: {role}",
            bg="#e0f2fe", fg="#0369a1", font=("Calibri", 10, "bold"), padx=8, pady=3, relief=tk.SOLID, bd=1
        )
        role_badge.pack(side=tk.RIGHT)

        # ---------------------------------------------------------------------
        # 1. UNIFIED SEARCH & BARCODE SCANNER TOOLBAR (Request 6)
        # ---------------------------------------------------------------------
        scan_frame = ttk.LabelFrame(self.content_area, text="🔍 Unified Barcode Scanner & Rapid Search", padding=8)
        scan_frame.pack(fill=tk.X, pady=(0, 8))

        scan_box = ttk.Frame(scan_frame)
        scan_box.pack(fill=tk.X)

        ttk.Label(scan_box, text="Scan Barcode / Batch / Search:", font=("Calibri", 11, "bold")).pack(side=tk.LEFT, padx=(0, 8))
        
        self.unified_search_var = tk.StringVar()
        self.unified_search_entry = AutoCompleteEntry(
            scan_box,
            search_callback=MedicineRepository.search_autocomplete,
            on_select_callback=self._on_autocomplete_med_selected,
            width=36,
            font=("Calibri", 11)
        )
        self.unified_search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        self.unified_search_entry.bind("<Return>", self._on_barcode_or_search_enter)

        btn_find = ttk.Button(scan_box, text="⚡ Scan / Lookup", style="Action.TButton", command=self._on_barcode_or_search_enter)
        btn_find.pack(side=tk.LEFT, padx=4)

        # Quick Active Item Preview Strip
        self.preview_strip = tk.Frame(scan_frame, bg="#f1f5f9", padx=10, pady=6, relief=tk.GROOVE, bd=1)
        self.preview_strip.pack(fill=tk.X, pady=(6, 0))

        self.preview_title_lbl = tk.Label(
            self.preview_strip, text="No Medicine Selected (Scan a barcode or type medicine name/salt above)",
            bg="#f1f5f9", fg="#64748b", font=("Calibri", 10, "bold")
        )
        self.preview_title_lbl.pack(side=tk.LEFT)

        qty_action_box = tk.Frame(self.preview_strip, bg="#f1f5f9")
        qty_action_box.pack(side=tk.RIGHT)

        tk.Label(qty_action_box, text="Dispense Qty:", bg="#f1f5f9", font=("Calibri", 10, "bold")).pack(side=tk.LEFT, padx=(0, 4))
        self.dispense_qty_var = tk.StringVar(value="1")
        self.dispense_qty_entry = ttk.Entry(qty_action_box, textvariable=self.dispense_qty_var, width=6, font=("Calibri", 10))
        self.dispense_qty_entry.pack(side=tk.LEFT, padx=(0, 6))
        self.dispense_qty_entry.bind("<Return>", lambda e: self._add_to_cart())

        self.btn_add_to_cart = ttk.Button(qty_action_box, text="➕ Add to Bill", style="Success.TButton", command=self._add_to_cart)
        self.btn_add_to_cart.pack(side=tk.LEFT)

        # ---------------------------------------------------------------------
        # 2. PATIENT / CUSTOMER ROW (AUTOMATIC UPON SALE - Request 4 & Strict Phone - Request 2)
        # ---------------------------------------------------------------------
        cust_bar = ttk.LabelFrame(self.content_area, text="👤 Patient / Customer Details (Auto-Captured On Sale)", padding=8)
        cust_bar.pack(fill=tk.X, pady=(0, 8))

        c_grid = ttk.Frame(cust_bar)
        c_grid.pack(fill=tk.X)

        ttk.Label(c_grid, text="Contact Mobile (10-Digit) *:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.cust_phone_entry = PlaceholderMaskedPhoneEntry(
            c_grid, placeholder="e.g. 9876543210", width=18,
            on_phone_filled_callback=self._on_patient_phone_filled
        )
        self.cust_phone_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 15))

        ttk.Label(c_grid, text="Patient Full Name *:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.cust_name_entry = PlaceholderEntry(c_grid, placeholder="e.g. Rajesh Sharma / Walk-in", width=24)
        self.cust_name_entry.grid(row=0, column=3, sticky=tk.W, padx=(0, 15))

        ttk.Label(c_grid, text="Payment Mode:").grid(row=0, column=4, sticky=tk.W, padx=(0, 5))
        self.pay_mode_var = tk.StringVar(value="Cash")
        pay_combo = ttk.Combobox(c_grid, textvariable=self.pay_mode_var, state="readonly", width=12, values=["Cash", "Card", "UPI", "NetBanking"])
        pay_combo.grid(row=0, column=5, sticky=tk.W)

        # Patient Auto-Lookup Banner
        self.patient_status_lbl = tk.Label(
            cust_bar,
            text="💡 Tip: Entering a 10-digit mobile automatically detects returning patients or auto-saves a new record upon sale.",
            bg="#f8f9fa", fg="#475569", font=("Calibri", 9, "italic")
        )
        self.patient_status_lbl.pack(anchor=tk.W, pady=(4, 0))

        # ---------------------------------------------------------------------
        # 3. DISPENSING CART (Itemized Differential GST Taxes - Request 3)
        # ---------------------------------------------------------------------
        cart_frame = ttk.LabelFrame(self.content_area, text="🛒 Active Prescription Billing Cart", padding=8)
        cart_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        cart_cols = ("idx", "name", "batch", "barcode", "mrp", "gst", "qty", "subtotal", "tax_amt", "line_total")
        self.cart_tree = ttk.Treeview(cart_frame, columns=cart_cols, show="headings", height=7)

        self.cart_tree.heading("idx", text="#")
        self.cart_tree.heading("name", text="Medicine Name & Composition")
        self.cart_tree.heading("batch", text="Batch No")
        self.cart_tree.heading("barcode", text="Barcode")
        self.cart_tree.heading("mrp", text="MRP / Unit")
        self.cart_tree.heading("gst", text="GST Rate")
        self.cart_tree.heading("qty", text="Quantity")
        self.cart_tree.heading("subtotal", text="Base Amt (Rs.)")
        self.cart_tree.heading("tax_amt", text="Tax (Rs.)")
        self.cart_tree.heading("line_total", text="Total (Rs.)")

        self.cart_tree.column("idx", width=35, anchor=tk.CENTER)
        self.cart_tree.column("name", width=250, anchor=tk.W)
        self.cart_tree.column("batch", width=105, anchor=tk.CENTER)
        self.cart_tree.column("barcode", width=95, anchor=tk.CENTER)
        self.cart_tree.column("mrp", width=80, anchor=tk.E)
        self.cart_tree.column("gst", width=70, anchor=tk.CENTER)
        self.cart_tree.column("qty", width=65, anchor=tk.CENTER)
        self.cart_tree.column("subtotal", width=95, anchor=tk.E)
        self.cart_tree.column("tax_amt", width=80, anchor=tk.E)
        self.cart_tree.column("line_total", width=105, anchor=tk.E)

        self.cart_tree.pack(fill=tk.BOTH, expand=True)

        # ---------------------------------------------------------------------
        # 4. FINANCIAL SUMMARY & MANUAL DISCOUNT (Request 3)
        # ---------------------------------------------------------------------
        bottom_box = ttk.Frame(self.content_area)
        bottom_box.pack(fill=tk.X)

        # Left controls
        left_actions = ttk.Frame(bottom_box)
        left_actions.pack(side=tk.LEFT)

        ttk.Button(left_actions, text="❌ Remove Item", command=self._remove_cart_item).pack(side=tk.LEFT, padx=3)
        ttk.Button(left_actions, text="🧹 Clear Cart", command=self._clear_cart).pack(side=tk.LEFT, padx=3)

        # Center Discount Box (Request 3)
        disc_frame = tk.LabelFrame(bottom_box, text="🎁 Manual Customer Discount", bg="#f8f9fa", font=("Calibri", 10, "bold"), padx=8, pady=4)
        disc_frame.pack(side=tk.LEFT, padx=15)

        tk.Label(disc_frame, text="Discount:", bg="#f8f9fa", font=("Calibri", 10)).pack(side=tk.LEFT, padx=(0, 4))
        self.discount_var = tk.StringVar(value="0")
        self.disc_entry = ttk.Entry(disc_frame, textvariable=self.discount_var, width=10, font=("Calibri", 10, "bold"))
        self.disc_entry.pack(side=tk.LEFT, padx=(0, 4))
        self.disc_entry.bind("<KeyRelease>", lambda e: self._refresh_cart_view())

        tk.Label(disc_frame, text="(e.g. 10% or Rs. 50)", bg="#f8f9fa", fg="#64748b", font=("Calibri", 9)).pack(side=tk.LEFT)

        # Right Summary Box
        summary_box = ttk.Frame(bottom_box)
        summary_box.pack(side=tk.RIGHT)

        self.lbl_gross = ttk.Label(summary_box, text="Gross: Rs. 0.00", font=("Calibri", 10))
        self.lbl_gross.pack(side=tk.LEFT, padx=6)

        self.lbl_disc = ttk.Label(summary_box, text="Disc: -Rs. 0.00", font=("Calibri", 10), foreground="#0369a1")
        self.lbl_disc.pack(side=tk.LEFT, padx=6)

        self.lbl_tax = ttk.Label(summary_box, text="GST: Rs. 0.00", font=("Calibri", 10))
        self.lbl_tax.pack(side=tk.LEFT, padx=6)

        self.lbl_net = ttk.Label(summary_box, text="Net: Rs. 0.00", font=("Trebuchet MS", 13, "bold"), foreground="#005f73")
        self.lbl_net.pack(side=tk.LEFT, padx=10)

        self.btn_checkout = ttk.Button(summary_box, text="💳 Checkout & Bill", style="Success.TButton", command=self._execute_checkout)
        self.btn_checkout.pack(side=tk.LEFT, padx=5)

    def _on_barcode_or_search_enter(self, event=None):
        """Unified Scanner Bar Handler: Barcode, Batch Number, or Medicine Name."""
        query = self.unified_search_entry.get().strip()
        if not query:
            return

        # Direct barcode / batch exact search
        med = MedicineRepository.search_by_barcode_or_batch(query)
        if med:
            self._on_autocomplete_med_selected(med)
            self.dispense_qty_entry.focus_set()
            return

        # Autocomplete search fallback
        results = MedicineRepository.search_autocomplete(query)
        if results:
            self._on_autocomplete_med_selected(results[0])
            self.dispense_qty_entry.focus_set()
        else:
            messagebox.showinfo("Not Found", f"No medicine found matching barcode/batch/name: '{query}'")

    def _on_autocomplete_med_selected(self, med):
        """Populate active medicine preview bar upon scan or search match."""
        self.selected_med_for_cart = med
        tax_pct = float(med.get("tax_rate", 5.0))
        barcode_str = med.get("barcode") or "No Barcode"

        stock_color = "#15803d" if med["stock_qty"] > 10 else "#dc2626"
        self.preview_strip.config(bg="#f0fdf4" if med["stock_qty"] > 10 else "#fef2f2")
        self.preview_title_lbl.config(
            text=f"✔ {med['name']} ({med['generic_name']}) | Batch: {med['batch_no']} | Barcode: {barcode_str} | MRP: Rs. {med['sale_price']:.2f} | GST: {tax_pct:.0f}% | Stock: {med['stock_qty']} units",
            bg="#f0fdf4" if med["stock_qty"] > 10 else "#fef2f2",
            fg=stock_color
        )

    def _on_patient_phone_filled(self, phone_digits):
        """Auto-lookup customer when 10 digits are filled (User Request 4)."""
        cust = CustomerRepository.get_by_phone(phone_digits)
        if cust:
            self.cust_name_entry.set_value(cust["name"])
            self.patient_status_lbl.config(
                text=f"🟢 Verified Patient: {cust['name']} | Total Orders: {cust['total_orders']} | Lifetime Spend: Rs. {cust['total_spent']:.2f}",
                fg="#15803d"
            )
        else:
            self.patient_status_lbl.config(
                text="🆕 New Patient Profile: Record will be automatically registered in customer master on billing.",
                fg="#0369a1"
            )

    def _add_to_cart(self):
        if not self.selected_med_for_cart:
            messagebox.showwarning("Selection Required", "Please scan a barcode or select a medicine before adding to cart.")
            return

        try:
            qty = int(self.dispense_qty_var.get().strip())
        except ValueError:
            messagebox.showerror("Invalid Input", "Dispense quantity must be a valid integer.")
            return

        if qty <= 0:
            messagebox.showerror("Invalid Input", "Dispense quantity must be greater than zero.")
            return

        avail = self.selected_med_for_cart["stock_qty"]
        if qty > avail:
            messagebox.showerror(
                "Stock Insufficient",
                f"Requested quantity ({qty}) exceeds available stock ({avail} units)."
            )
            return

        # Check existing quantity in cart
        med_id = self.selected_med_for_cart["id"]
        for item in self.cart_items:
            if item["medicine_id"] == med_id:
                if item["quantity"] + qty > avail:
                    messagebox.showerror(
                        "Stock Exceeded",
                        f"Cart already holds {item['quantity']} units. Adding {qty} exceeds available stock ({avail})."
                    )
                    return
                item["quantity"] += qty
                item["subtotal"] = round(item["quantity"] * item["unit_price"], 2)
                self._refresh_cart_view()
                self._reset_scan_input()
                return

        unit_p = float(self.selected_med_for_cart["sale_price"])
        tax_r = float(self.selected_med_for_cart.get("tax_rate", 5.0))
        subtotal = round(qty * unit_p, 2)

        self.cart_items.append({
            "medicine_id": med_id,
            "name": self.selected_med_for_cart["name"],
            "batch_no": self.selected_med_for_cart["batch_no"],
            "barcode": self.selected_med_for_cart.get("barcode") or "-",
            "unit_price": unit_p,
            "tax_rate": tax_r,
            "quantity": qty,
            "subtotal": subtotal
        })

        self._reset_scan_input()
        self._refresh_cart_view()

    def _reset_scan_input(self):
        self.unified_search_entry.delete(0, tk.END)
        self.selected_med_for_cart = None
        self.dispense_qty_var.set("1")
        self.preview_strip.config(bg="#f1f5f9")
        self.preview_title_lbl.config(
            text="No Medicine Selected (Scan a barcode or type medicine name/salt above)",
            bg="#f1f5f9", fg="#64748b"
        )
        self.unified_search_entry.focus_set()

    def _refresh_cart_view(self):
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)

        gross = sum(i["subtotal"] for i in self.cart_items)

        # Parse manual discount (User Request 3)
        raw_disc = self.discount_var.get().strip() if hasattr(self, "discount_var") else "0"
        try:
            disc_amt = DataValidator.validate_discount(raw_disc, gross)
        except ValidationError:
            disc_amt = 0.0

        disc_ratio = (gross - disc_amt) / gross if gross > 0 else 1.0

        total_tax = 0.0
        for idx, item in enumerate(self.cart_items, 1):
            taxable_line = round(item["subtotal"] * disc_ratio, 2)
            item_tax = round(taxable_line * (item["tax_rate"] / 100.0), 2)
            line_net = round(taxable_line + item_tax, 2)
            total_tax += item_tax

            self.cart_tree.insert("", tk.END, values=(
                idx, item["name"], item["batch_no"], item["barcode"],
                f"{item['unit_price']:.2f}", f"{item['tax_rate']:.0f}%",
                item["quantity"], f"{item['subtotal']:.2f}",
                f"{item_tax:.2f}", f"{line_net:.2f}"
            ))

        net = round((gross - disc_amt) + total_tax, 2)

        self.lbl_gross.config(text=f"Gross: Rs. {gross:.2f}")
        self.lbl_disc.config(text=f"Disc: -Rs. {disc_amt:.2f}")
        self.lbl_tax.config(text=f"GST: Rs. {total_tax:.2f}")
        self.lbl_net.config(text=f"Net: Rs. {net:.2f}")

    def _remove_cart_item(self):
        sel = self.cart_tree.selection()
        if not sel:
            messagebox.showwarning("Select Item", "Please select a cart item to remove.")
            return
        idx = int(self.cart_tree.item(sel[0])["values"][0]) - 1
        if 0 <= idx < len(self.cart_items):
            self.cart_items.pop(idx)
            self._refresh_cart_view()

    def _clear_cart(self):
        self.cart_items = []
        self._refresh_cart_view()

    def _execute_checkout(self):
        """Checkout and Prescription Sale Execution with Poka-Yoke."""
        if not self.cart_items:
            messagebox.showwarning("Cart Empty", "Please add medicines to cart before checking out.")
            return

        cust_name = self.cust_name_entry.get_actual_value() if hasattr(self, "cust_name_entry") else ""
        if not cust_name:
            cust_name = "Walk-in Patient"

        raw_phone = self.cust_phone_entry.get_actual_value() if hasattr(self, "cust_phone_entry") else ""
        if not raw_phone:
            raw_phone = "9876543210"

        # Strict Phone Validation (User Request 2)
        try:
            cust_phone = DataValidator.validate_phone(raw_phone)
        except ValidationError as ve:
            messagebox.showerror(f"Poka-Yoke Rejection [{ve.defect_code}]", f"{ve.category}:\n\n{ve.message}")
            return

        gross = sum(i["subtotal"] for i in self.cart_items)

        # Discount validation (User Request 3)
        raw_disc = self.discount_var.get().strip() if hasattr(self, "discount_var") else "0"
        try:
            discount_amount = DataValidator.validate_discount(raw_disc, gross)
        except ValidationError as ve:
            messagebox.showerror("Invalid Discount", ve.message)
            return

        disc_ratio = (gross - discount_amount) / gross if gross > 0 else 1.0
        total_tax = sum(round(round(i["subtotal"] * disc_ratio, 2) * (i["tax_rate"] / 100.0), 2) for i in self.cart_items)
        net_payable = round((gross - discount_amount) + total_tax, 2)
        mode = self.pay_mode_var.get()
        role = self.current_user_role.get()

        # Confirmation Dialog
        summary_msg = (
            f"Dispense Prescription & Generate Tax Invoice?\n\n"
            f"• Patient: {cust_name} ({cust_phone})\n"
            f"• Medicine Lines: {len(self.cart_items)} item(s)\n"
            f"• Gross Amount: Rs. {gross:.2f}\n"
            f"• Applied Discount: Rs. {discount_amount:.2f}\n"
            f"• Itemized GST Tax: Rs. {total_tax:.2f}\n"
            f"• Net Amount Payable: Rs. {net_payable:.2f}\n"
            f"• Payment Mode: {mode}\n"
            f"• Dispensing Operator: {role}\n\n"
            f"Patient record will be automatically updated in database master."
        )

        if messagebox.askyesno("Confirm Prescription Sale", summary_msg):
            try:
                inv_no, total = SalesRepository.create_sale(
                    customer_name=cust_name,
                    customer_phone=cust_phone,
                    items=self.cart_items,
                    payment_mode=mode,
                    discount_amount=discount_amount,
                    user_role=role
                )
                messagebox.showinfo(
                    "Tax Invoice Generated",
                    f"Prescription successfully dispensed!\n\n"
                    f"Invoice Number: {inv_no}\n"
                    f"Patient Registered: {cust_name}\n"
                    f"Net Amount Collected: Rs. {total:.2f}\n\n"
                    f"Stock deducted atomically and logged in Immutable Audit Trail."
                )
                self._clear_cart()
                if hasattr(self, "cust_name_entry"):
                    self.cust_name_entry.set_value("")
                if hasattr(self, "cust_phone_entry"):
                    self.cust_phone_entry.set_value("")
                if hasattr(self, "discount_var"):
                    self.discount_var.set("0")
                if hasattr(self, "patient_status_lbl"):
                    self.patient_status_lbl.config(
                        text="💡 Tip: Entering a 10-digit mobile automatically detects returning patients or auto-saves a new record upon sale.",
                        fg="#475569"
                    )
            except Exception as e:
                messagebox.showerror("Checkout Failed", f"Transaction aborted:\n{e}")

    # =========================================================================
    # TAB 3: IMMUTABLE AUDIT TRAIL (Q07 Feature 5)
    # =========================================================================
    def show_audit_tab(self):
        self.current_tab_name = "audit"
        self.clear_content()

        top_bar = ttk.Frame(self.content_area)
        top_bar.pack(fill=tk.X, pady=(0, 10))

        title = ttk.Label(top_bar, text="Immutable Audit Trail & Historical Traceability", font=("Trebuchet MS", 14, "bold"))
        title.pack(side=tk.LEFT)

        badge = tk.Label(
            top_bar,
            text="🔒 Immutability Trigger Locked (Zero Deletes/Updates Allowed)",
            bg="#dbeafe", fg="#1e40af",
            font=("Calibri", 10, "bold"), padx=10, pady=4
        )
        badge.pack(side=tk.RIGHT)

        filter_bar = ttk.Frame(self.content_area)
        filter_bar.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(filter_bar, text="Action:").pack(side=tk.LEFT, padx=(0, 4))
        self.audit_action_var = tk.StringVar(value="All")
        action_combo = ttk.Combobox(
            filter_bar, textvariable=self.audit_action_var, state="readonly", width=12,
            values=["All", "INSERT", "UPDATE", "DELETE", "CHECKOUT"]
        )
        action_combo.pack(side=tk.LEFT, padx=(0, 12))
        action_combo.bind("<<ComboboxSelected>>", lambda e: self.load_audit_data())

        ttk.Label(filter_bar, text="Table:").pack(side=tk.LEFT, padx=(0, 4))
        self.audit_table_var = tk.StringVar(value="All")
        tbl_combo = ttk.Combobox(
            filter_bar, textvariable=self.audit_table_var, state="readonly", width=12,
            values=["All", "medicines", "suppliers", "sales", "customers"]
        )
        tbl_combo.pack(side=tk.LEFT, padx=(0, 12))
        tbl_combo.bind("<<ComboboxSelected>>", lambda e: self.load_audit_data())

        btn_refresh = ttk.Button(filter_bar, text="🔄 Refresh Logs", command=self.load_audit_data)
        btn_refresh.pack(side=tk.LEFT, padx=4)

        btn_export = ttk.Button(filter_bar, text="📥 Export Audit CSV", command=self.export_audit_csv)
        btn_export.pack(side=tk.RIGHT, padx=4)

        grid_frame = ttk.Frame(self.content_area)
        grid_frame.pack(fill=tk.BOTH, expand=True)

        cols = ("id", "timestamp", "action", "table", "record_id", "field", "old_val", "new_val", "user")
        self.audit_tree = ttk.Treeview(grid_frame, columns=cols, show="headings", selectmode="browse")

        col_defs = [
            ("id", "Log #", 50, tk.CENTER),
            ("timestamp", "Timestamp", 135, tk.CENTER),
            ("action", "Action", 85, tk.CENTER),
            ("table", "Table", 85, tk.CENTER),
            ("record_id", "Record ID", 70, tk.CENTER),
            ("field", "Field Modified", 110, tk.W),
            ("old_val", "Old Value", 160, tk.W),
            ("new_val", "New Value", 220, tk.W),
            ("user", "Operator / Role", 130, tk.W),
        ]

        for col_id, heading, width, align in col_defs:
            self.audit_tree.heading(col_id, text=heading)
            self.audit_tree.column(col_id, width=width, anchor=align)

        y_scroll = ttk.Scrollbar(grid_frame, orient=tk.VERTICAL, command=self.audit_tree.yview)
        x_scroll = ttk.Scrollbar(grid_frame, orient=tk.HORIZONTAL, command=self.audit_tree.xview)
        self.audit_tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        self.audit_tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

        grid_frame.grid_rowconfigure(0, weight=1)
        grid_frame.grid_columnconfigure(0, weight=1)

        self.audit_tree.tag_configure("INSERT", background="#f0fdf4")
        self.audit_tree.tag_configure("UPDATE", background="#fefce8")
        self.audit_tree.tag_configure("DELETE", background="#fef2f2")
        self.audit_tree.tag_configure("CHECKOUT", background="#f5f3ff")

        self.load_audit_data()

    def load_audit_data(self):
        for item in self.audit_tree.get_children():
            self.audit_tree.delete(item)

        action = self.audit_action_var.get()
        table = self.audit_table_var.get()
        logs = AuditRepository.get_all(limit=150, action_type=action, table_name=table)

        for l in logs:
            self.audit_tree.insert("", tk.END, values=(
                l["id"], l["timestamp"], l["action_type"], l["table_name"],
                l["record_id"], l["field_name"] or "-",
                l["old_value"] or "-", l["new_value"] or "-",
                l["user_role"]
            ), tags=(l["action_type"],))

        role = self.current_user_role.get()
        self.status_lbl.config(text=f"Displaying {len(logs)} audit trail entries. User: {role}. Immutability Active.")

    def export_audit_csv(self):
        logs = AuditRepository.get_all(limit=500)
        export_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports", "audit_trail_export.csv")
        os.makedirs(os.path.dirname(export_path), exist_ok=True)
        try:
            import csv
            with open(export_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["id", "timestamp", "action_type", "table_name", "record_id", "field_name", "old_value", "new_value", "user_role"])
                writer.writeheader()
                writer.writerows(logs)
            messagebox.showinfo("Export Successful", f"Audit trail exported successfully to:\n{export_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Could not export CSV:\n{e}")

    def show_sqc_tab(self):
        self.current_tab_name = "sqc"
        self.clear_content()
        lbl = ttk.Label(self.content_area, text="Statistical Quality Control (SQC) Dashboard", font=("Trebuchet MS", 14, "bold"))
        lbl.pack(anchor=tk.W, pady=5)
        ttk.Label(self.content_area, text="SQC Analytics (Pareto, Fishbone, Control Checksheets) will be integrated in Review 3/4.", font=("Calibri", 11)).pack(anchor=tk.W, pady=10)


# =============================================================================
# MEDICINE FORM DIALOG (WITH TAX RATES & BARCODES)
# =============================================================================
class MedicineFormDialog(tk.Toplevel):
    """Dialog for creating and editing medicines with Poka-Yoke field validation."""

    def __init__(self, parent, mode="add", medicine_data=None, on_save=None):
        super().__init__(parent)
        self.parent = parent
        self.mode = mode
        self.medicine_data = medicine_data or {}
        self.on_save = on_save

        self.title("Add New Medicine" if mode == "add" else f"Edit Medicine: {self.medicine_data.get('name', '')}")
        self.geometry("600x670")
        self.resizable(False, False)
        self.grab_set()

        self._build_form()

    def _build_form(self):
        frame = ttk.Frame(self, padding=18)
        frame.pack(fill=tk.BOTH, expand=True)

        header = ttk.Label(
            frame,
            text="Medicine Master Information" if self.mode == "add" else "Update Medicine Details",
            font=("Trebuchet MS", 13, "bold"),
            foreground="#005f73"
        )
        header.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 12))

        self.fields = {}
        row = 1

        default_tax = f"{float(self.medicine_data.get('tax_rate', 5.0)):.0f}%"
        if default_tax not in ["0%", "5%", "12%", "18%", "28%"]:
            default_tax = "5%"

        specs = [
            ("name", "Trade/Brand Name *", self.medicine_data.get("name", "")),
            ("generic_name", "Generic Salt Composition *", self.medicine_data.get("generic_name", "")),
            ("category", "Therapeutic Category *", self.medicine_data.get("category", "Antibiotic")),
            ("dosage_form", "Dosage Form *", self.medicine_data.get("dosage_form", "Tablet")),
            ("schedule_type", "Regulatory Schedule *", self.medicine_data.get("schedule_type", "OTC")),
            ("batch_no", "Batch Number * (Prefix: BATCH-)", self.medicine_data.get("batch_no", "")),
            ("barcode", "Barcode / EAN-13 (Optional)", self.medicine_data.get("barcode", "") or ""),
            ("expiry_date", "Expiry Date * (YYYY-MM-DD)", self.medicine_data.get("expiry_date", "")),
            ("purchase_price", "Wholesale Cost Price (Rs.) *", str(self.medicine_data.get("purchase_price", "0.00"))),
            ("sale_price", "Retail MRP Sale Price (Rs.) *", str(self.medicine_data.get("sale_price", "0.00"))),
            ("tax_rate", "GST Tax Slab % *", default_tax),
            ("stock_qty", "Stock Quantity *", str(self.medicine_data.get("stock_qty", "0"))),
            ("reorder_level", "Reorder Threshold *", str(self.medicine_data.get("reorder_level", "15"))),
        ]

        for key, label_text, default_val in specs:
            lbl = ttk.Label(frame, text=label_text)
            lbl.grid(row=row, column=0, sticky=tk.W, pady=3)

            if key == "category":
                var = tk.StringVar(value=default_val)
                widget = ttk.Combobox(frame, textvariable=var, state="readonly", values=DataValidator.VALID_CATEGORIES)
                self.fields[key] = var
            elif key == "dosage_form":
                var = tk.StringVar(value=default_val)
                widget = ttk.Combobox(frame, textvariable=var, state="readonly", values=DataValidator.VALID_DOSAGE_FORMS)
                self.fields[key] = var
            elif key == "schedule_type":
                var = tk.StringVar(value=default_val)
                widget = ttk.Combobox(frame, textvariable=var, state="readonly", values=DataValidator.VALID_SCHEDULES)
                self.fields[key] = var
            elif key == "tax_rate":
                var = tk.StringVar(value=default_val)
                widget = ttk.Combobox(frame, textvariable=var, state="readonly", values=["0%", "5%", "12%", "18%", "28%"])
                self.fields[key] = var
            elif key == "expiry_date":
                var = tk.StringVar(value=default_val)
                widget = MaskedDateEntry(frame, textvariable=var, width=32)
                self.fields[key] = var
            elif key == "batch_no":
                widget = BatchNumberWidget(frame, initial_value=default_val, width=22)
                self.fields[key] = widget
            else:
                var = tk.StringVar(value=default_val)
                widget = ttk.Entry(frame, textvariable=var, width=32)
                self.fields[key] = var

            widget.grid(row=row, column=1, sticky=tk.EW, pady=3)
            row += 1

        # Suppliers
        lbl_sup = ttk.Label(frame, text="Primary Supplier *")
        lbl_sup.grid(row=row, column=0, sticky=tk.W, pady=3)

        suppliers = SupplierRepository.get_all()
        self.supplier_map = {s["name"]: s["id"] for s in suppliers}
        default_sup_name = ""
        for name, sid in self.supplier_map.items():
            if sid == self.medicine_data.get("supplier_id"):
                default_sup_name = name
                break
        if not default_sup_name and suppliers:
            default_sup_name = suppliers[0]["name"]

        self.sup_var = tk.StringVar(value=default_sup_name)
        sup_combo = ttk.Combobox(frame, textvariable=self.sup_var, state="readonly", values=list(self.supplier_map.keys()))
        sup_combo.grid(row=row, column=1, sticky=tk.EW, pady=3)
        row += 1

        # Action Buttons
        btn_box = ttk.Frame(frame)
        btn_box.grid(row=row, column=0, columnspan=2, pady=(15, 0))

        btn_cancel = ttk.Button(btn_box, text="Cancel", command=self.destroy)
        btn_cancel.pack(side=tk.LEFT, padx=10)

        btn_submit = ttk.Button(btn_box, text="Save Medicine", style="Success.TButton", command=self.save)
        btn_submit.pack(side=tk.LEFT, padx=10)

    def save(self):
        data = {k: v.get().strip() for k, v in self.fields.items()}
        data["supplier_id"] = self.supplier_map.get(self.sup_var.get())

        if not data["name"] or not data["generic_name"]:
            messagebox.showerror("Validation Error", "Medicine Trade Name and Generic Salt Composition are mandatory fields.")
            return

        try:
            # Poka-Yoke Validations
            data["expiry_date"] = DataValidator.validate_expiry_date(data["expiry_date"], require_future=True)
            data["batch_no"] = DataValidator.validate_batch_number(data["batch_no"])
            data["purchase_price"], data["sale_price"] = DataValidator.validate_prices(data["purchase_price"], data["sale_price"])
            data["stock_qty"] = DataValidator.validate_stock_quantity(data["stock_qty"])
            data["reorder_level"] = DataValidator.validate_stock_quantity(data["reorder_level"])
            data["tax_rate"] = DataValidator.validate_tax_rate(data["tax_rate"])

            barcode = data.get("barcode", "").strip()
            data["barcode"] = barcode if barcode else None

            DataValidator.validate_enum(data["dosage_form"], DataValidator.VALID_DOSAGE_FORMS, "Dosage Form")
            DataValidator.validate_enum(data["schedule_type"], DataValidator.VALID_SCHEDULES, "Schedule Type")
            DataValidator.validate_enum(data["category"], DataValidator.VALID_CATEGORIES, "Category")

            role = self.parent.current_user_role.get()

            # Check for changes in edit mode to trigger ConfirmationModal
            if self.mode == "edit":
                deltas = {}
                for k in ["name", "generic_name", "category", "dosage_form", "schedule_type", "batch_no", "barcode", "expiry_date", "purchase_price", "sale_price", "tax_rate", "stock_qty", "reorder_level"]:
                    old_v = str(self.medicine_data.get(k, "") or "")
                    new_v = str(data.get(k, "") or "")
                    if k in ("purchase_price", "sale_price", "tax_rate"):
                        old_v = f"{float(old_v):.2f}" if old_v else "0.00"
                        new_v = f"{float(new_v):.2f}" if new_v else "0.00"
                    if old_v != new_v:
                        deltas[k.replace("_", " ").title()] = (old_v, new_v)

                if deltas:
                    def commit_edit():
                        med_id = self.medicine_data["id"]
                        MedicineRepository.update(med_id, data, user_role=role)
                        messagebox.showinfo("Success", f"Medicine '{data['name']}' updated successfully with audit trail recording.")
                        if self.on_save:
                            self.on_save()
                        self.destroy()

                    ConfirmationModal(
                        self,
                        title=f"Confirm Modifications: {data['name']}",
                        action_description=f"You are modifying {len(deltas)} parameter(s) for medicine '{data['name']}'. Review the changes below:",
                        changes_dict=deltas,
                        on_confirm=commit_edit
                    )
                    return
                else:
                    self.destroy()
                    return

            # Add mode
            MedicineRepository.create(data, user_role=role)
            messagebox.showinfo("Success", f"Medicine '{data['name']}' registered successfully with full Poka-Yoke validation.")
            if self.on_save:
                self.on_save()
            self.destroy()
        except ValidationError as ve:
            messagebox.showerror(f"Poka-Yoke Rejection [{ve.defect_code}]", f"{ve.category}:\n\n{ve.message}\n\nThis event has been logged to the SQC Defect Checksheet.")
        except Exception as e:
            messagebox.showerror("System Error", f"Could not save medicine record:\n{e}")


if __name__ == "__main__":
    app = PharmacyApp()
    app.mainloop()

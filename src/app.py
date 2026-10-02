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

"""
Custom GUI Widgets for Q07 Data Accuracy:
1. Input Masking (Date, Phone, Batch)
2. Validated Dropdown Lists
3. Dynamic Auto-Complete Search
4. Delta Confirmation Modals
BBAT104: Fundamentals of TQM (Session 2026-27)
Student: Anmol Joshi (Roll No: 2410302004, Branch: CSE-B)
"""

import re
import tkinter as tk
from tkinter import ttk, messagebox


class MaskedDateEntry(ttk.Entry):
    """Q07 Feature 1: Automatically masks and restricts date inputs to YYYY-MM-DD."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.bind("<KeyRelease>", self._format_date)

    def _format_date(self, event):
        # Ignore backspace, delete, navigation
        if event.keysym in ("BackSpace", "Delete", "Left", "Right", "Tab"):
            return

        text = self.get()
        digits = re.sub(r"\D", "", text)
        if len(digits) > 8:
            digits = digits[:8]

        formatted = ""
        if len(digits) <= 4:
            formatted = digits
        elif len(digits) <= 6:
            formatted = f"{digits[:4]}-{digits[4:]}"
        else:
            formatted = f"{digits[:4]}-{digits[4:6]}-{digits[6:]}"

        self.delete(0, tk.END)
        self.insert(0, formatted)



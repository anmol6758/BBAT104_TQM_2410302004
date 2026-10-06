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


class MaskedPhoneEntry(ttk.Entry):
    """Q07 Feature 1: Automatically formats phone numbers to (XXX) XXX-XXXX."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.bind("<KeyRelease>", self._format_phone)

    def _format_phone(self, event):
        if event.keysym in ("BackSpace", "Delete", "Left", "Right", "Tab"):
            return

        text = self.get()
        digits = re.sub(r"\D", "", text)
        if len(digits) > 10:
            digits = digits[:10]

        formatted = ""
        if len(digits) == 0:
            formatted = ""
        elif len(digits) <= 3:
            formatted = f"({digits}"
        elif len(digits) <= 6:
            formatted = f"({digits[:3]}) {digits[3:]}"
        else:
            formatted = f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"

        self.delete(0, tk.END)
        self.insert(0, formatted)


class PlaceholderEntry(ttk.Entry):
    """
    Q07 UX Enhancement:
    Displays subtle gray placeholder text when empty and unfocused.
    Clears automatically on focus without polluting actual form data.
    """

    def __init__(self, master, placeholder="", placeholder_color="#9ca3af", normal_color="#1f2937", **kwargs):
        super().__init__(master, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = placeholder_color
        self.normal_color = normal_color
        self._is_placeholder = False

        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._restore_placeholder)

        self._show_placeholder()

    def _show_placeholder(self):
        if not self.get():
            self._is_placeholder = True
            self.configure(foreground=self.placeholder_color)
            self.insert(0, self.placeholder)

    def _clear_placeholder(self, event=None):
        if self._is_placeholder:
            self._is_placeholder = False
            self.delete(0, tk.END)
            self.configure(foreground=self.normal_color)

    def _restore_placeholder(self, event=None):
        if not self.get().strip():
            self._show_placeholder()

    def get_actual_value(self):
        """Returns the actual user input, or empty string if placeholder is active."""
        if self._is_placeholder:
            return ""
        return self.get().strip()

    def set_value(self, val):
        self.delete(0, tk.END)
        if val:
            self._is_placeholder = False
            self.configure(foreground=self.normal_color)
            self.insert(0, val)
        else:
            self._show_placeholder()

    def is_placeholder_active(self):
        return self._is_placeholder


class PlaceholderMaskedPhoneEntry(ttk.Entry):
    """
    Q07 Feature 1:
    Combines Phone Input Masking with subtle gray placeholder text.
    Ensures no dummy pre-filled values pollute the checkout flow.
    """

    def __init__(self, master, placeholder="e.g. 9876543210", placeholder_color="#9ca3af", normal_color="#1f2937", **kwargs):
        super().__init__(master, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = placeholder_color
        self.normal_color = normal_color
        self._is_placeholder = False

        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._restore_placeholder)
        self.bind("<KeyRelease>", self._format_phone)

        self._show_placeholder()

    def _show_placeholder(self):
        if not self.get():
            self._is_placeholder = True
            self.configure(foreground=self.placeholder_color)
            self.insert(0, self.placeholder)

    def _clear_placeholder(self, event=None):
        if self._is_placeholder:
            self._is_placeholder = False
            self.delete(0, tk.END)
            self.configure(foreground=self.normal_color)

    def _restore_placeholder(self, event=None):
        if not self.get().strip():
            self._show_placeholder()

    def _format_phone(self, event):
        if self._is_placeholder:
            return
        if event.keysym in ("BackSpace", "Delete", "Left", "Right", "Tab"):
            return

        text = self.get()
        digits = re.sub(r"\D", "", text)
        if len(digits) > 10:
            digits = digits[:10]

        formatted = ""
        if len(digits) == 0:
            formatted = ""
        elif len(digits) <= 3:
            formatted = f"({digits}"
        elif len(digits) <= 6:
            formatted = f"({digits[:3]}) {digits[3:]}"
        else:
            formatted = f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"

        self.delete(0, tk.END)
        self.insert(0, formatted)

    def get_actual_value(self):
        if self._is_placeholder:
            return ""
        return self.get().strip()

    def set_value(self, val):
        self.delete(0, tk.END)
        if val:
            self._is_placeholder = False
            self.configure(foreground=self.normal_color)
            self.insert(0, val)
        else:
            self._show_placeholder()

    def is_placeholder_active(self):
        return self._is_placeholder


class BatchNumberWidget(ttk.Frame):
    """
    Q07 Poka-Yoke Widget (Requirement 2):
    Renders 'BATCH-' as an uneditable fixed prefix label outside the textbox.
    The user can ONLY type the alphanumeric suffix into the textbox, preventing
    accidental prefix deletion, syntax corruption, and bugs.
    """

    def __init__(self, master, initial_value="", width=24, **kwargs):
        super().__init__(master, **kwargs)
        self.prefix_lbl = tk.Label(
            self, text=" BATCH- ", font=("Calibri", 10, "bold"),
            bg="#e2e8f0", fg="#334155", relief=tk.SOLID, bd=1, padx=4, pady=2
        )
        self.prefix_lbl.pack(side=tk.LEFT)

        self.suffix_var = tk.StringVar()
        self.entry = ttk.Entry(self, textvariable=self.suffix_var, width=width, font=("Calibri", 10))
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0))
        self.entry.bind("<KeyRelease>", self._on_key)

        if initial_value:
            self.set(initial_value)

    def _on_key(self, event=None):
        raw = self.suffix_var.get().upper()
        clean = re.sub(r"[^A-Z0-9]", "", raw)
        if len(clean) > 12:
            clean = clean[:12]
        if clean != raw:
            self.suffix_var.set(clean)

    def get(self):
        """Returns the full batch number formatted as BATCH-XXXXX."""
        suffix = self.suffix_var.get().strip().upper()
        return f"BATCH-{suffix}" if suffix else ""

    def get_suffix(self):
        return self.suffix_var.get().strip().upper()

    def set(self, full_value):
        clean = str(full_value or "").strip().upper()
        if clean.startswith("BATCH-"):
            clean = clean[6:]
        clean = re.sub(r"[^A-Z0-9]", "", clean)
        self.suffix_var.set(clean)


class MaskedBatchEntry(ttk.Entry):
    """Q07 Feature 1: Enforces BATCH- prefix and uppercase alphanumeric syntax."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        if not self.get():
            self.insert(0, "BATCH-")
        self.bind("<KeyRelease>", self._format_batch)

    def _format_batch(self, event):
        if event.keysym in ("Left", "Right", "Tab"):
            return
        text = self.get().upper()
        if not text.startswith("BATCH-"):
            clean = re.sub(r"[^A-Z0-9]", "", text.replace("BATCH", ""))
            text = f"BATCH-{clean}"
        else:
            prefix = "BATCH-"
            suffix = re.sub(r"[^A-Z0-9]", "", text[6:])
            text = f"{prefix}{suffix}"

        pos = self.index(tk.INSERT)
        self.delete(0, tk.END)
        self.insert(0, text)
        self.icursor(min(pos, len(text)))



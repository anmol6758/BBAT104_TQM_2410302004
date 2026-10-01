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


class AutoCompleteEntry(ttk.Entry):
    """Q07 Feature 3: Dynamic cross-query Auto-Complete popup listbox."""

    def __init__(self, master, search_callback, on_select_callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self.search_callback = search_callback
        self.on_select_callback = on_select_callback
        self.listbox_window = None
        self.listbox = None
        self.data_items = []

        self.bind("<KeyRelease>", self._on_key_release)
        self.bind("<FocusOut>", self._on_focus_out)
        self.bind("<Down>", self._move_down)

    def _on_key_release(self, event):
        if event.keysym in ("Down", "Up", "Return", "Escape"):
            if event.keysym == "Return" and self.listbox and self.listbox.curselection():
                self._select_item()
            elif event.keysym == "Escape":
                self._close_popup()
            return

        query = self.get().strip()
        if len(query) < 2:
            self._close_popup()
            return

        results = self.search_callback(query)
        if results:
            self._show_popup(results)
        else:
            self._close_popup()

    def _show_popup(self, items):
        self.data_items = items
        if not self.listbox_window or not self.listbox_window.winfo_exists():
            self.listbox_window = tk.Toplevel(self)
            self.listbox_window.wm_overrideredirect(True)
            self.listbox = tk.Listbox(
                self.listbox_window, font=("Calibri", 10),
                height=min(6, len(items)),
                selectmode=tk.SINGLE,
                bg="#ffffff", fg="#212529",
                selectbackground="#0a9396", selectforeground="#ffffff"
            )
            self.listbox.pack(fill=tk.BOTH, expand=True)
            self.listbox.bind("<ButtonRelease-1>", lambda e: self._select_item())
            self.listbox.bind("<Return>", lambda e: self._select_item())

        # Position below the entry
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()
        w = max(self.winfo_width(), 320)
        self.listbox_window.geometry(f"{w}x{min(150, len(items)*24 + 10)}+{x}+{y}")
        self.listbox_window.lift()

        self.listbox.delete(0, tk.END)
        for item in items:
            display_str = f"{item['name']} ({item['generic_name']}) | Rs. {item['sale_price']:.2f} | Stock: {item['stock_qty']}"
            self.listbox.insert(tk.END, display_str)

    def _move_down(self, event):
        if self.listbox and self.listbox_window and self.listbox_window.winfo_exists():
            self.listbox.focus_set()
            self.listbox.selection_set(0)

    def _select_item(self):
        if self.listbox and self.listbox.curselection():
            index = self.listbox.curselection()[0]
            selected_item = self.data_items[index]
            self.delete(0, tk.END)
            self.insert(0, selected_item["name"])
            self._close_popup()
            if self.on_select_callback:
                self.on_select_callback(selected_item)

    def _on_focus_out(self, event):
        # Small delay to allow click on popup listbox
        self.after(200, self._check_focus_and_close)

    def _check_focus_and_close(self):
        if self.listbox_window and self.listbox_window.winfo_exists():
            focused = self.focus_get()
            if focused != self.listbox and focused != self:
                self._close_popup()

    def _close_popup(self):
        if self.listbox_window and self.listbox_window.winfo_exists():
            self.listbox_window.destroy()
            self.listbox_window = None
            self.listbox = None


class ConfirmationModal(tk.Toplevel):
    """Q07 Feature 4: Delta Preview Confirmation Modal before critical state commits."""

    def __init__(self, parent, title, action_description, changes_dict=None, on_confirm=None):
        super().__init__(parent)
        self.parent = parent
        self.title(title)
        self.geometry("520x400")
        self.resizable(False, False)
        self.grab_set()
        self.confirmed = False
        self.on_confirm = on_confirm

        # Build UI
        container = ttk.Frame(self, padding=20)
        container.pack(fill=tk.BOTH, expand=True)

        header = ttk.Label(container, text="⚠️ Action Confirmation Required", font=("Trebuchet MS", 12, "bold"), foreground="#d90429")
        header.pack(anchor=tk.W, pady=(0, 5))

        desc = ttk.Label(container, text=action_description, font=("Calibri", 11), wraplength=480)
        desc.pack(anchor=tk.W, pady=(0, 15))

        if changes_dict:
            tree_frame = ttk.LabelFrame(container, text="Field Modifications Delta (Poka-Yoke Inspection)", padding=8)
            tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

            cols = ("field", "old", "new")
            tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=5)
            tree.heading("field", text="Parameter")
            tree.heading("old", text="Previous Value")
            tree.heading("new", text="Proposed Value")

            tree.column("field", width=140, anchor=tk.W)
            tree.column("old", width=150, anchor=tk.CENTER)
            tree.column("new", width=150, anchor=tk.CENTER)
            tree.pack(fill=tk.BOTH, expand=True)

            for f_name, (old_v, new_v) in changes_dict.items():
                tree.insert("", tk.END, values=(f_name, str(old_v), str(new_v)))

        # Action Buttons
        btn_bar = ttk.Frame(container)
        btn_bar.pack(fill=tk.X, pady=(10, 0))

        btn_cancel = ttk.Button(btn_bar, text="✖ Cancel (Abort)", command=self.destroy)
        btn_cancel.pack(side=tk.LEFT, padx=10)

        btn_confirm = ttk.Button(btn_bar, text="✔ Confirm & Commit to Database", style="Danger.TButton", command=self._do_confirm)
        btn_confirm.pack(side=tk.RIGHT, padx=10)

    def _do_confirm(self):
        self.confirmed = True
        self.destroy()
        if self.on_confirm:
            self.on_confirm()

"""
Custom GUI Widgets for Q07 Data Accuracy:
1. Input Masking (Date, Phone, Batch)
2. Validated Dropdown Lists
3. Dynamic Auto-Complete Search
4. Delta Confirmation Modals
5. Supplier Deal Comparison Dialog
BBAT104: Fundamentals of TQM (Session 2026-27)
Student: Anmol Joshi (Roll No: 2410302004, Branch: CSE-B)
"""

import re
import tkinter as tk
from tkinter import ttk, messagebox
from src.models import SupplierDealRepository


class MaskedDateEntry(ttk.Entry):
    """Q07 Feature 1: Automatically masks and restricts date inputs to YYYY-MM-DD."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.bind("<KeyRelease>", self._format_date)

    def _format_date(self, event):
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
    Combines Phone Input Masking with subtle gray placeholder text and auto-lookup trigger.
    Ensures no dummy pre-filled values pollute the checkout flow.
    """

    def __init__(self, master, placeholder="e.g. 9876543210", placeholder_color="#9ca3af", normal_color="#1f2937", on_phone_filled_callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = placeholder_color
        self.normal_color = normal_color
        self.on_phone_filled_callback = on_phone_filled_callback
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

        # Trigger customer auto-lookup when all 10 digits are entered
        if len(digits) == 10 and self.on_phone_filled_callback:
            self.on_phone_filled_callback(digits)

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
        w = max(self.winfo_width(), 360)
        self.listbox_window.geometry(f"{w}x{min(160, len(items)*25 + 10)}+{x}+{y}")
        self.listbox_window.lift()

        self.listbox.delete(0, tk.END)
        for item in items:
            gst = item.get("tax_rate", 5.0)
            display_str = f"{item['name']} ({item['generic_name']}) | Rs. {item['sale_price']:.2f} (GST {gst}%) | Stock: {item['stock_qty']}"
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
        self.geometry("540x420")
        self.resizable(False, False)
        self.grab_set()
        self.confirmed = False
        self.on_confirm = on_confirm

        # Build UI
        container = ttk.Frame(self, padding=20)
        container.pack(fill=tk.BOTH, expand=True)

        header = ttk.Label(container, text="⚠️ Action Confirmation Required", font=("Trebuchet MS", 12, "bold"), foreground="#d90429")
        header.pack(anchor=tk.W, pady=(0, 5))

        desc = ttk.Label(container, text=action_description, font=("Calibri", 11), wraplength=490)
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


class SupplierComparisonDialog(tk.Toplevel):
    """
    TQM Procurement Advisor:
    Evaluates which supplier offers the best trade discount and lowest wholesale cost
    for any selected medicine, empowering smart purchasing decisions.
    """

    def __init__(self, parent, medicine, on_assigned_callback=None):
        super().__init__(parent)
        self.parent = parent
        self.medicine = medicine
        self.on_assigned_callback = on_assigned_callback

        self.title(f"Supplier Procurement Comparison — {medicine['name']}")
        self.geometry("780x520")
        self.resizable(False, False)
        self.grab_set()

        self._build_ui()

    def _build_ui(self):
        pad_frame = ttk.Frame(self, padding=16)
        pad_frame.pack(fill=tk.BOTH, expand=True)

        # Header Info Banner
        header_frame = ttk.Frame(pad_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        title = ttk.Label(
            header_frame,
            text=f"🏢 Supplier Discount & Price Comparison",
            font=("Trebuchet MS", 13, "bold"),
            foreground="#005f73"
        )
        title.pack(anchor=tk.W)

        sub = ttk.Label(
            header_frame,
            text=f"Medicine: {self.medicine['name']} ({self.medicine['generic_name']}) | MRP: Rs. {self.medicine['sale_price']:.2f} | Current Cost: Rs. {self.medicine['purchase_price']:.2f}",
            font=("Calibri", 10, "italic")
        )
        sub.pack(anchor=tk.W, pady=(2, 0))

        # Fetch deals from repository
        deals = SupplierDealRepository.get_deals_for_medicine(self.medicine["id"])
        self.deals = deals

        if deals and deals[0].get("is_best_deal"):
            best = deals[0]
            recommend_banner = tk.Frame(pad_frame, bg="#dcfce7", padx=10, pady=6, relief=tk.SOLID, bd=1)
            recommend_banner.pack(fill=tk.X, pady=(5, 10))

            tk.Label(
                recommend_banner,
                text=f"🏆 RECOMMENDED BEST DEAL: {best['supplier_name']} offers the highest discount ({best['discount_percent']}%)! "
                     f"Cost: Rs. {best['cost_price']:.2f}/unit (Profit Margin: {best['profit_margin_percent']}%)",
                bg="#dcfce7", fg="#15803d", font=("Calibri", 10, "bold")
            ).pack(side=tk.LEFT)

        # Table showing deals
        table_frame = ttk.Frame(pad_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        cols = ("rank", "name", "discount", "cost", "mrp", "margin", "delivery", "status")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse", height=8)

        self.tree.heading("rank", text="#")
        self.tree.heading("name", text="Supplier Name")
        self.tree.heading("discount", text="Trade Discount %")
        self.tree.heading("cost", text="Net Cost (Rs.)")
        self.tree.heading("mrp", text="Retail MRP (Rs.)")
        self.tree.heading("margin", text="Profit Margin %")
        self.tree.heading("delivery", text="Lead Days")
        self.tree.heading("status", text="Deal Rating")

        self.tree.column("rank", width=35, anchor=tk.CENTER)
        self.tree.column("name", width=220, anchor=tk.W)
        self.tree.column("discount", width=120, anchor=tk.CENTER)
        self.tree.column("cost", width=95, anchor=tk.E)
        self.tree.column("mrp", width=95, anchor=tk.E)
        self.tree.column("margin", width=95, anchor=tk.CENTER)
        self.tree.column("delivery", width=70, anchor=tk.CENTER)
        self.tree.column("status", width=110, anchor=tk.CENTER)

        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.tag_configure("best", background="#dcfce7", foreground="#15803d")
        self.tree.tag_configure("preferred", background="#e0f2fe", foreground="#0369a1")

        for idx, d in enumerate(deals, 1):
            is_best = d.get("is_best_deal", False)
            is_pref = bool(d.get("is_preferred", False))
            
            if is_best and is_pref:
                rating = "⭐ Best & Active"
                tag = "best"
            elif is_best:
                rating = "🏆 Best Discount"
                tag = "best"
            elif is_pref:
                rating = "✓ Currently Assigned"
                tag = "preferred"
            else:
                rating = "Standard Deal"
                tag = "normal"

            self.tree.insert("", tk.END, values=(
                idx,
                d["supplier_name"],
                f"{d['discount_percent']:.1f}%",
                f"Rs. {d['cost_price']:.2f}",
                f"Rs. {d['mrp']:.2f}",
                f"{d['profit_margin_percent']:.1f}%",
                f"{d['delivery_days']} Day(s)",
                rating
            ), tags=(tag,))

        # Action Buttons
        btn_bar = ttk.Frame(pad_frame)
        btn_bar.pack(fill=tk.X, pady=(5, 0))

        btn_close = ttk.Button(btn_bar, text="Close", command=self.destroy)
        btn_close.pack(side=tk.LEFT, padx=5)

        btn_apply = ttk.Button(
            btn_bar,
            text="⭐ Set Selected Supplier as Primary & Update Cost Price",
            style="Success.TButton",
            command=self._apply_preferred_supplier
        )
        btn_apply.pack(side=tk.RIGHT, padx=5)

    def _apply_preferred_supplier(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a supplier quote from the table to assign.")
            return

        idx = self.tree.index(selected[0])
        deal = self.deals[idx]

        confirm_msg = (
            f"Are you sure you want to assign '{deal['supplier_name']}' as the primary supplier for '{self.medicine['name']}'?\n\n"
            f"• Trade Discount: {deal['discount_percent']}%\n"
            f"• New Wholesale Cost Price: Rs. {deal['cost_price']:.2f}\n"
            f"• Estimated Profit Margin: {deal['profit_margin_percent']}%\n\n"
            f"This will update the purchase cost in medicine catalog and record an audit log."
        )

        if messagebox.askyesno("Confirm Procurement Order", confirm_msg):
            role = getattr(self.parent, "current_user_role", "Pharmacist")
            SupplierDealRepository.assign_supplier_to_medicine(
                self.medicine["id"], deal["supplier_id"], deal["cost_price"], user_role=role
            )
            messagebox.showinfo("Supplier Assigned", f"'{deal['supplier_name']}' is now set as the primary supplier at Rs. {deal['cost_price']:.2f}/unit.")
            self.destroy()
            if self.on_assigned_callback:
                self.on_assigned_callback()

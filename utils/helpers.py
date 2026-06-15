"""
Helpers Module
Module: helpers.py
Purpose: Shared utility functions used across multiple windows
"""

import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import re


# ==============================================
# DATE FORMATTING FUNCTIONS
# ==============================================

def format_date(date_str, input_format="%Y-%m-%d", output_format="%d %b %Y"):
    """Formats a date string nicely for display."""
    if not date_str:
        return "N/A"
    
    try:
        if isinstance(date_str, str):
            for fmt in [input_format, "%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y"]:
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    return date_obj.strftime(output_format)
                except ValueError:
                    continue
            return date_str
        elif isinstance(date_str, datetime):
            return date_str.strftime(output_format)
        else:
            return str(date_str)
    except Exception:
        return str(date_str)


def format_datetime(datetime_str, output_format="%d %b %Y %H:%M"):
    """Formats a datetime string nicely for display."""
    if not datetime_str:
        return "N/A"
    
    try:
        if isinstance(datetime_str, str):
            for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y/%m/%d %H:%M:%S"]:
                try:
                    dt_obj = datetime.strptime(datetime_str, fmt)
                    return dt_obj.strftime(output_format)
                except ValueError:
                    continue
            return datetime_str
        elif isinstance(datetime_str, datetime):
            return datetime_str.strftime(output_format)
        else:
            return str(datetime_str)
    except Exception:
        return str(datetime_str)


def get_current_date(format_str="%Y-%m-%d"):
    """Returns the current date in specified format."""
    return datetime.now().strftime(format_str)


def get_current_datetime(format_str="%Y-%m-%d %H:%M:%S"):
    """Returns the current datetime in specified format."""
    return datetime.now().strftime(format_str)


# ==============================================
# FRAME MANAGEMENT
# ==============================================

def clear_frame(frame):
    """Destroys all widgets inside a given frame."""
    if frame is None:
        return
    
    for widget in frame.winfo_children():
        widget.destroy()


def clear_widgets(widgets_list):
    """Destroys a list of specific widgets."""
    for widget in widgets_list:
        if widget and widget.winfo_exists():
            widget.destroy()


def hide_frame(frame):
    """Hides a frame (pack_forget or grid_forget based on its manager)."""
    if frame is None:
        return
    
    manager = frame.winfo_manager()
    if manager == "pack":
        frame.pack_forget()
    elif manager == "grid":
        frame.grid_forget()
    elif manager == "place":
        frame.place_forget()


def show_frame(frame, pack_kwargs=None, grid_kwargs=None):
    """Shows a previously hidden frame."""
    if frame is None:
        return
    
    manager = frame.winfo_manager()
    if manager == "pack":
        kwargs = pack_kwargs or {}
        frame.pack(**kwargs)
    elif manager == "grid":
        kwargs = grid_kwargs or {}
        frame.grid(**kwargs)


# ==============================================
# MESSAGE BOX FUNCTIONS
# ==============================================

def show_error(message, title="Error"):
    """Displays an error message dialog."""
    return messagebox.showerror(title, message)


def show_success(message, title="Success"):
    """Displays a success message dialog."""
    return messagebox.showinfo(title, message)


def show_info(message, title="Information"):
    """Displays an information message dialog."""
    return messagebox.showinfo(title, message)


def show_warning(message, title="Warning"):
    """Displays a warning message dialog."""
    return messagebox.showwarning(title, message)


def show_confirm(message, title="Confirm"):
    """Displays a confirmation dialog with Yes/No buttons."""
    return messagebox.askyesno(title, message)


def show_ok_cancel(message, title="Confirm"):
    """Displays a confirmation dialog with OK/Cancel buttons."""
    return messagebox.askokcancel(title, message)


def show_retry_cancel(message, title="Error"):
    """Displays a dialog with Retry/Cancel buttons."""
    return messagebox.askretrycancel(title, message)


# ==============================================
# TREEVIEW FUNCTIONS
# ==============================================

def treeview_select_row(tree):
    """Returns the selected row's values from a ttk.Treeview."""
    if tree is None:
        return None
    
    selection = tree.selection()
    if not selection:
        return None
    
    item = selection[0]
    values = tree.item(item, 'values')
    
    return values if values else None


def treeview_select_multiple(tree):
    """Returns all selected rows' values from a ttk.Treeview."""
    if tree is None:
        return []
    
    selection = tree.selection()
    if not selection:
        return []
    
    selected_rows = []
    for item in selection:
        values = tree.item(item, 'values')
        if values:
            selected_rows.append(values)
    
    return selected_rows


def treeview_get_item_id(tree):
    """Returns the IID (item ID) of the selected row."""
    if tree is None:
        return None
    
    selection = tree.selection()
    return selection[0] if selection else None


def treeview_clear_selection(tree):
    """Clears all selections in a treeview."""
    if tree:
        tree.selection_remove(tree.selection())


def treeview_populate(tree, columns, data, clear_first=True):
    """Populates a treeview with data."""
    if tree is None:
        return 0
    
    if clear_first:
        for item in tree.get_children():
            tree.delete(item)
    
    for row in data:
        tree.insert('', 'end', values=row)
    
    return len(data)


# ==============================================
# WINDOW MANAGEMENT
# ==============================================

def center_window(window, width, height):
    """Centers a Tk window on screen using geometry() with calculated x/y."""
    if window is None:
        return
    
    window.update_idletasks()
    
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    
    window.geometry(f"{width}x{height}+{x}+{y}")


def set_window_icon(window, icon_path=None):
    """Sets the window icon (for both tk.Tk and tk.Toplevel)."""
    if window is None:
        return
    
    try:
        if icon_path:
            window.iconbitmap(icon_path)
        else:
            pass
    except Exception:
        pass


def disable_window_resize(window):
    """Disables window resizing."""
    if window:
        window.resizable(False, False)


def set_window_to_front(window):
    """Brings window to the front."""
    if window:
        window.lift()
        window.focus_force()


# ==============================================
# STRING FORMATTING FUNCTIONS
# ==============================================

def format_currency(amount, symbol="₹"):
    """Formats a number as currency."""
    if amount is None:
        return f"{symbol} 0.00"
    
    try:
        amount = float(amount)
        return f"{symbol} {amount:,.2f}"
    except (ValueError, TypeError):
        return f"{symbol} 0.00"


def format_percentage(value, decimal_places=1):
    """Formats a number as percentage."""
    if value is None:
        return "0%"
    
    try:
        return f"{value:.{decimal_places}f}%"
    except (ValueError, TypeError):
        return "0%"


def truncate_string(text, max_length=50, suffix="..."):
    """Truncates a string if it exceeds max_length."""
    if not text:
        return ""
    
    text = str(text)
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def capitalize_words(text):
    """Capitalizes each word in a string."""
    if not text:
        return ""
    
    return ' '.join(word.capitalize() for word in str(text).split())


# ==============================================
# VALIDATION FUNCTIONS
# ==============================================

def validate_email(email):
    """Validates an email address format."""
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone):
    """Validates a phone number (10 digits)."""
    if not phone:
        return False
    
    digits = re.sub(r'\D', '', str(phone))
    return len(digits) == 10


def validate_positive_number(value, allow_zero=False):
    """Validates if a value is a positive number."""
    try:
        num = float(value)
        if allow_zero:
            return num >= 0
        return num > 0
    except (ValueError, TypeError):
        return False


def validate_required_fields(fields_dict):
    """Validates that required fields are not empty."""
    missing = [field for field, value in fields_dict.items() if not value or str(value).strip() == ""]
    return len(missing) == 0, missing


# ==============================================
# DATA CONVERSION FUNCTIONS
# ==============================================

def safe_int(value, default=0):
    """Safely converts a value to integer."""
    try:
        return int(float(value)) if value is not None else default
    except (ValueError, TypeError):
        return default


def safe_float(value, default=0.0):
    """Safely converts a value to float."""
    try:
        return float(value) if value is not None else default
    except (ValueError, TypeError):
        return default


def safe_str(value, default=""):
    """Safely converts a value to string."""
    if value is None:
        return default
    return str(value)


# ==============================================
# UI HELPER FUNCTIONS
# ==============================================

def create_labeled_entry(parent, label_text, row, column, **kwargs):
    """Creates a labeled entry widget (Label + Entry)."""
    label = ttk.Label(parent, text=label_text)
    label.grid(row=row, column=column, sticky='e', padx=5, pady=5)
    
    entry = ttk.Entry(parent, **kwargs)
    entry.grid(row=row, column=column + 1, sticky='ew', padx=5, pady=5)
    
    return label, entry


def create_labeled_combobox(parent, label_text, row, column, values, **kwargs):
    """Creates a labeled combobox widget (Label + Combobox)."""
    label = ttk.Label(parent, text=label_text)
    label.grid(row=row, column=column, sticky='e', padx=5, pady=5)
    
    combobox = ttk.Combobox(parent, values=values, **kwargs)
    combobox.grid(row=row, column=column + 1, sticky='ew', padx=5, pady=5)
    
    return label, combobox


def create_labeled_spinbox(parent, label_text, row, column, from_, to, **kwargs):
    """Creates a labeled spinbox widget (Label + Spinbox)."""
    label = ttk.Label(parent, text=label_text)
    label.grid(row=row, column=column, sticky='e', padx=5, pady=5)
    
    spinbox = ttk.Spinbox(parent, from_=from_, to=to, **kwargs)
    spinbox.grid(row=row, column=column + 1, sticky='ew', padx=5, pady=5)
    
    return label, spinbox


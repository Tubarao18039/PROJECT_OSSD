"""
TeddyShine Laundry Management System - Payments Window Module
Color Theme: Light Greenish-Gray (#E8F0E6 background style)
Module: payments_window.py
Purpose: Record payments against invoices and view payment history
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from database import get_connection, close_connection
from auth import get_current_user
from helpers import (
    show_error, show_success, show_confirm, center_window,
    format_date, format_datetime, format_currency, safe_float, safe_int,
    get_current_date, get_current_datetime
)


class PaymentsWindow(tk.Frame):
    """
    Payments Window - Record payments against invoices and view payment history.
    Provides tabs for Payment Recording and Payment History.
    """
    
    COLORS = {
        'bg': '#E8F0E6',
        'card_bg': '#FFFFFF',
        'primary': '#2E7D32',
        'primary_dark': '#1B5E20',
        'primary_light': '#4CAF50',
        'accent': '#81C784',
        'text': '#1B5E20',
        'text_secondary': '#555555',
        'text_light': '#FFFFFF',
        'border': '#C8E6C9',
        'danger': '#F44336',
        'danger_dark': '#D32F2F',
        'warning': '#FF9800',
        'success': '#4CAF50',
        'info': '#2196F3',
        'header_bg': '#F5F9F4',
        'cash_bg': '#E8F5E9',
        'card_bg_row': '#E3F2FD',
        'online_bg': '#F3E5F5'
    }
    
    PAYMENT_METHODS = ['Cash', 'Card', 'Online', 'Wallet']
    
    def __init__(self, parent, go_back_callback):
        super().__init__(parent, bg=self.COLORS['bg'])
        self.parent = parent
        self.go_back_callback = go_back_callback
        self.current_invoice_id = None
        self.current_remaining_balance = 0
        
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.create_header()
        self.create_main_content()
        
        self.load_invoices_with_balance()
        self.load_payments()
        
    def create_header(self):
        header_frame = tk.Frame(
            self,
            bg=self.COLORS['primary'],
            height=70
        )
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_propagate(False)
        
        header_frame.grid_columnconfigure(0, weight=0)
        header_frame.grid_columnconfigure(1, weight=1)
        header_frame.grid_columnconfigure(2, weight=0)
        
        back_btn = tk.Button(
            header_frame,
            text="← Back to Dashboard",
            font=('Helvetica', 11, 'bold'),
            bg=self.COLORS['primary_dark'],
            fg=self.COLORS['text_light'],
            activebackground=self.COLORS['primary'],
            activeforeground='white',
            relief='flat',
            cursor='hand2',
            padx=15,
            pady=8,
            command=self.go_back_callback
        )
        back_btn.grid(row=0, column=0, padx=20, pady=15, sticky='w')
        
        def on_enter(e):
            back_btn.config(bg=self.COLORS['primary'])
            
        def on_leave(e):
            back_btn.config(bg=self.COLORS['primary_dark'])
            
        back_btn.bind("<Enter>", on_enter)
        back_btn.bind("<Leave>", on_leave)
        
        title_label = tk.Label(
            header_frame,
            text="Payment Management",
            font=('Helvetica', 20, 'bold'),
            bg=self.COLORS['primary'],
            fg=self.COLORS['text_light']
        )
        title_label.grid(row=0, column=1, padx=20, pady=15)
        
        self.stats_label = tk.Label(
            header_frame,
            text="Total Payments: 0",
            font=('Helvetica', 11),
            bg=self.COLORS['primary'],
            fg=self.COLORS['text_light']
        )
        self.stats_label.grid(row=0, column=2, padx=20, pady=15, sticky='e')
        
    def create_main_content(self):
        main_container = tk.Frame(self, bg=self.COLORS['bg'])
        main_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill='both', expand=True)
        
        style = ttk.Style()
        style.configure('TNotebook.Tab', padding=[20, 10], font=('Helvetica', 11))
        
        self.record_frame = tk.Frame(self.notebook, bg=self.COLORS['bg'])
        self.notebook.add(self.record_frame, text="💰 Record Payment")
        self.create_record_tab()
        
        self.history_frame = tk.Frame(self.notebook, bg=self.COLORS['bg'])
        self.notebook.add(self.history_frame, text="📜 Payment History")
        self.create_history_tab()
        
    def create_record_tab(self):
        main_frame = tk.Frame(self.record_frame, bg=self.COLORS['bg'])
        main_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        left_panel = tk.Frame(main_frame, bg=self.COLORS['bg'])
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 15))
        
        right_panel = tk.Frame(main_frame, bg=self.COLORS['bg'])
        right_panel.pack(side='right', fill='both', expand=True, padx=(15, 0))
        
        self.create_invoice_selection_panel(left_panel)
        self.create_payment_form_panel(right_panel)
        
    def create_invoice_selection_panel(self, parent):
        card = tk.Frame(
            parent,
            bg=self.COLORS['card_bg'],
            relief='flat',
            highlightbackground=self.COLORS['border'],
            highlightthickness=1
        )
        card.pack(fill='both', expand=True)
        
        title_frame = tk.Frame(card, bg=self.COLORS['header_bg'])
        title_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(
            title_frame,
            text="📋 Select Invoice",
            font=('Helvetica', 14, 'bold'),
            bg=self.COLORS['header_bg'],
            fg=self.COLORS['primary']
        ).pack(pady=12)
        
        form_frame = tk.Frame(card, bg=self.COLORS['card_bg'])
        form_frame.pack(fill='both', padx=20, pady=20)
        
        tk.Label(
            form_frame,
            text="Invoice *:",
            font=('Helvetica', 11, 'bold'),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text']
        ).grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        self.invoice_combo = ttk.Combobox(
            form_frame,
            font=('Helvetica', 11),
            state='readonly',
            width=40
        )
        self.invoice_combo.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(0, 20), ipady=5)
        self.invoice_combo.bind('<<ComboboxSelected>>', self.on_invoice_select)
        
        details_frame = tk.LabelFrame(
            form_frame,
            text="Invoice Details",
            font=('Helvetica', 10, 'bold'),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['primary']
        )
        details_frame.grid(row=2, column=0, columnspan=2, sticky='ew', pady=(0, 10))
        
        tk.Label(
            details_frame,
            text="Resident:",
            font=('Helvetica', 10, 'bold'),
            bg=self.COLORS['card_bg']
        ).grid(row=0, column=0, sticky='w', padx=10, pady=(10, 5))
        
        self.resident_label = tk.Label(
            details_frame,
            text="-",
            font=('Helvetica', 10),
            bg=self.COLORS['card_bg'],
            anchor='w'
        )
        self.resident_label.grid(row=0, column=1, sticky='w', padx=10, pady=(10, 5))
        
        tk.Label(
            details_frame,
            text="Invoice Amount:",
            font=('Helvetica', 10, 'bold'),
            bg=self.COLORS['card_bg']
        ).grid(row=1, column=0, sticky='w', padx=10, pady=5)
        
        self.amount_label = tk.Label(
            details_frame,
            text="-",
            font=('Helvetica', 10),
            bg=self.COLORS['card_bg']
        )
        self.amount_label.grid(row=1, column=1, sticky='w', padx=10, pady=5)
        
        tk.Label(
            details_frame,
            text="Total Paid:",
            font=('Helvetica', 10, 'bold'),
            bg=self.COLORS['card_bg']
        ).grid(row=2, column=0, sticky='w', padx=10, pady=5)
        
        self.paid_label = tk.Label(
            details_frame,
            text="-",
            font=('Helvetica', 10),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['success']
        )
        self.paid_label.grid(row=2, column=1, sticky='w', padx=10, pady=5)
        
        tk.Label(
            details_frame,
            text="Remaining Balance:",
            font=('Helvetica', 10, 'bold'),
            bg=self.COLORS['card_bg']
        ).grid(row=3, column=0, sticky='w', padx=10, pady=5)
        
        self.balance_label = tk.Label(
            details_frame,
            text="-",
            font=('Helvetica', 10, 'bold'),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['danger']
        )
        self.balance_label.grid(row=3, column=1, sticky='w', padx=10, pady=5)
        
        tk.Label(
            details_frame,
            text="Status:",
            font=('Helvetica', 10, 'bold'),
            bg=self.COLORS['card_bg']
        ).grid(row=4, column=0, sticky='w', padx=10, pady=(5, 10))
        
        self.status_label = tk.Label(
            details_frame,
            text="-",
            font=('Helvetica', 10),
            bg=self.COLORS['card_bg']
        )
        self.status_label.grid(row=4, column=1, sticky='w', padx=10, pady=(5, 10))
        
        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_columnconfigure(1, weight=1)
        details_frame.grid_columnconfigure(0, weight=0)
        details_frame.grid_columnconfigure(1, weight=1)
        
    def create_payment_form_panel(self, parent):
        card = tk.Frame(
            parent,
            bg=self.COLORS['card_bg'],
            relief='flat',
            highlightbackground=self.COLORS['border'],
            highlightthickness=1
        )
        card.pack(fill='both', expand=True)
        
        title_frame = tk.Frame(card, bg=self.COLORS['header_bg'])
        title_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(
            title_frame,
            text="💵 Payment Information",
            font=('Helvetica', 14, 'bold'),
            bg=self.COLORS['header_bg'],
            fg=self.COLORS['primary']
        ).pack(pady=12)
        
        form_frame = tk.Frame(card, bg=self.COLORS['card_bg'])
        form_frame.pack(fill='both', padx=25, pady=25)
        
        tk.Label(
            form_frame,
            text="Payment Amount *:",
            font=('Helvetica', 11, 'bold'),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text']
        ).grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        amount_frame = tk.Frame(form_frame, bg=self.COLORS['card_bg'])
        amount_frame.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(0, 15))
        
        self.amount_entry = tk.Entry(
            amount_frame,
            font=('Helvetica', 14),
            bg='#FAFAFA',
            relief='solid',
            bd=1,
            width=20
        )
        self.amount_entry.pack(side='left', ipady=8)
        
        tk.Label(
            amount_frame,
            text="(Max: ₹0.00)",
            font=('Helvetica', 9),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text_secondary']
        ).pack(side='left', padx=(10, 0))
        
        tk.Label(
            form_frame,
            text="Payment Method *:",
            font=('Helvetica', 11, 'bold'),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text']
        ).grid(row=2, column=0, sticky='w', pady=(0, 5))
        
        self.method_combo = ttk.Combobox(
            form_frame,
            values=self.PAYMENT_METHODS,
            state='readonly',
            font=('Helvetica', 11),
            width=25
        )
        self.method_combo.grid(row=3, column=0, columnspan=2, sticky='w', pady=(0, 15), ipady=5)
        self.method_combo.set('Cash')
        
        tk.Label(
            form_frame,
            text="Payment Date *:",
            font=('Helvetica', 11, 'bold'),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text']
        ).grid(row=4, column=0, sticky='w', pady=(0, 5))
        
        date_frame = tk.Frame(form_frame, bg=self.COLORS['card_bg'])
        date_frame.grid(row=5, column=0, columnspan=2, sticky='w', pady=(0, 15))
        
        self.date_var = tk.StringVar(value=get_current_date())
        self.date_entry = tk.Entry(
            date_frame,
            textvariable=self.date_var,
            font=('Helvetica', 11),
            bg='#FAFAFA',
            relief='solid',
            bd=1,
            width=20
        )
        self.date_entry.pack(side='left', ipady=5)
        
        tk.Label(
            date_frame,
            text="(YYYY-MM-DD)",
            font=('Helvetica', 9),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text_secondary']
        ).pack(side='left', padx=(10, 0))
        
        tk.Label(
            form_frame,
            text="Transaction ID (Optional):",
            font=('Helvetica', 10),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text']
        ).grid(row=6, column=0, sticky='w', pady=(0, 5))
        
        self.transaction_entry = tk.Entry(
            form_frame,
            font=('Helvetica', 11),
            bg='#FAFAFA',
            relief='solid',
            bd=1,
            width=30
        )
        self.transaction_entry.grid(row=7, column=0, columnspan=2, sticky='ew', pady=(0, 15), ipady=5)
        
        tk.Label(
            form_frame,
            text="Notes:",
            font=('Helvetica', 10),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text']
        ).grid(row=8, column=0, sticky='w', pady=(0, 5))
        
        self.notes_text = tk.Text(
            form_frame,
            font=('Helvetica', 10),
            bg='#FAFAFA',
            relief='solid',
            bd=1,
            height=3,
            width=40
        )
        self.notes_text.grid(row=9, column=0, columnspan=2, sticky='ew', pady=(0, 20))
        
        self.record_btn = tk.Button(
            form_frame,
            text="✅ Record Payment",
            font=('Helvetica', 12, 'bold'),
            bg=self.COLORS['success'],
            fg='white',
            activebackground='#45A049',
            activeforeground='white',
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=10,
            command=self.record_payment
        )
        self.record_btn.grid(row=10, column=0, columnspan=2, sticky='ew', pady=(10, 0))
        
        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_columnconfigure(1, weight=0)
        
    def create_history_tab(self):
        main_frame = tk.Frame(self.history_frame, bg=self.COLORS['bg'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        filter_frame = tk.Frame(main_frame, bg=self.COLORS['card_bg'], relief='flat')
        filter_frame.pack(fill='x', pady=(0, 15), ipady=10)
        
        tk.Label(
            filter_frame,
            text="Filter by Method:",
            font=('Helvetica', 10, 'bold'),
            bg=self.COLORS['card_bg']
        ).pack(side='left', padx=(15, 10))
        
        self.method_filter = ttk.Combobox(
            filter_frame,
            values=['All'] + self.PAYMENT_METHODS,
            state='readonly',
            width=15
        )
        self.method_filter.set('All')
        self.method_filter.pack(side='left', padx=(0, 15))
        self.method_filter.bind('<<ComboboxSelected>>', lambda e: self.load_payments())
        
        tk.Label(
            filter_frame,
            text="Search:",
            font=('Helvetica', 10),
            bg=self.COLORS['card_bg']
        ).pack(side='left', padx=(10, 10))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.load_payments())
        
        search_entry = tk.Entry(
            filter_frame,
            textvariable=self.search_var,
            font=('Helvetica', 10),
            bg='#FAFAFA',
            relief='solid',
            bd=1,
            width=20
        )
        search_entry.pack(side='left', fill='x', expand=True, ipady=5)
        
        refresh_btn = tk.Button(
            filter_frame,
            text="🔄 Refresh",
            font=('Helvetica', 10),
            bg=self.COLORS['info'],
            fg='white',
            relief='flat',
            cursor='hand2',
            padx=15,
            pady=5,
            command=self.load_payments
        )
        refresh_btn.pack(side='right', padx=15)
        
        tree_frame = tk.Frame(main_frame)
        tree_frame.pack(fill='both', expand=True)
        
        columns = ('ID', 'Invoice No', 'Resident', 'Date', 'Amount', 'Method', 'Transaction ID', 'Status')
        self.payment_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=14)
        
        self.payment_tree.heading('ID', text='ID')
        self.payment_tree.heading('Invoice No', text='Invoice No')
        self.payment_tree.heading('Resident', text='Resident')
        self.payment_tree.heading('Date', text='Date')
        self.payment_tree.heading('Amount', text='Amount')
        self.payment_tree.heading('Method', text='Method')
        self.payment_tree.heading('Transaction ID', text='Transaction ID')
        self.payment_tree.heading('Status', text='Status')
        
        self.payment_tree.column('ID', width=50, anchor='center')
        self.payment_tree.column('Invoice No', width=100, anchor='center')
        self.payment_tree.column('Resident', width=150)
        self.payment_tree.column('Date', width=100, anchor='center')
        self.payment_tree.column('Amount', width=100, anchor='center')
        self.payment_tree.column('Method', width=100, anchor='center')
        self.payment_tree.column('Transaction ID', width=120, anchor='center')
        self.payment_tree.column('Status', width=100, anchor='center')
        
        self.payment_tree.tag_configure('Cash', background=self.COLORS['cash_bg'])
        self.payment_tree.tag_configure('Card', background=self.COLORS['card_bg_row'])
        self.payment_tree.tag_configure('Online', background=self.COLORS['online_bg'])
        self.payment_tree.tag_configure('Wallet', background=self.COLORS['header_bg'])
        
        v_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.payment_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.payment_tree.xview)
        self.payment_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.payment_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        legend_frame = tk.Frame(main_frame, bg=self.COLORS['card_bg'])
        legend_frame.pack(fill='x', pady=(10, 0), ipady=5)
        
        tk.Label(
            legend_frame,
            text="Legend:",
            font=('Helvetica', 9, 'bold'),
            bg=self.COLORS['card_bg']
        ).pack(side='left', padx=(15, 10))
        
        legend_items = [
            ('Cash', self.COLORS['cash_bg']),
            ('Card', self.COLORS['card_bg_row']),
            ('Online', self.COLORS['online_bg'])
        ]
        
        for text, color in legend_items:
            frame = tk.Frame(legend_frame, bg=self.COLORS['card_bg'])
            frame.pack(side='left', padx=10)
            
            box = tk.Frame(frame, bg=color, width=15, height=15)
            box.pack(side='left', padx=(0, 5))
            
            label = tk.Label(frame, text=text, font=('Helvetica', 9), bg=self.COLORS['card_bg'])
            label.pack(side='left')
            
    def load_invoices_with_balance(self):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT i.invoice_id, i.invoice_number, i.total_amount, i.amount_paid,
                       i.balance_due, i.status, r.full_name, o.order_number
                FROM Invoice i
                JOIN Orders o ON i.order_id = o.order_id
                JOIN Resident r ON o.resident_id = r.resident_id
                WHERE i.status IN ('Unpaid', 'Partial')
                ORDER BY i.invoice_id DESC
            """)
            invoices = cursor.fetchall()
            
            self.invoice_list = []
            for inv in invoices:
                display_text = f"{inv['invoice_number']} - {inv['full_name']} (Balance: {format_currency(inv['balance_due'])})"
                self.invoice_list.append({
                    'id': inv['invoice_id'],
                    'number': inv['invoice_number'],
                    'resident': inv['full_name'],
                    'total': inv['total_amount'],
                    'paid': inv['amount_paid'],
                    'balance': inv['balance_due'],
                    'status': inv['status'],
                    'display': display_text
                })
            
            self.invoice_combo['values'] = [inv['display'] for inv in self.invoice_list]
            
        except Exception as e:
            print(f"[PaymentsWindow] Error loading invoices: {e}")
        finally:
            close_connection(conn)
            
    def on_invoice_select(self, event=None):
        selection = self.invoice_combo.current()
        if selection < 0:
            return
            
        invoice = self.invoice_list[selection]
        self.current_invoice_id = invoice['id']
        self.current_remaining_balance = invoice['balance']
        
        self.resident_label.config(text=invoice['resident'])
        self.amount_label.config(text=format_currency(invoice['total']))
        self.paid_label.config(text=format_currency(invoice['paid']))
        self.balance_label.config(text=format_currency(invoice['balance']))
        
        status_emoji = "⚠️" if invoice['status'] == 'Partial' else "❌"
        self.status_label.config(text=f"{status_emoji} {invoice['status']}")
        
        max_hint = f"(Max: {format_currency(invoice['balance'])})"
        for widget in self.amount_entry.master.winfo_children():
            if isinstance(widget, tk.Label) and widget.cget('text').startswith('(Max:'):
                widget.config(text=max_hint)
                
        self.amount_entry.delete(0, tk.END)
        self.transaction_entry.delete(0, tk.END)
        self.notes_text.delete("1.0", tk.END)
        
    def validate_payment(self):
        if not self.current_invoice_id:
            show_error("Please select an invoice first")
            return False
            
        amount_str = self.amount_entry.get().strip()
        if not amount_str:
            show_error("Please enter payment amount")
            return False
            
        try:
            amount = safe_float(amount_str)
            if amount <= 0:
                show_error("Payment amount must be greater than 0")
                return False
                
            if amount > self.current_remaining_balance:
                show_error(f"Payment amount cannot exceed remaining balance of {format_currency(self.current_remaining_balance)}")
                return False
                
        except ValueError:
            show_error("Please enter a valid payment amount")
            return False
            
        method = self.method_combo.get()
        if not method:
            show_error("Please select a payment method")
            return False
            
        payment_date = self.date_var.get().strip()
        if not payment_date:
            show_error("Please enter payment date")
            return False
            
        try:
            datetime.strptime(payment_date, "%Y-%m-%d")
        except ValueError:
            show_error("Please enter payment date in YYYY-MM-DD format")
            return False
            
        return True
        
    def update_invoice_status(self, invoice_id, new_paid_amount):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT total_amount, amount_paid, balance_due, status
                FROM Invoice WHERE invoice_id = ?
            """, (invoice_id,))
            invoice = cursor.fetchone()
            
            if not invoice:
                return False
                
            new_total_paid = invoice['amount_paid'] + new_paid_amount
            new_balance = invoice['total_amount'] - new_total_paid
            
            if new_balance <= 0:
                new_status = 'Paid'
                paid_date = get_current_datetime()
            elif new_total_paid > 0:
                new_status = 'Partial'
                paid_date = None
            else:
                new_status = 'Unpaid'
                paid_date = None
                
            cursor.execute("""
                UPDATE Invoice
                SET amount_paid = ?, balance_due = ?, status = ?, paid_date = ?
                WHERE invoice_id = ?
            """, (new_total_paid, new_balance, new_status, paid_date, invoice_id))
            conn.commit()
            
            return True
            
        except Exception as e:
            print(f"[PaymentsWindow] Error updating invoice status: {e}")
            return False
        finally:
            close_connection(conn)
            
    def record_payment(self):
        if not self.validate_payment():
            return
            
        amount = safe_float(self.amount_entry.get())
        method = self.method_combo.get()
        payment_date = self.date_var.get()
        transaction_id = self.transaction_entry.get().strip() or None
        notes = self.notes_text.get("1.0", tk.END).strip() or None
        
        if not transaction_id:
            transaction_id = f"TXN-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
        current_user = get_current_user()
        
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO Payments (invoice_id, order_id, amount, payment_method,
                                     payment_date, transaction_id, status, notes)
                SELECT ?, o.order_id, ?, ?, ?, ?, 'Completed', ?
                FROM Invoice i
                JOIN Orders o ON i.order_id = o.order_id
                WHERE i.invoice_id = ?
            """, (self.current_invoice_id, amount, method, payment_date,
                  transaction_id, notes, self.current_invoice_id))
            
            conn.commit()
            
            self.update_invoice_status(self.current_invoice_id, amount)
            
            show_success(f"Payment of {format_currency(amount)} recorded successfully!\nTransaction ID: {transaction_id}")
            
            self.load_invoices_with_balance()
            self.load_payments()
            
            self.invoice_combo.set('')
            self.resident_label.config(text="-")
            self.amount_label.config(text="-")
            self.paid_label.config(text="-")
            self.balance_label.config(text="-")
            self.status_label.config(text="-")
            self.amount_entry.delete(0, tk.END)
            self.transaction_entry.delete(0, tk.END)
            self.notes_text.delete("1.0", tk.END)
            self.current_invoice_id = None
            
            self.notebook.select(1)
            
        except Exception as e:
            print(f"[PaymentsWindow] Error recording payment: {e}")
            show_error(f"Failed to record payment: {str(e)}")
            conn.rollback()
        finally:
            close_connection(conn)
            
    def load_payments(self):
        for item in self.payment_tree.get_children():
            self.payment_tree.delete(item)
            
        method_filter = self.method_filter.get()
        search_term = self.search_var.get().strip()
        
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            query = """
                SELECT p.payment_id, p.invoice_id, i.invoice_number, r.full_name,
                       p.payment_date, p.amount, p.payment_method, p.transaction_id, p.status
                FROM Payments p
                JOIN Invoice i ON p.invoice_id = i.invoice_id
                JOIN Orders o ON i.order_id = o.order_id
                JOIN Resident r ON o.resident_id = r.resident_id
                WHERE 1=1
            """
            params = []
            
            if method_filter != 'All':
                query += " AND p.payment_method = ?"
                params.append(method_filter)
                
            if search_term:
                query += " AND (i.invoice_number LIKE ? OR r.full_name LIKE ? OR p.transaction_id LIKE ?)"
                search_pattern = f"%{search_term}%"
                params.extend([search_pattern, search_pattern, search_pattern])
                
            query += " ORDER BY p.payment_id DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            for row in rows:
                self.payment_tree.insert('', 'end', values=(
                    row['payment_id'],
                    row['invoice_number'],
                    row['full_name'],
                    format_date(row['payment_date']),
                    format_currency(row['amount']),
                    row['payment_method'],
                    row['transaction_id'] or 'N/A',
                    row['status']
                ), tags=(row['payment_method'],))
                
            self.stats_label.config(text=f"Total Payments: {len(rows)}")
            
        except Exception as e:
            print(f"[PaymentsWindow] Error loading payments: {e}")
            show_error(f"Failed to load payment history: {str(e)}")
        finally:
            close_connection(conn)
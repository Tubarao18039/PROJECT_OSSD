import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

from database import get_connection, close_connection
from auth import is_admin, get_current_user
from helpers import (
    show_error, show_success, show_confirm, center_window,
    format_date, format_currency, safe_int, safe_float
)


class OrdersWindow(tk.Frame):
    """Provides tabs for New Order creation and View/Manage existing orders."""
    
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
        'header_bg': '#F5F9F4'      
    }
    
    ORDER_STATUSES = ['Pending', 'Processing', 'Completed', 'Cancelled', 'Delivered']
    
    def __init__(self, parent, go_back_callback):

        super().__init__(parent, bg=self.COLORS['bg'])
        self.parent = parent
        self.go_back_callback = go_back_callback
        
        self.order_items = []
        self.current_total = 0.0
        
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=1)  # Main content
        self.grid_columnconfigure(0, weight=1)
        
        # Create UI sections
        self.create_header()
        self.create_main_content()
        
        self.load_residents()
        self.load_staff()
        self.load_delivery_slots()
        self.load_services()
        self.load_orders()
        
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
        
        # Hover effect
        def on_enter(e):
            back_btn.config(bg=self.COLORS['primary'])
            
        def on_leave(e):
            back_btn.config(bg=self.COLORS['primary_dark'])
            
        back_btn.bind("<Enter>", on_enter)
        back_btn.bind("<Leave>", on_leave)
        
        title_label = tk.Label(
            header_frame,
            text="Order Management",
            font=('Helvetica', 20, 'bold'),
            bg=self.COLORS['primary'],
            fg=self.COLORS['text_light']
        )
        title_label.grid(row=0, column=1, padx=20, pady=15)
        
        # Stats label (will be updated)
        self.stats_label = tk.Label(
            header_frame,
            text="Total Orders: 0",
            font=('Helvetica', 11),
            bg=self.COLORS['primary'],
            fg=self.COLORS['text_light']
        )
        self.stats_label.grid(row=0, column=2, padx=20, pady=15, sticky='e')
        
    def create_main_content(self):
        """Creates the main content area with notebook tabs."""
        main_container = tk.Frame(self, bg=self.COLORS['bg'])
        main_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        
        # Create Notebook
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill='both', expand=True)
        
        style = ttk.Style()
        style.configure('TNotebook.Tab', padding=[20, 10], font=('Helvetica', 11))
        
        # Tab 1: New Order
        self.new_order_frame = tk.Frame(self.notebook, bg=self.COLORS['bg'])
        self.notebook.add(self.new_order_frame, text="📝 New Order")
        self.create_new_order_tab()
        
        # Tab 2: View Orders
        self.view_orders_frame = tk.Frame(self.notebook, bg=self.COLORS['bg'])
        self.notebook.add(self.view_orders_frame, text="📋 View Orders")
        self.create_view_orders_tab()
        
    def create_new_order_tab(self):
        """Creates the New Order form tab."""

        main_frame = tk.Frame(self.new_order_frame, bg=self.COLORS['bg'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Left Panel - Order Details
        left_panel = tk.Frame(main_frame, bg=self.COLORS['bg'])
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Right Panel - Order Items
        right_panel = tk.Frame(main_frame, bg=self.COLORS['bg'])
        right_panel.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        self.create_order_details_panel(left_panel)
        self.create_order_items_panel(right_panel)
        
    def create_order_details_panel(self, parent):
        """Creates the order details form panel."""
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
            text="📋 Order Information",
            font=('Helvetica', 14, 'bold'),
            bg=self.COLORS['header_bg'],
            fg=self.COLORS['primary']
        ).pack(pady=12)
        
        form_frame = tk.Frame(card, bg=self.COLORS['card_bg'])
        form_frame.pack(fill='both', padx=20, pady=15)
        
        # Resident Selection
        tk.Label(
            form_frame, text="Resident *:",
            font=('Helvetica', 10, 'bold'),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text']
        ).grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        self.resident_combo = ttk.Combobox(
            form_frame,
            font=('Helvetica', 10),
            state='readonly',
            width=35
        )
        self.resident_combo.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(0, 15), ipady=5)
        
        # Staff Selection
        tk.Label(
            form_frame, text="Assign Staff:",
            font=('Helvetica', 10, 'bold'),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text']
        ).grid(row=2, column=0, sticky='w', pady=(0, 5))
        
        self.staff_combo = ttk.Combobox(
            form_frame,
            font=('Helvetica', 10),
            state='readonly',
            width=35
        )
        self.staff_combo.grid(row=3, column=0, columnspan=2, sticky='ew', pady=(0, 15), ipady=5)
        
        # Delivery Slot Selection
        tk.Label(
            form_frame, text="Delivery Slot *:",
            font=('Helvetica', 10, 'bold'),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text']
        ).grid(row=4, column=0, sticky='w', pady=(0, 5))
        
        self.slot_combo = ttk.Combobox(
            form_frame,
            font=('Helvetica', 10),
            state='readonly',
            width=35
        )
        self.slot_combo.grid(row=5, column=0, columnspan=2, sticky='ew', pady=(0, 15), ipady=5)
        
        # Weight 
        tk.Label(
            form_frame, text="Total Weight (kg):",
            font=('Helvetica', 10),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text']
        ).grid(row=6, column=0, sticky='w', pady=(0, 5))
        
        self.weight_entry = tk.Entry(
            form_frame,
            font=('Helvetica', 10),
            bg='#FAFAFA',
            relief='solid',
            bd=1,
            width=20
        )
        self.weight_entry.grid(row=7, column=0, sticky='w', pady=(0, 15), ipady=5)
        
        # Special Instructions
        tk.Label(
            form_frame, text="Special Instructions:",
            font=('Helvetica', 10),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text']
        ).grid(row=8, column=0, sticky='w', pady=(0, 5))
        
        self.instructions_text = tk.Text(
            form_frame,
            font=('Helvetica', 10),
            bg='#FAFAFA',
            relief='solid',
            bd=1,
            height=4,
            width=35
        )
        self.instructions_text.grid(row=9, column=0, columnspan=2, sticky='ew', pady=(0, 15))
        
        # Place Order Button
        self.place_order_btn = tk.Button(
            form_frame,
            text="✅ Place Order",
            font=('Helvetica', 12, 'bold'),
            bg=self.COLORS['success'],
            fg='white',
            activebackground='#45A049',
            activeforeground='white',
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=10,
            command=self.place_order
        )
        self.place_order_btn.grid(row=10, column=0, columnspan=2, pady=(10, 0), sticky='ew')
        
        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_columnconfigure(1, weight=0)
        
    def create_order_items_panel(self, parent):
        """Creates the order items selection panel."""
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
            text="🛍️ Order Items",
            font=('Helvetica', 14, 'bold'),
            bg=self.COLORS['header_bg'],
            fg=self.COLORS['primary']
        ).pack(pady=12)
        
        # Add item section
        add_frame = tk.Frame(card, bg=self.COLORS['card_bg'])
        add_frame.pack(fill='x', padx=20, pady=10)
        
        # Service selection
        tk.Label(
            add_frame, text="Service:",
            font=('Helvetica', 10),
            bg=self.COLORS['card_bg']
        ).grid(row=0, column=0, sticky='w', padx=(0, 10))
        
        self.service_combo = ttk.Combobox(
            add_frame,
            font=('Helvetica', 10),
            state='readonly',
            width=25
        )
        self.service_combo.grid(row=0, column=1, padx=(0, 10), sticky='ew')
        
        # Quantity
        tk.Label(
            add_frame, text="Qty:",
            font=('Helvetica', 10),
            bg=self.COLORS['card_bg']
        ).grid(row=0, column=2, sticky='w', padx=(0, 10))
        
        self.qty_spinbox = tk.Spinbox(
            add_frame,
            from_=1,
            to=99,
            width=5,
            font=('Helvetica', 10)
        )
        self.qty_spinbox.grid(row=0, column=3, padx=(0, 10))
        
        # Add button
        add_item_btn = tk.Button(
            add_frame,
            text="➕ Add Item",
            font=('Helvetica', 10, 'bold'),
            bg=self.COLORS['primary'],
            fg='white',
            activebackground=self.COLORS['primary_dark'],
            relief='flat',
            cursor='hand2',
            padx=10,
            pady=5,
            command=self.add_item_to_list
        )
        add_item_btn.grid(row=0, column=4, padx=(10, 0))
        
        add_frame.grid_columnconfigure(1, weight=1)
        
        # Items listbox with scrollbar
        list_frame = tk.Frame(card, bg=self.COLORS['card_bg'])
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.items_listbox = tk.Listbox(
            list_frame,
            font=('Helvetica', 10),
            bg='#FAFAFA',
            yscrollcommand=scrollbar.set,
            height=10
        )
        self.items_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.items_listbox.yview)
        
        # Remove item button
        remove_btn = tk.Button(
            card,
            text="🗑️ Remove Selected Item",
            font=('Helvetica', 10),
            bg=self.COLORS['danger'],
            fg='white',
            activebackground=self.COLORS['danger_dark'],
            relief='flat',
            cursor='hand2',
            padx=10,
            pady=5,
            command=self.remove_item
        )
        remove_btn.pack(pady=(5, 10))
        
        # Total amount display
        total_frame = tk.Frame(card, bg=self.COLORS['header_bg'])
        total_frame.pack(fill='x', padx=20, pady=(10, 20))
        
        tk.Label(
            total_frame,
            text="Total Amount:",
            font=('Helvetica', 12, 'bold'),
            bg=self.COLORS['header_bg'],
            fg=self.COLORS['text']
        ).pack(side='left', padx=10, pady=10)
        
        self.total_label = tk.Label(
            total_frame,
            text="₹ 0.00",
            font=('Helvetica', 16, 'bold'),
            bg=self.COLORS['header_bg'],
            fg=self.COLORS['primary']
        )
        self.total_label.pack(side='right', padx=10, pady=10)
        
    def create_view_orders_tab(self):
        """Creates the View Orders tab with filtering and management."""
        
        main_frame = tk.Frame(self.view_orders_frame, bg=self.COLORS['bg'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Filter bar
        filter_frame = tk.Frame(main_frame, bg=self.COLORS['card_bg'], relief='flat')
        filter_frame.pack(fill='x', pady=(0, 15), ipady=10)
        
        tk.Label(
            filter_frame,
            text="Filter by Status:",
            font=('Helvetica', 10, 'bold'),
            bg=self.COLORS['card_bg']
        ).pack(side='left', padx=(15, 10))
        
        self.status_filter = ttk.Combobox(
            filter_frame,
            values=['All'] + self.ORDER_STATUSES,
            state='readonly',
            width=15
        )
        self.status_filter.set('All')
        self.status_filter.pack(side='left', padx=(0, 15))
        self.status_filter.bind('<<ComboboxSelected>>', lambda e: self.load_orders())
        
        # Refresh button
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
            command=self.load_orders
        )
        refresh_btn.pack(side='right', padx=15)
        
        # Treeview frame
        tree_frame = tk.Frame(main_frame)
        tree_frame.pack(fill='both', expand=True)
        
        
        columns = ('Order ID', 'Order No', 'Resident', 'Date', 'Delivery Date', 'Amount', 'Status')
        self.orders_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # Define headings
        self.orders_tree.heading('Order ID', text='ID')
        self.orders_tree.heading('Order No', text='Order No')
        self.orders_tree.heading('Resident', text='Resident')
        self.orders_tree.heading('Date', text='Order Date')
        self.orders_tree.heading('Delivery Date', text='Delivery Date')
        self.orders_tree.heading('Amount', text='Amount')
        self.orders_tree.heading('Status', text='Status')
        
        # Define column widths
        self.orders_tree.column('Order ID', width=50, anchor='center')
        self.orders_tree.column('Order No', width=100, anchor='center')
        self.orders_tree.column('Resident', width=150)
        self.orders_tree.column('Date', width=100, anchor='center')
        self.orders_tree.column('Delivery Date', width=100, anchor='center')
        self.orders_tree.column('Amount', width=100, anchor='center')
        self.orders_tree.column('Status', width=100, anchor='center')
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.orders_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.orders_tree.xview)
        self.orders_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        

        self.orders_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        

        action_frame = tk.Frame(main_frame, bg=self.COLORS['bg'])
        action_frame.pack(fill='x', pady=(15, 0))
        
        # Mark Complete button
        self.complete_btn = tk.Button(
            action_frame,
            text="✅ Mark as Completed",
            font=('Helvetica', 11, 'bold'),
            bg=self.COLORS['success'],
            fg='white',
            activebackground='#45A049',
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=8,
            command=self.mark_complete
        )
        self.complete_btn.pack(side='left', padx=5)
        
        # Delete Order button
        self.delete_order_btn = tk.Button(
            action_frame,
            text="🗑️ Delete Order",
            font=('Helvetica', 11, 'bold'),
            bg=self.COLORS['danger'],
            fg='white',
            activebackground=self.COLORS['danger_dark'],
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=8,
            command=self.delete_order
        )
        self.delete_order_btn.pack(side='left', padx=5)
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from database import get_connection, close_connection
from auth import is_admin, get_current_user
from helpers import (
    show_error, show_success, show_confirm, center_window,
    format_datetime, safe_int, get_current_datetime
)
class TrackingWindow(tk.Frame):
# Modern color theme
    COLORS = {
        'bg': '#E8F0E6',           # Light greenish-gray background
        'card_bg': '#FFFFFF',       # White for cards
        'primary': '#2E7D32',       # Dark green
        'primary_dark': '#1B5E20',  # Darker green for hover
        'primary_light': '#4CAF50', # Light green
        'accent': '#81C784',        # Soft green accent
        'text': '#1B5E20',          # Dark green text
        'text_secondary': '#555555', # Secondary text
        'text_light': '#FFFFFF',    # Light text for buttons
        'border': '#C8E6C9',        # Light green border
        'danger': '#F44336',        # Danger red
        'danger_dark': '#D32F2F',   # Darker red
        'warning': '#FF9800',       # Warning orange
        'success': '#4CAF50',       # Success green
        'info': '#2196F3',          # Info blue
        'header_bg': '#F5F9F4',     # Light header background
        'in_progress_bg': '#FFF3E0', # Light orange for in-progress rows
        'in_progress_fg': '#E65100', # Dark orange text
        'completed_bg': '#E8F5E9',   # Light green for completed rows
        'completed_fg': '#1B5E20',   # Dark green text
        'pending_bg': '#F3E5F5',     # Light purple for pending rows
        'pending_fg': '#4A148C'      # Dark purple text
    }
# Status options
    STATUS_OPTIONS = ['Pending', 'InProgress', 'Completed', 'Failed']
    def __init__(self, parent, go_back_callback):
super().__init__(parent, bg=self.COLORS['bg'])
        self.parent = parent
        self.go_back_callback = go_back_callback
        self.current_tracking_id = None
# Configure grid weights
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=1)  # Main content
        self.grid_columnconfigure(0, weight=1)
# Create UI sections
        self.create_header()
        self.create_main_content()
# Load data
        self.load_orders()
        self.load_process_stages()
        self.load_staff()
        self.load_tracking()
def create_header(self):
        """Creates the header bar with title and back button."""
        header_frame = tk.Frame(
            self,
            bg=self.COLORS['primary'],
            height=70
        )
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_propagate(False)
# Configure columns
        header_frame.grid_columnconfigure(0, weight=0)
        header_frame.grid_columnconfigure(1, weight=1)
        header_frame.grid_columnconfigure(2, weight=0)
# Back button
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
# Title
        title_label = tk.Label(
            header_frame,
            text="Order Tracking",
            font=('Helvetica', 20, 'bold'),
            bg=self.COLORS['primary'],
            fg=self.COLORS['text_light']
        )
        title_label.grid(row=0, column=1, padx=20, pady=15)
# Stats label (will be updated)
        self.stats_label = tk.Label(
            header_frame,
            text="Active Trackings: 0",
            font=('Helvetica', 11),
            bg=self.COLORS['primary'],
            fg=self.COLORS['text_light']
        )
        self.stats_label.grid(row=0, column=2, padx=20, pady=15, sticky='e')
        
    def create_main_content(self):
        """Creates the main content area with form and table."""
        main_container = tk.Frame(self, bg=self.COLORS['bg'])
        main_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=2)
# Left Panel - Form
        self.create_form_panel(main_container)
# Right Panel - Table
        self.create_table_panel(main_container)
def create_form_panel(self, parent):
        """Creates the form panel for adding/editing tracking records."""
        form_frame = tk.Frame(
            parent,
            bg=self.COLORS['card_bg'],
            relief='flat',
            highlightbackground=self.COLORS['border'],
            highlightthickness=1
        )
        form_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
# Form title
        title_frame = tk.Frame(form_frame, bg=self.COLORS['header_bg'])
        title_frame.pack(fill='x', pady=(0, 15))
        title_label = tk.Label(
            title_frame,
            text="📍 Tracking Information",
            font=('Helvetica', 14, 'bold'),
            bg=self.COLORS['header_bg'],
            fg=self.COLORS['primary']
        )
        title_label.pack(pady=12)
# Scrollable form fields
        canvas = tk.Canvas(form_frame, bg=self.COLORS['card_bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(form_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.COLORS['card_bg'])
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
# Form fields
        self.create_form_fields(scrollable_frame)
    def create_form_fields(self, parent):
        """Creates all form input fields."""
        fields_frame = tk.Frame(parent, bg=self.COLORS['card_bg'])
        fields_frame.pack(fill='both', padx=25, pady=20)
# Order Selection
        tk.Label(
            fields_frame,
            text="Order *:",
            font=('Helvetica', 11, 'bold'),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text']
        ).grid(row=0, column=0, sticky='w', pady=(0, 5))
self.order_combo = ttk.Combobox(
            fields_frame,
            font=('Helvetica', 11),
            state='readonly',
            width=35
        )
        self.order_combo.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(0, 15), ipady=5)
# Process Stage Selection
        tk.Label(
            fields_frame,
            text="Process Stage *:",
            font=('Helvetica', 11, 'bold'),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text']
        ).grid(row=2, column=0, sticky='w', pady=(0, 5))
        
        self.stage_combo = ttk.Combobox(
            fields_frame,
            font=('Helvetica', 11),
            state='readonly',
            width=35
        )
        self.stage_combo.grid(row=3, column=0, columnspan=2, sticky='ew', pady=(0, 15), ipady=5)
# Staff Assignment
        tk.Label(
            fields_frame,
            text="Assigned Staff:",
            font=('Helvetica', 11, 'bold'),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text']
        ).grid(row=4, column=0, sticky='w', pady=(0, 5))
self.staff_combo = ttk.Combobox(
            fields_frame,
            font=('Helvetica', 11),
            state='readonly',
            width=35
        )
        self.staff_combo.grid(row=5, column=0, columnspan=2, sticky='ew', pady=(0, 15), ipady=5)
# Start Time
        tk.Label(
            fields_frame,
            text="Start Time *:",
            font=('Helvetica', 11, 'bold'),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text']
        ).grid(row=6, column=0, sticky='w', pady=(0, 5))
        
        time_frame = tk.Frame(fields_frame, bg=self.COLORS['card_bg'])
        time_frame.grid(row=7, column=0, columnspan=2, sticky='ew', pady=(0, 15))
self.start_time_entry = tk.Entry(
            time_frame,
            font=('Helvetica', 11),
            bg='#FAFAFA',
            relief='solid',
            bd=1,
            width=25
        )
        self.start_time_entry.pack(side='left', ipady=5)
tk.Button(
            time_frame,
            text="📅 Now",
            font=('Helvetica', 9),
            bg=self.COLORS['info'],
            fg='white',
            relief='flat',
            cursor='hand2',
            padx=10,
            command=self.set_start_time_now
        ).pack(side='left', padx=(10, 0))
# End Time
        tk.Label(
            fields_frame,
            text="End Time:",
            font=('Helvetica', 11, 'bold'),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text']
        ).grid(row=8, column=0, sticky='w', pady=(0, 5))
        
        self.end_time_entry = tk.Entry(
            fields_frame,
            font=('Helvetica', 11),
            bg='#FAFAFA',
            relief='solid',
            bd=1,
            width=35
        )
        self.end_time_entry.grid(row=9, column=0, columnspan=2, sticky='ew', pady=(0, 15), ipady=5)
# Status
        tk.Label(
            fields_frame,
            text="Status:",
            font=('Helvetica', 11, 'bold'),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text']
        ).grid(row=10, column=0, sticky='w', pady=(0, 5))
        
        self.status_combo = ttk.Combobox(
            fields_frame,
            values=self.STATUS_OPTIONS,
            state='readonly',
            font=('Helvetica', 11),
            width=33
        )
        self.status_combo.grid(row=11, column=0, columnspan=2, sticky='ew', pady=(0, 15), ipady=5)
        self.status_combo.set('Pending')
# Notes
        tk.Label(
            fields_frame,
            text="Notes:",
            font=('Helvetica', 11, 'bold'),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text']
        ).grid(row=12, column=0, sticky='w', pady=(0, 5))
        
        self.notes_text = tk.Text(
            fields_frame,
            font=('Helvetica', 10),
            bg='#FAFAFA',
            relief='solid',
            bd=1,
            height=4,
            width=40
        )
        self.notes_text.grid(row=13, column=0, columnspan=2, sticky='ew', pady=(0, 15))
# Required fields hint
        hint_label = tk.Label(
            fields_frame,
            text="* Required fields",
            font=('Helvetica', 8, 'italic'),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text_secondary']
        )
        hint_label.grid(row=14, column=0, columnspan=2, sticky='w', pady=(5, 10))
# Buttons
        self.create_form_buttons(fields_frame)
# Configure grid weights
        fields_frame.grid_columnconfigure(0, weight=1)
        fields_frame.grid_columnconfigure(1, weight=0)
        
    def create_form_buttons(self, parent):
        """Creates the form action buttons."""
        button_frame = tk.Frame(parent, bg=self.COLORS['card_bg'])
        button_frame.grid(row=15, column=0, columnspan=2, sticky='ew', pady=(10, 0))
# Configure grid for buttons
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
# Add Button
        self.add_btn = tk.Button(
            button_frame,
            text="➕ Add Tracking",
            font=('Helvetica', 11, 'bold'),
            bg=self.COLORS['success'],
            fg='white',
            activebackground='#45A049',
            activeforeground='white',
            relief='flat',
            cursor='hand2',
            padx=15,
            pady=10,
            command=self.add_tracking
        )
        self.add_btn.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
# Mark Complete Button
        self.complete_btn = tk.Button(
            button_frame,
            text="✅ Mark Complete",
            font=('Helvetica', 11, 'bold'),
            bg=self.COLORS['primary'],
            fg='white',
            activebackground=self.COLORS['primary_dark'],
            activeforeground='white',
            relief='flat',
            cursor='hand2',
            padx=15,
            pady=10,
            state='disabled',
            command=self.mark_complete
        )
        self.complete_btn.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
# Delete & Clear buttons row
        self.delete_btn = tk.Button(
            button_frame,
            text="🗑️ Delete Tracking",
            font=('Helvetica', 10),
            bg=self.COLORS['danger'],
            fg='white',
            activebackground=self.COLORS['danger_dark'],
            activeforeground='white',
            relief='flat',
            cursor='hand2',
            padx=15,
            pady=8,
            state='disabled',
            command=self.delete_tracking
        )
        self.delete_btn.grid(row=1, column=0, padx=5, pady=(10, 0), sticky='ew')
        
        self.clear_btn = tk.Button(
            button_frame,
            text="🗑️ Clear Form",
            font=('Helvetica', 10),
            bg=self.COLORS['warning'],
            fg='white',
            activebackground='#FB8C00',
            activeforeground='white',
            relief='flat',
            cursor='hand2',
            padx=15,
            pady=8,
            command=self.clear_form
        )
        self.clear_btn.grid(row=1, column=1, padx=5, pady=(10, 0), sticky='ew')
# Hover effects
        def on_enter(btn, color):
            btn.config(bg=color)
        def on_leave(btn, original_color):
            btn.config(bg=original_color)
            
        self.add_btn.bind("<Enter>", lambda e: on_enter(self.add_btn, '#45A049'))
        self.add_btn.bind("<Leave>", lambda e: on_leave(self.add_btn, self.COLORS['success']))
        self.complete_btn.bind("<Enter>", lambda e: on_enter(self.complete_btn, self.COLORS['primary_dark']))
        self.complete_btn.bind("<Leave>", lambda e: on_leave(self.complete_btn, self.COLORS['primary']))
        self.delete_btn.bind("<Enter>", lambda e: on_enter(self.delete_btn, self.COLORS['danger_dark']))
        self.delete_btn.bind("<Leave>", lambda e: on_leave(self.delete_btn, self.COLORS['danger']))
        self.clear_btn.bind("<Enter>", lambda e: on_enter(self.clear_btn, '#FB8C00'))
        self.clear_btn.bind("<Leave>", lambda e: on_leave(self.clear_btn, self.COLORS['warning']))
    def create_table_panel(self, parent):
        """Creates the table panel for displaying tracking records."""
        table_frame = tk.Frame(
            parent,
            bg=self.COLORS['card_bg'],
            relief='flat',
            highlightbackground=self.COLORS['border'],
            highlightthickness=1
        )
        table_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
# Table title
        title_frame = tk.Frame(table_frame, bg=self.COLORS['header_bg'])
        title_frame.pack(fill='x', pady=(0, 10))
        
        title_label = tk.Label(
            title_frame,
            text="📊 Process Tracking Log",
            font=('Helvetica', 14, 'bold'),
            bg=self.COLORS['header_bg'],
            fg=self.COLORS['primary']
        )
        title_label.pack(pady=12)
        
        # Search and filter bar
        filter_frame = tk.Frame(table_frame, bg=self.COLORS['card_bg'])
        filter_frame.pack(fill='x', padx=15, pady=(0, 10))
        
        tk.Label(
            filter_frame,
            text="🔍 Search:",
            font=('Helvetica', 10),
            bg=self.COLORS['card_bg']
        ).pack(side='left', padx=(0, 10))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.search_tracking())
        
        search_entry = tk.Entry(
            filter_frame,
            textvariable=self.search_var,
            font=('Helvetica', 10),
            bg='#FAFAFA',
            relief='solid',
            bd=1
        )
        search_entry.pack(side='left', fill='x', expand=True, ipady=5)
        
        tk.Label(
            filter_frame,
            text="Filter by Status:",
            font=('Helvetica', 10),
            bg=self.COLORS['card_bg']
        ).pack(side='left', padx=(10, 10))
        
        self.status_filter = ttk.Combobox(
            filter_frame,
            values=['All', 'Pending', 'InProgress', 'Completed', 'Failed'],
            state='readonly',
            width=12
        )
        self.status_filter.set('All')
        self.status_filter.pack(side='left')
        self.status_filter.bind('<<ComboboxSelected>>', lambda e: self.filter_by_status())
        
        # Treeview frame
        tree_frame = tk.Frame(table_frame)
        tree_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # Create Treeview
        columns = ('ID', 'Order No', 'Stage', 'Staff', 'Start Time', 'End Time', 'Status')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=14)
        
        # Define headings
        self.tree.heading('ID', text='ID')
        self.tree.heading('Order No', text='Order No')
        self.tree.heading('Stage', text='Process Stage')
        self.tree.heading('Staff', text='Staff')
        self.tree.heading('Start Time', text='Start Time')
        self.tree.heading('End Time', text='End Time')
        self.tree.heading('Status', text='Status')
        
        # Define column widths
        self.tree.column('ID', width=50, anchor='center')
        self.tree.column('Order No', width=120, anchor='center')
        self.tree.column('Stage', width=120, anchor='center')
        self.tree.column('Staff', width=150)
        self.tree.column('Start Time', width=150, anchor='center')
        self.tree.column('End Time', width=150, anchor='center')
        self.tree.column('Status', width=100, anchor='center')
        
        # Configure tags for color coding
        self.tree.tag_configure('pending', background=self.COLORS['pending_bg'], foreground=self.COLORS['pending_fg'])
        self.tree.tag_configure('inprogress', background=self.COLORS['in_progress_bg'], foreground=self.COLORS['in_progress_fg'])
        self.tree.tag_configure('completed', background=self.COLORS['completed_bg'], foreground=self.COLORS['completed_fg'])
        self.tree.tag_configure('failed', background=self.COLORS['danger'], foreground='white')
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Bind selection event
        self.tree.bind('<<TreeviewSelect>>', self.on_row_select)
        
        # Legend for color coding
        legend_frame = tk.Frame(table_frame, bg=self.COLORS['card_bg'])
        legend_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        tk.Label(
            legend_frame,
            text="Legend:",
            font=('Helvetica', 9, 'bold'),
            bg=self.COLORS['card_bg']
        ).pack(side='left', padx=(0, 10))
        
        # Legend items
        legend_items = [
            ('Pending', self.COLORS['pending_bg']),
            ('In Progress', self.COLORS['in_progress_bg']),
            ('Completed', self.COLORS['completed_bg'])
        ]
        
        for text, color in legend_items:
            frame = tk.Frame(legend_frame, bg=self.COLORS['card_bg'])
            frame.pack(side='left', padx=10)
            
            box = tk.Frame(frame, bg=color, width=15, height=15)
            box.pack(side='left', padx=(0, 5))
            
            label = tk.Label(frame, text=text, font=('Helvetica', 9), bg=self.COLORS['card_bg'])
            label.pack(side='left')
            
    # ==============================================
    # DATA LOADING FUNCTIONS
    # ==============================================
    
    def load_orders(self):
        """Loads orders into the combobox."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT o.order_id, o.order_number, r.full_name, o.status
                FROM Orders o
                JOIN Resident r ON o.resident_id = r.resident_id
                WHERE o.status != 'Completed' AND o.status != 'Cancelled'
                ORDER BY o.order_id DESC
            """)
            orders = cursor.fetchall()
            
            self.order_list = []
            for o in orders:
                display_text = f"{o['order_number']} - {o['full_name']} ({o['status']})"
                self.order_list.append({
                    'id': o['order_id'],
                    'display': display_text
                })
            
            self.order_combo['values'] = [o['display'] for o in self.order_list]
            
        except Exception as e:
            print(f"[TrackingWindow] Error loading orders: {e}")
        finally:
            close_connection(conn)
            
    def load_process_stages(self):
        """Loads process stages into the combobox."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT stage_id, stage_name, stage_order
                FROM ProcessStage
                WHERE is_active = 1
                ORDER BY stage_order
            """)
            stages = cursor.fetchall()
            
            self.stage_list = []
            for s in stages:
                self.stage_list.append({
                    'id': s['stage_id'],
                    'name': s['stage_name'],
                    'display': s['stage_name']
                })
            
            self.stage_combo['values'] = [s['display'] for s in self.stage_list]
            
        except Exception as e:
            print(f"[TrackingWindow] Error loading stages: {e}")
        finally:
            close_connection(conn)
            
    def load_staff(self):
        """Loads staff into the combobox."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT staff_id, full_name, role
                FROM Staff
                WHERE is_available = 1
                ORDER BY full_name
            """)
            staff = cursor.fetchall()
            
            self.staff_list = []
            self.staff_list.append({'id': None, 'display': 'None'})
            for s in staff:
                display_text = f"{s['full_name']} ({s['role']})"
                self.staff_list.append({
                    'id': s['staff_id'],
                    'display': display_text
                })
            
            self.staff_combo['values'] = [s['display'] for s in self.staff_list]
            self.staff_combo.set('None')
            
        except Exception as e:
            print(f"[TrackingWindow] Error loading staff: {e}")
        finally:
            close_connection(conn)
            
    def load_tracking(self, search_term=None, status_filter=None):
        """
        Loads tracking records from database into treeview with color coding.
        
        Args:
            search_term (str): Optional search term to filter results
            status_filter (str): Optional status filter
        """
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            query = """
                SELECT t.tracking_id, t.order_id, o.order_number, t.stage_id, p.stage_name,
                       t.staff_id, s.full_name as staff_name, t.start_time, t.end_time,
                       t.status, t.notes
                FROM Tracking t
                JOIN Orders o ON t.order_id = o.order_id
                JOIN ProcessStage p ON t.stage_id = p.stage_id
                LEFT JOIN Staff s ON t.staff_id = s.staff_id
                WHERE 1=1
            """
            params = []
            
            if search_term:
                query += " AND (o.order_number LIKE ? OR p.stage_name LIKE ? OR s.full_name LIKE ?)"
                search_pattern = f"%{search_term}%"
                params.extend([search_pattern, search_pattern, search_pattern])
                
            if status_filter and status_filter != 'All':
                query += " AND t.status = ?"
                params.append(status_filter)
                
            query += " ORDER BY t.tracking_id DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Status emoji and tag mapping
            status_info = {
                'Pending': {'emoji': '⏳', 'tag': 'pending'},
                'InProgress': {'emoji': '⚙️', 'tag': 'inprogress'},
                'Completed': {'emoji': '✅', 'tag': 'completed'},
                'Failed': {'emoji': '❌', 'tag': 'failed'}
            }
            
            in_progress_count = 0
            for row in rows:
                info = status_info.get(row['status'], {'emoji': '❓', 'tag': 'pending'})
                display_status = f"{info['emoji']} {row['status']}"
                
                self.tree.insert('', 'end', values=(
                    row['tracking_id'],
                    row['order_number'],
                    row['stage_name'],
                    row['staff_name'] or 'Unassigned',
                    format_datetime(row['start_time']),
                    format_datetime(row['end_time']) if row['end_time'] else 'In Progress',
                    display_status
                ), tags=(info['tag'],))
                
                if row['status'] == 'InProgress':
                    in_progress_count += 1
            
            # Update stats
            self.stats_label.config(text=f"Active Trackings: {in_progress_count}")
            
        except Exception as e:
            print(f"[TrackingWindow] Error loading tracking: {e}")
            show_error(f"Failed to load tracking records: {str(e)}")
        finally:
            close_connection(conn)
            
    def search_tracking(self):
        """Filters tracking records based on search term."""
        search_term = self.search_var.get().strip()
        status_filter = self.status_filter.get()
        self.load_tracking(search_term if search_term else None, status_filter)
        
    def filter_by_status(self):
        """Filters tracking records by status."""
        search_term = self.search_var.get().strip()
        status_filter = self.status_filter.get()
        self.load_tracking(search_term if search_term else None, status_filter)
        
    def set_start_time_now(self):
        """Sets the start time entry to current datetime."""
        self.start_time_entry.delete(0, tk.END)
        self.start_time_entry.insert(0, get_current_datetime())
        
    def validate_form(self):
        """Validates the form inputs."""
        order_selection = self.order_combo.current()
        stage_selection = self.stage_combo.current()
        start_time = self.start_time_entry.get().strip()
        
        if order_selection < 0:
            show_error("Please select an order")
            return False
            
        if stage_selection < 0:
            show_error("Please select a process stage")
            return False
            
        if not start_time:
            show_error("Please enter start time")
            return False
            
        return True
        
    def add_tracking(self):
        """Adds a new tracking record to the database."""
        if not self.validate_form():
            return
            
        order_id = self.order_list[self.order_combo.current()]['id']
        stage_id = self.stage_list[self.stage_combo.current()]['id']
        
        # Get staff ID (if selected)
        staff_selection = self.staff_combo.current()
        staff_id = self.staff_list[staff_selection]['id'] if staff_selection > 0 else None
        
        start_time = self.start_time_entry.get().strip()
        end_time = self.end_time_entry.get().strip() or None
        status = self.status_combo.get()
        notes = self.notes_text.get("1.0", tk.END).strip() or None
        
        # If end_time is set but status not completed, auto-set status
        if end_time and status != 'Completed':
            status = 'Completed'
            
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Tracking (order_id, stage_id, staff_id, start_time, end_time, status, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (order_id, stage_id, staff_id, start_time, end_time, status, notes))
            conn.commit()
            
            show_success("Tracking record added successfully!")
            self.clear_form()
            self.load_tracking()
            
        except Exception as e:
            print(f"[TrackingWindow] Error adding tracking: {e}")
            show_error(f"Failed to add tracking record: {str(e)}")
            conn.rollback()
        finally:
            close_connection(conn)
            
    def mark_complete(self):
        """Marks the selected tracking record as completed."""
        if not self.current_tracking_id:
            show_error("Please select a tracking record to mark as complete")
            return
            
        if self.status_combo.get() == 'Completed':
            show_error("This tracking record is already completed")
            return
            
        if show_confirm("Mark this tracking record as completed?\nThis will set the end time to current time."):
            conn = get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE Tracking
                    SET end_time = ?, status = 'Completed'
                    WHERE tracking_id = ? AND status != 'Completed'
                """, (get_current_datetime(), self.current_tracking_id))
                conn.commit()
                
                show_success("Tracking record marked as completed!")
                self.clear_form()
                self.load_tracking()
                
            except Exception as e:
                print(f"[TrackingWindow] Error marking complete: {e}")
                show_error(f"Failed to mark as completed: {str(e)}")
            finally:
                close_connection(conn)
                
    def delete_tracking(self):
        """Deletes the selected tracking record after confirmation."""
        if not self.current_tracking_id:
            show_error("Please select a tracking record to delete")
            return
            
        if show_confirm("Are you sure you want to delete this tracking record?\nThis action cannot be undone."):
            conn = get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Tracking WHERE tracking_id = ?", (self.current_tracking_id,))
                conn.commit()
                
                show_success("Tracking record deleted successfully!")
                self.clear_form()
                self.load_tracking()
                
            except Exception as e:
                print(f"[TrackingWindow] Error deleting tracking: {e}")
                show_error(f"Failed to delete tracking record: {str(e)}")
            finally:
                close_connection(conn)
                
    def on_row_select(self, event):
        """Handles row selection in treeview."""
        selected = self.tree.selection()
        if not selected:
            return
            
        values = self.tree.item(selected[0], 'values')
        if values:
            self.current_tracking_id = safe_int(values[0])
            
            # Fetch full details from database
            conn = get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT t.*, p.stage_name, o.order_number
                    FROM Tracking t
                    JOIN ProcessStage p ON t.stage_id = p.stage_id
                    JOIN Orders o ON t.order_id = o.order_id
                    WHERE t.tracking_id = ?
                """, (self.current_tracking_id,))
                row = cursor.fetchone()
                
                if row:
                    # Set order
                    for i, order in enumerate(self.order_list):
                        if order['id'] == row['order_id']:
                            self.order_combo.current(i)
                            break
                            
                    # Set stage
                    for i, stage in enumerate(self.stage_list):
                        if stage['id'] == row['stage_id']:
                            self.stage_combo.current(i)
                            break
                            
                    # Set staff
                    staff_found = False
                    for i, staff in enumerate(self.staff_list):
                        if staff['id'] == row['staff_id']:
                            self.staff_combo.current(i)
                            staff_found = True
                            break
                    if not staff_found:
                        self.staff_combo.current(0)
                        
                    self.start_time_entry.delete(0, tk.END)
                    self.start_time_entry.insert(0, row['start_time'] if row['start_time'] else "")
                    
                    self.end_time_entry.delete(0, tk.END)
                    self.end_time_entry.insert(0, row['end_time'] if row['end_time'] else "")
                    
                    self.status_combo.set(row['status'])
                    
                    self.notes_text.delete("1.0", tk.END)
                    if row['notes']:
                        self.notes_text.insert("1.0", row['notes'])
                        
            except Exception as e:
                print(f"[TrackingWindow] Error fetching tracking details: {e}")
            finally:
                close_connection(conn)
            
            # Enable buttons
            self.complete_btn.config(state='normal')
            self.delete_btn.config(state='normal')
            self.add_btn.config(state='disabled')
            
    def clear_form(self):
        """Clears all form fields and resets button states."""
        self.order_combo.set('')
        self.stage_combo.set('')
        self.staff_combo.set('None')
        self.start_time_entry.delete(0, tk.END)
        self.end_time_entry.delete(0, tk.END)
        self.status_combo.set('Pending')
        self.notes_text.delete("1.0", tk.END)
        self.current_tracking_id = None
        
        self.complete_btn.config(state='disabled')
        self.delete_btn.config(state='disabled')
        self.add_btn.config(state='normal')
        
        # Clear treeview selection
        self.tree.selection_remove(self.tree.selection())



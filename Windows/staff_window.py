import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from database import get_connection, close_connection
from auth import is_admin, get_current_user
from helpers import (
    show_error, show_success, show_confirm, center_window,
    validate_email, validate_phone, safe_int, safe_float, format_date  # Fixed: Added safe_float
)
from schema import create_tables
from seed_data import seed_all


class StaffWindow(tk.Frame):
    
    
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
        'access_denied_bg': '#FFEBEE' # Light red for access denied
    }
    
    # Role options (matching DB CHECK constraint)
    ROLES = ['Washer', 'Dryer', 'Ironer', 'Packer', 'Delivery', 'Admin']
    
    # Shift validation pattern (HH:MM)
    TIME_PATTERN = r'^([0-1][0-9]|2[0-3]):[0-5][0-9]$'
    
    def __init__(self, parent, go_back_callback):
        """
        Initialize the Staff Window.
        
        Args:
            parent: The parent window (tk.Tk or tk.Frame)
            go_back_callback: Function to call when back button is clicked
        """
        super().__init__(parent, bg=self.COLORS['bg'])
        self.parent = parent
        self.go_back_callback = go_back_callback
        self.current_staff_id = None
        
        # Configure grid weights
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=1)  # Main content
        self.grid_columnconfigure(0, weight=1)
        
        # Create UI sections
        self.create_header()
        
        # Check admin access
        if is_admin():
            self.create_main_content()
            self.load_staff()
        else:
            self.create_access_denied()
        
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
        
        # Title with admin badge
        title_frame = tk.Frame(header_frame, bg=self.COLORS['primary'])
        title_frame.grid(row=0, column=1, padx=20, pady=15)
        
        title_label = tk.Label(
            title_frame,
            text="Staff Management",
            font=('Helvetica', 20, 'bold'),
            bg=self.COLORS['primary'],
            fg=self.COLORS['text_light']
        )
        title_label.pack(side='left')
        
        # Admin badge
        admin_badge = tk.Label(
            title_frame,
            text="🔒 Admin Only",
            font=('Helvetica', 9, 'bold'),
            bg=self.COLORS['warning'],
            fg='white',
            padx=8,
            pady=2
        )
        admin_badge.pack(side='left', padx=(10, 0))
        
        # Stats label (will be updated)
        self.stats_label = tk.Label(
            header_frame,
            text="Total Staff: 0",
            font=('Helvetica', 11),
            bg=self.COLORS['primary'],
            fg=self.COLORS['text_light']
        )
        self.stats_label.grid(row=0, column=2, padx=20, pady=15, sticky='e')
        
    def create_access_denied(self):
        """Creates the access denied screen for non-admin users."""
        main_frame = tk.Frame(self, bg=self.COLORS['access_denied_bg'])
        main_frame.grid(row=1, column=0, sticky="nsew")
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Access denied card
        card = tk.Frame(
            main_frame,
            bg=self.COLORS['card_bg'],
            relief='flat',
            highlightbackground=self.COLORS['danger'],
            highlightthickness=2
        )
        card.grid(row=0, column=0, padx=50, pady=50)
        
        # Lock icon
        lock_label = tk.Label(
            card,
            text="🔒",
            font=('Segoe UI Emoji', 64),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['danger']
        )
        lock_label.pack(pady=(30, 10))
        
        # Title
        title_label = tk.Label(
            card,
            text="Access Denied",
            font=('Helvetica', 24, 'bold'),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['danger']
        )
        title_label.pack(pady=(0, 10))
        
        # Message
        message_label = tk.Label(
            card,
            text="This section is restricted to administrators only.\n\nPlease contact your system administrator for access.",
            font=('Helvetica', 11),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text_secondary'],
            justify='center'
        )
        message_label.pack(pady=(0, 30))
        
        # Go back button
        back_btn = tk.Button(
            card,
            text="← Return to Dashboard",
            font=('Helvetica', 11, 'bold'),
            bg=self.COLORS['primary'],
            fg='white',
            activebackground=self.COLORS['primary_dark'],
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=10,
            command=self.go_back_callback
        )
        back_btn.pack(pady=(0, 30))
        
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
        """Creates the form panel for adding/editing staff."""
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
            text="👨‍💼 Staff Information",
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
        
        # Column configuration for 2-column layout
        fields_frame.grid_columnconfigure(0, weight=1)
        fields_frame.grid_columnconfigure(1, weight=1)
        
        # Field definitions
        self.form_vars = {}
        
        # Row 0: Full Name
        self.create_labeled_field(fields_frame, "Full Name *:", "full_name", 0, 0)
        
        # Row 1: Contact No & Email
        self.create_labeled_field(fields_frame, "Contact No *:", "phone", 1, 0)
        self.create_labeled_field(fields_frame, "Email *:", "email", 1, 1)
        
        # Row 2: Role
        tk.Label(
            fields_frame,
            text="Role *:",
            font=('Helvetica', 10, 'bold'),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text']
        ).grid(row=2, column=0, sticky='w', pady=(10, 5))
        
        self.role_combo = ttk.Combobox(
            fields_frame,
            values=self.ROLES,
            state='readonly',
            font=('Helvetica', 10),
            width=25
        )
        self.role_combo.grid(row=3, column=0, sticky='ew', pady=(0, 15), ipady=5)
        self.form_vars['role'] = self.role_combo
        
        # Row 3: Hire Date
        self.create_labeled_field(fields_frame, "Hire Date *:", "hire_date", 4, 0)
        
        # Row 4: Salary
        self.create_labeled_field(fields_frame, "Salary (₹) *:", "salary", 4, 1)
        
        # Row 5: Shift Start & Shift End
        self.create_labeled_field(fields_frame, "Shift Start (HH:MM):", "shift_start", 5, 0)
        self.create_labeled_field(fields_frame, "Shift End (HH:MM):", "shift_end", 5, 1)
        
        # Row 6: Availability
        tk.Label(
            fields_frame,
            text="Availability:",
            font=('Helvetica', 10, 'bold'),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text']
        ).grid(row=6, column=0, sticky='w', pady=(10, 5))
        
        self.available_var = tk.StringVar(value="available")
        available_radio = tk.Radiobutton(
            fields_frame,
            text="Available",
            variable=self.available_var,
            value="available",
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text'],
            selectcolor=self.COLORS['card_bg']
        )
        available_radio.grid(row=7, column=0, sticky='w')
        
        unavailable_radio = tk.Radiobutton(
            fields_frame,
            text="Unavailable",
            variable=self.available_var,
            value="unavailable",
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text'],
            selectcolor=self.COLORS['card_bg']
        )
        unavailable_radio.grid(row=7, column=1, sticky='w')
        
        # Required fields hint
        hint_label = tk.Label(
            fields_frame,
            text="* Required fields",
            font=('Helvetica', 8, 'italic'),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text_secondary']
        )
        hint_label.grid(row=8, column=0, columnspan=2, sticky='w', pady=(15, 5))
        
        # Buttons
        self.create_form_buttons(fields_frame)
        
    def create_labeled_field(self, parent, label_text, var_name, row, col):
        """Creates a labeled entry field."""
        tk.Label(
            parent,
            text=label_text,
            font=('Helvetica', 10, 'bold'),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text']
        ).grid(row=row, column=col, sticky='w', pady=(10, 5))
        
        var = tk.StringVar()
        entry = tk.Entry(
            parent,
            textvariable=var,
            font=('Helvetica', 10),
            bg='#FAFAFA',
            relief='solid',
            bd=1,
            highlightthickness=1,
            highlightcolor=self.COLORS['primary']
        )
        entry.grid(row=row + 1, column=col, sticky='ew', pady=(0, 15), ipady=5)
        
        self.form_vars[var_name] = var
        
    def create_form_buttons(self, parent):
        """Creates the form action buttons."""
        button_frame = tk.Frame(parent, bg=self.COLORS['card_bg'])
        button_frame.grid(row=9, column=0, columnspan=2, sticky='ew', pady=(10, 0))
        
        # Configure grid for buttons
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        
        # Add Button
        self.add_btn = tk.Button(
            button_frame,
            text="➕ Add Staff",
            font=('Helvetica', 11, 'bold'),
            bg=self.COLORS['success'],
            fg='white',
            activebackground='#45A049',
            activeforeground='white',
            relief='flat',
            cursor='hand2',
            padx=15,
            pady=10,
            command=self.add_staff
        )
        self.add_btn.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        
        # Update Button
        self.update_btn = tk.Button(
            button_frame,
            text="✏️ Update Staff",
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
            command=self.update_staff
        )
        self.update_btn.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        # Clear Button
        self.clear_btn = tk.Button(
            button_frame,
            text="🗑️ Clear Form",
            font=('Helvetica', 11),
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
        self.clear_btn.grid(row=1, column=0, columnspan=2, pady=(10, 0), sticky='ew')
        
        # Hover effects
        def on_enter(btn, color):
            btn.config(bg=color)
            
        def on_leave(btn, original_color):
            btn.config(bg=original_color)
            
        self.add_btn.bind("<Enter>", lambda e: on_enter(self.add_btn, '#45A049'))
        self.add_btn.bind("<Leave>", lambda e: on_leave(self.add_btn, self.COLORS['success']))
        self.update_btn.bind("<Enter>", lambda e: on_enter(self.update_btn, self.COLORS['primary_dark']))
        self.update_btn.bind("<Leave>", lambda e: on_leave(self.update_btn, self.COLORS['primary']))
        self.clear_btn.bind("<Enter>", lambda e: on_enter(self.clear_btn, '#FB8C00'))
        self.clear_btn.bind("<Leave>", lambda e: on_leave(self.clear_btn, self.COLORS['warning']))
        
    def create_table_panel(self, parent):
        """Creates the table panel for displaying staff."""
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
            text="📋 Staff Directory",
            font=('Helvetica', 14, 'bold'),
            bg=self.COLORS['header_bg'],
            fg=self.COLORS['primary']
        )
        title_label.pack(pady=12)
        
        # Search bar
        search_frame = tk.Frame(table_frame, bg=self.COLORS['card_bg'])
        search_frame.pack(fill='x', padx=15, pady=(0, 10))
        
        tk.Label(
            search_frame,
            text="🔍 Search:",
            font=('Helvetica', 10),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text']
        ).pack(side='left', padx=(0, 10))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.search_staff())
        
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=('Helvetica', 10),
            bg='#FAFAFA',
            relief='solid',
            bd=1
        )
        search_entry.pack(side='left', fill='x', expand=True, ipady=5)
        
        # Treeview frame
        tree_frame = tk.Frame(table_frame)
        tree_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # Create Treeview
        columns = ('ID', 'Name', 'Role', 'Contact', 'Email', 'Shift', 'Status')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=12)
        
        # Define headings
        self.tree.heading('ID', text='ID')
        self.tree.heading('Name', text='Staff Name')
        self.tree.heading('Role', text='Role')
        self.tree.heading('Contact', text='Contact')
        self.tree.heading('Email', text='Email')
        self.tree.heading('Shift', text='Shift')
        self.tree.heading('Status', text='Status')
        
        # Define column widths
        self.tree.column('ID', width=50, anchor='center')
        self.tree.column('Name', width=150)
        self.tree.column('Role', width=100, anchor='center')
        self.tree.column('Contact', width=100, anchor='center')
        self.tree.column('Email', width=160)
        self.tree.column('Shift', width=100, anchor='center')
        self.tree.column('Status', width=80, anchor='center')
        
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
        
        # Delete button at bottom
        delete_frame = tk.Frame(table_frame, bg=self.COLORS['card_bg'])
        delete_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        self.delete_btn = tk.Button(
            delete_frame,
            text="🗑️ Delete Selected Staff",
            font=('Helvetica', 10, 'bold'),
            bg=self.COLORS['danger'],
            fg='white',
            activebackground=self.COLORS['danger_dark'],
            activeforeground='white',
            relief='flat',
            cursor='hand2',
            padx=10,
            pady=8,
            state='disabled',
            command=self.delete_staff
        )
        self.delete_btn.pack(fill='x')
        
        # Hover effect
        self.delete_btn.bind("<Enter>", lambda e: self.delete_btn.config(bg=self.COLORS['danger_dark']))
        self.delete_btn.bind("<Leave>", lambda e: self.delete_btn.config(bg=self.COLORS['danger']))
        
    def load_staff(self, search_term=None):
        """
        Loads all staff from database into treeview.
        
        Args:
            search_term (str): Optional search term to filter results
        """
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            if search_term:
                query = """
                    SELECT staff_id, full_name, role, phone, email, 
                           shift_start, shift_end, is_available, hire_date, salary
                    FROM Staff
                    WHERE full_name LIKE ? OR email LIKE ? OR phone LIKE ? OR role LIKE ?
                    ORDER BY staff_id
                """
                search_pattern = f"%{search_term}%"
                cursor.execute(query, (search_pattern, search_pattern, search_pattern, search_pattern))
            else:
                cursor.execute("""
                    SELECT staff_id, full_name, role, phone, email, 
                           shift_start, shift_end, is_available, hire_date, salary
                    FROM Staff
                    ORDER BY staff_id
                """)
            
            rows = cursor.fetchall()
            
            # Status mapping
            status_display = {
                1: "✅ Active",
                0: "❌ Inactive"
            }
            
            for row in rows:
                # Format shift
                shift = "N/A"
                if row['shift_start'] and row['shift_end']:
                    shift = f"{row['shift_start']}-{row['shift_end']}"
                
                self.tree.insert('', 'end', values=(
                    row['staff_id'],
                    row['full_name'],
                    row['role'],
                    row['phone'],
                    row['email'],
                    shift,
                    status_display.get(row['is_available'], "Unknown")
                ))
            
            # Update stats
            self.stats_label.config(text=f"Total Staff: {len(rows)}")
            
        except Exception as e:
            print(f"[StaffWindow] Error loading staff: {e}")
            show_error(f"Failed to load staff: {str(e)}")
        finally:
            close_connection(conn)
            
    def search_staff(self):
        """Filters staff based on search term."""
        search_term = self.search_var.get().strip()
        self.load_staff(search_term if search_term else None)
        
    def validate_form(self):
        """Validates the form inputs."""
        full_name = self.form_vars['full_name'].get().strip()
        phone = self.form_vars['phone'].get().strip()
        email = self.form_vars['email'].get().strip()
        role = self.role_combo.get()
        hire_date = self.form_vars['hire_date'].get().strip()
        salary = self.form_vars['salary'].get().strip()
        shift_start = self.form_vars['shift_start'].get().strip()
        shift_end = self.form_vars['shift_end'].get().strip()
        
        if not full_name:
            show_error("Please enter the staff name")
            return False
            
        if not phone:
            show_error("Please enter the contact number")
            return False
            
        if not validate_phone(phone):
            show_error("Please enter a valid 10-digit phone number")
            return False
            
        if not email:
            show_error("Please enter the email address")
            return False
            
        if not validate_email(email):
            show_error("Please enter a valid email address")
            return False
            
        if not role:
            show_error("Please select a role")
            return False
            
        if not hire_date:
            show_error("Please enter the hire date (YYYY-MM-DD)")
            return False
            
        # Validate date format
        try:
            datetime.strptime(hire_date, "%Y-%m-%d")
        except ValueError:
            show_error("Please enter hire date in YYYY-MM-DD format")
            return False
            
        if not salary:
            show_error("Please enter the salary")
            return False
            
        try:
            salary_val = safe_float(salary)
            if salary_val < 0:
                show_error("Salary must be greater than or equal to 0")
                return False
        except ValueError:
            show_error("Please enter a valid salary amount")
            return False
            
        # Validate shift times if provided
        if shift_start:
            import re
            if not re.match(self.TIME_PATTERN, shift_start):
                show_error("Shift Start must be in HH:MM format (24-hour)")
                return False
                
        if shift_end:
            import re
            if not re.match(self.TIME_PATTERN, shift_end):
                show_error("Shift End must be in HH:MM format (24-hour)")
                return False
                
        return True
        
    def add_staff(self):
        """Adds a new staff member to the database."""
        if not self.validate_form():
            return
            
        full_name = self.form_vars['full_name'].get().strip()
        phone = self.form_vars['phone'].get().strip()
        email = self.form_vars['email'].get().strip()
        role = self.role_combo.get()
        hire_date = self.form_vars['hire_date'].get().strip()
        salary = safe_float(self.form_vars['salary'].get().strip())
        shift_start = self.form_vars['shift_start'].get().strip() or None
        shift_end = self.form_vars['shift_end'].get().strip() or None
        is_available = 1 if self.available_var.get() == "available" else 0
        
        # Check if email already exists
        if self.email_exists(email):
            show_error(f"A staff member with email '{email}' already exists")
            return
            
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Staff (full_name, phone, email, role, hire_date, 
                                   salary, shift_start, shift_end, is_available)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (full_name, phone, email, role, hire_date, 
                  salary, shift_start, shift_end, is_available))
            conn.commit()
            
            show_success(f"Staff member '{full_name}' added successfully!")
            self.clear_form()
            self.load_staff()
            
        except Exception as e:
            print(f"[StaffWindow] Error adding staff: {e}")
            show_error(f"Failed to add staff: {str(e)}")
        finally:
            close_connection(conn)
            
    def update_staff(self):
        """Updates the selected staff member."""
        if not self.current_staff_id:
            show_error("Please select a staff member to update")
            return
            
        if not self.validate_form():
            return
            
        full_name = self.form_vars['full_name'].get().strip()
        phone = self.form_vars['phone'].get().strip()
        email = self.form_vars['email'].get().strip()
        role = self.role_combo.get()
        hire_date = self.form_vars['hire_date'].get().strip()
        salary = safe_float(self.form_vars['salary'].get().strip())
        shift_start = self.form_vars['shift_start'].get().strip() or None
        shift_end = self.form_vars['shift_end'].get().strip() or None
        is_available = 1 if self.available_var.get() == "available" else 0
        
        # Check if email already exists (excluding current)
        if self.email_exists(email, self.current_staff_id):
            show_error(f"A staff member with email '{email}' already exists")
            return
            
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Staff
                SET full_name = ?, phone = ?, email = ?, role = ?, hire_date = ?,
                    salary = ?, shift_start = ?, shift_end = ?, is_available = ?
                WHERE staff_id = ?
            """, (full_name, phone, email, role, hire_date, 
                  salary, shift_start, shift_end, is_available, self.current_staff_id))
            conn.commit()
            
            show_success(f"Staff member '{full_name}' updated successfully!")
            self.clear_form()
            self.load_staff()
            
        except Exception as e:
            print(f"[StaffWindow] Error updating staff: {e}")
            show_error(f"Failed to update staff: {str(e)}")
        finally:
            close_connection(conn)
            
    def delete_staff(self):
        """Deletes the selected staff member after confirmation."""
        if not self.current_staff_id:
            show_error("Please select a staff member to delete")
            return
            
        # Get staff name for confirmation
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0], 'values')
            staff_name = values[1] if values else "this staff member"
            
            # Check if staff is assigned to any orders
            if self.is_staff_assigned(self.current_staff_id):
                show_error(f"Cannot delete '{staff_name}' because they are assigned to existing orders.\nPlease make them inactive instead.")
                return
                
            if show_confirm(f"Are you sure you want to delete '{staff_name}'?\nThis action cannot be undone."):
                conn = get_connection()
                try:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM Staff WHERE staff_id = ?", (self.current_staff_id,))
                    conn.commit()
                    
                    show_success(f"Staff member '{staff_name}' deleted successfully!")
                    self.clear_form()
                    self.load_staff()
                    
                except Exception as e:
                    print(f"[StaffWindow] Error deleting staff: {e}")
                    show_error(f"Failed to delete staff: {str(e)}")
                finally:
                    close_connection(conn)
                    
    def is_staff_assigned(self, staff_id):
        """Checks if a staff member is assigned to any orders."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM Orders WHERE staff_id = ?", (staff_id,))
            result = cursor.fetchone()
            return result['count'] > 0
        except Exception:
            return False
        finally:
            close_connection(conn)
            
    def email_exists(self, email, exclude_id=None):
        """Checks if an email already exists in the staff table."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            if exclude_id:
                cursor.execute(
                    "SELECT COUNT(*) as count FROM Staff WHERE email = ? AND staff_id != ?",
                    (email, exclude_id)
                )
            else:
                cursor.execute("SELECT COUNT(*) as count FROM Staff WHERE email = ?", (email,))
            result = cursor.fetchone()
            return result['count'] > 0
        except Exception:
            return False
        finally:
            close_connection(conn)
            
    def on_row_select(self, event):
        """Handles row selection in treeview."""
        selected = self.tree.selection()
        if not selected:
            return
            
        values = self.tree.item(selected[0], 'values')
        if values:
            self.current_staff_id = safe_int(values[0])
            
            # Populate form fields
            self.form_vars['full_name'].set(values[1])
            self.form_vars['phone'].set(values[3])
            self.form_vars['email'].set(values[4])
            self.role_combo.set(values[2])
            
            # Fetch additional data from database
            conn = get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT hire_date, salary, shift_start, shift_end, is_available
                    FROM Staff WHERE staff_id = ?
                """, (self.current_staff_id,))
                row = cursor.fetchone()
                
                if row:
                    self.form_vars['hire_date'].set(row['hire_date'] if row['hire_date'] else "")
                    self.form_vars['salary'].set(str(row['salary']) if row['salary'] else "")
                    self.form_vars['shift_start'].set(row['shift_start'] if row['shift_start'] else "")
                    self.form_vars['shift_end'].set(row['shift_end'] if row['shift_end'] else "")
                    self.available_var.set("available" if row['is_available'] == 1 else "unavailable")
                    
            except Exception as e:
                print(f"[StaffWindow] Error fetching staff details: {e}")
            finally:
                close_connection(conn)
            
            # Enable update and delete buttons
            self.update_btn.config(state='normal')
            self.delete_btn.config(state='normal')
            self.add_btn.config(state='disabled')
            
    def clear_form(self):
        """Clears all form fields and resets button states."""
        for key, var in self.form_vars.items():
            if hasattr(var, 'set'):
                var.set("")
        self.role_combo.set("")
        self.available_var.set("available")
        self.current_staff_id = None
        
        self.update_btn.config(state='disabled')
        self.delete_btn.config(state='disabled')
        self.add_btn.config(state='normal')
        
        # Clear treeview selection
        self.tree.selection_remove(self.tree.selection())
        
        # Focus on name field
        if 'full_name' in self.form_vars:
            self.form_vars['full_name'].focus()


# ==============================================
# TEST BLOCK (for standalone testing)
# ==============================================

if __name__ == "__main__":
    from database import get_connection, close_connection  # Already imported, but kept for clarity
    
    # Initialize database
    print("Initializing database...")
    create_tables()
    seed_all()
    
    # Create root window
    root = tk.Tk()
    root.title("TeddyShine Laundry Management System - Staff")
    root.geometry("1300x700")
    root.configure(bg='#E8F0E6')
    
    # Center window
    center_window(root, 1300, 700)
    
    # Test login as admin
    from auth import login_user
    login_user("admin@teddyshine.com", "admin123")
    
    # Dummy callback
    def go_back():
        print("Going back to dashboard...")
        root.quit()
    
    # Create and show staff window
    staff_window = StaffWindow(root, go_back)
    staff_window.pack(fill='both', expand=True)
    
    root.mainloop()
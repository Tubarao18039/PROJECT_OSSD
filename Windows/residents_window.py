import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from database import get_connection, close_connection
from auth import is_admin, get_current_user
from helpers import (
    show_error, show_success, show_confirm, center_window,
    validate_email, validate_phone, clear_frame, safe_int
)

class ResidentsWindow(tk.Frame):
    """
    Residents Window - Manage all resident profiles."""
    

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
        'header_bg': '#F5F9F4'      
    }
    
    def __init__(self, parent, go_back_callback):

        super().__init__(parent, bg=self.COLORS['bg'])
        self.parent = parent
        self.go_back_callback = go_back_callback
        self.current_resident_id = None
        
        # Configure grid weights
        self.grid_rowconfigure(0, weight=0)  
        self.grid_rowconfigure(1, weight=1) 
        self.grid_columnconfigure(0, weight=1)
        
        self.create_header()
        self.create_main_content()
        

        self.load_residents()
        
    def create_header(self):
        """Creates the header bar with title and back button."""
        header_frame = tk.Frame(
            self,
            bg=self.COLORS['primary'],
            height=70
        )
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_propagate(False)
        

        header_frame.grid_columnconfigure(0, weight=0)  # Back button
        header_frame.grid_columnconfigure(1, weight=1)  # Title
        header_frame.grid_columnconfigure(2, weight=0)  # Stats
        

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
            text="Resident Management",
            font=('Helvetica', 20, 'bold'),
            bg=self.COLORS['primary'],
            fg=self.COLORS['text_light']
        )
        title_label.grid(row=0, column=1, padx=20, pady=15)
        
        # Stats label 
        self.stats_label = tk.Label(
            header_frame,
            text="Total Residents: 0",
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
        
  
        self.create_form_panel(main_container)
        
        self.create_table_panel(main_container)
        
    def create_form_panel(self, parent):
        """Creates the form panel for adding/editing residents."""
        form_frame = tk.Frame(
            parent,
            bg=self.COLORS['card_bg'],
            relief='flat',
            highlightbackground=self.COLORS['border'],
            highlightthickness=1
        )
        form_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        title_frame = tk.Frame(form_frame, bg=self.COLORS['header_bg'])
        title_frame.pack(fill='x', pady=(0, 15))
        
        title_label = tk.Label(
            title_frame,
            text="📝 Resident Information",
            font=('Helvetica', 14, 'bold'),
            bg=self.COLORS['header_bg'],
            fg=self.COLORS['primary']
        )
        title_label.pack(pady=12)
        
        # Form fields container (scrollable)
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
        

        self.create_form_fields(scrollable_frame)
        
    def create_form_fields(self, parent):
        """Creates all form input fields."""
        fields_frame = tk.Frame(parent, bg=self.COLORS['card_bg'])
        fields_frame.pack(fill='both', padx=20, pady=15)
        
        # Column configuration for 2-column layout
        fields_frame.grid_columnconfigure(0, weight=1)
        fields_frame.grid_columnconfigure(1, weight=1)
        
        # Field definitions: (label, variable, row, column, width)
        self.form_vars = {}
        fields = [

            ("First Name", "first_name", 0, 0, 20, True),
            ("Last Name", "last_name", 0, 1, 20, True),
            

            ("Phone Number", "phone", 1, 0, 20, True),
            ("Email", "email", 1, 1, 20, True),
            

            ("Block", "block_name", 2, 0, 10, True),
            ("Room Number", "room_number", 2, 1, 10, True),
        ]
        
        for field in fields:
            label_text, var_name, row, col, width, required = field
            
            required_mark = "*" if required else ""
            label = tk.Label(
                fields_frame,
                text=f"{label_text}{required_mark}:",
                font=('Helvetica', 10, 'bold'),
                bg=self.COLORS['card_bg'],
                fg=self.COLORS['text']
            )
            label.grid(row=row, column=col, sticky='w', padx=(0, 10), pady=(10, 5))
            

            var = tk.StringVar()
            entry = tk.Entry(
                fields_frame,
                textvariable=var,
                font=('Helvetica', 10),
                bg='#FAFAFA',
                relief='solid',
                bd=1,
                highlightthickness=1,
                highlightcolor=self.COLORS['primary']
            )
            entry.grid(row=row + 1, column=col, sticky='ew', padx=(0, 10), pady=(0, 5), ipady=6)
            entry.config(width=width)
            
            self.form_vars[var_name] = var
            
            
        address_label = tk.Label(
            fields_frame,
            text="Address Details:",
            font=('Helvetica', 11, 'bold'),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['primary']
        )
        address_label.grid(row=3, column=0, columnspan=2, sticky='w', pady=(15, 5))
        

        status_frame = tk.Frame(fields_frame, bg=self.COLORS['card_bg'])
        status_frame.grid(row=4, column=0, columnspan=2, sticky='ew', pady=(10, 20))
        
        self.status_var = tk.StringVar(value="active")
        active_radio = tk.Radiobutton(
            status_frame,
            text="Active",
            variable=self.status_var,
            value="active",
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text'],
            selectcolor=self.COLORS['card_bg']
        )
        active_radio.pack(side='left', padx=(0, 15))
        
        inactive_radio = tk.Radiobutton(
            status_frame,
            text="Inactive",
            variable=self.status_var,
            value="inactive",
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text'],
            selectcolor=self.COLORS['card_bg']
        )
        inactive_radio.pack(side='left')
        
        
        hint_label = tk.Label(
            fields_frame,
            text="* Required fields",
            font=('Helvetica', 8, 'italic'),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text_secondary']
        )
        hint_label.grid(row=5, column=0, columnspan=2, sticky='w', pady=(5, 10))
        

        self.create_form_buttons(fields_frame)
        
    def create_form_buttons(self, parent):
        """Creates the form action buttons."""
        button_frame = tk.Frame(parent, bg=self.COLORS['card_bg'])
        button_frame.grid(row=6, column=0, columnspan=2, sticky='ew', pady=(10, 0))
        

        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)
        

        self.add_btn = tk.Button(
            button_frame,
            text="➕ Add Resident",
            font=('Helvetica', 10, 'bold'),
            bg=self.COLORS['success'],
            fg='white',
            activebackground='#45A049',
            activeforeground='white',
            relief='flat',
            cursor='hand2',
            padx=10,
            pady=8,
            command=self.add_resident
        )
        self.add_btn.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        

        self.update_btn = tk.Button(
            button_frame,
            text="✏️ Update Resident",
            font=('Helvetica', 10, 'bold'),
            bg=self.COLORS['primary'],
            fg='white',
            activebackground=self.COLORS['primary_dark'],
            activeforeground='white',
            relief='flat',
            cursor='hand2',
            padx=10,
            pady=8,
            state='disabled',
            command=self.update_resident
        )
        self.update_btn.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        

        self.clear_btn = tk.Button(
            button_frame,
            text="🗑️ Clear Form",
            font=('Helvetica', 10, 'bold'),
            bg=self.COLORS['warning'],
            fg='white',
            activebackground='#FB8C00',
            activeforeground='white',
            relief='flat',
            cursor='hand2',
            padx=10,
            pady=8,
            command=self.clear_form
        )
        self.clear_btn.grid(row=0, column=2, padx=5, pady=5, sticky='ew')
        
        # Hover effects
        for btn, color in [(self.add_btn, '#45A049'), (self.update_btn, self.COLORS['primary_dark'])]:
            def on_enter(e, b=btn, c=color):
                b.config(bg=c)
                
            def on_leave(e, b=btn, orig=btn.cget('bg')):
                b.config(bg=orig)
                
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
            
    def create_table_panel(self, parent):
        """Creates the table panel for displaying residents."""
        table_frame = tk.Frame(
            parent,
            bg=self.COLORS['card_bg'],
            relief='flat',
            highlightbackground=self.COLORS['border'],
            highlightthickness=1
        )
        table_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        

        title_frame = tk.Frame(table_frame, bg=self.COLORS['header_bg'])
        title_frame.pack(fill='x', pady=(0, 10))
        
        title_label = tk.Label(
            title_frame,
            text="📋 Registered Residents",
            font=('Helvetica', 14, 'bold'),
            bg=self.COLORS['header_bg'],
            fg=self.COLORS['primary']
        )
        title_label.pack(pady=12)
        

        search_frame = tk.Frame(table_frame, bg=self.COLORS['card_bg'])
        search_frame.pack(fill='x', padx=15, pady=(0, 10))
        
        tk.Label(
            search_frame,
            text="Search:",
            font=('Helvetica', 10),
            bg=self.COLORS['card_bg']
        ).pack(side='left', padx=(0, 10))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.search_residents())
        
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=('Helvetica', 10),
            relief='solid',
            bd=1
        )
        search_entry.pack(side='left', fill='x', expand=True, ipady=5)
        
        # Treeview frame with scrollbar
        tree_frame = tk.Frame(table_frame)
        tree_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # Create Treeview
        columns = ('ID', 'Name', 'Phone', 'Email', 'Block', 'Room', 'Status')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        

        self.tree.heading('ID', text='ID')
        self.tree.heading('Name', text='Full Name')
        self.tree.heading('Phone', text='Phone')
        self.tree.heading('Email', text='Email')
        self.tree.heading('Block', text='Block')
        self.tree.heading('Room', text='Room No')
        self.tree.heading('Status', text='Status')
        
     
        self.tree.column('ID', width=50, anchor='center')
        self.tree.column('Name', width=150)
        self.tree.column('Phone', width=100, anchor='center')
        self.tree.column('Email', width=180)
        self.tree.column('Block', width=60, anchor='center')
        self.tree.column('Room', width=70, anchor='center')
        self.tree.column('Status', width=80, anchor='center')
        
        v_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        


        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        self.tree.bind('<<TreeviewSelect>>', self.on_row_select)
        
        delete_frame = tk.Frame(table_frame, bg=self.COLORS['card_bg'])
        delete_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        self.delete_btn = tk.Button(
            delete_frame,
            text="🗑️ Delete Selected Resident",
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
            command=self.delete_resident
        )
        self.delete_btn.pack(fill='x')
        
    def load_residents(self, search_term=None):
        """
        Loads all residents from database into treeview."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            if search_term:
                query = """
                    SELECT resident_id, full_name, phone, email, block_name, room_number, is_active
                    FROM Resident
                    WHERE full_name LIKE ? OR email LIKE ? OR phone LIKE ?
                    ORDER BY resident_id
                """
                search_pattern = f"%{search_term}%"
                cursor.execute(query, (search_pattern, search_pattern, search_pattern))
            else:
                cursor.execute("""
                    SELECT resident_id, full_name, phone, email, block_name, room_number, is_active
                    FROM Resident
                    ORDER BY resident_id
                """)
            
            rows = cursor.fetchall()
            
            for row in rows:
                status_text = "Active" if row['is_active'] == 1 else "Inactive"
                status_color = "✅" if row['is_active'] == 1 else "❌"
                
                self.tree.insert('', 'end', values=(
                    row['resident_id'],
                    row['full_name'],
                    row['phone'],
                    row['email'],
                    row['block_name'],
                    row['room_number'],
                    f"{status_color} {status_text}"
                ))
            
            # Update stats
            self.stats_label.config(text=f"Total Residents: {len(rows)}")
            
        except Exception as e:
            print(f"[ResidentsWindow] Error loading residents: {e}")
            show_error(f"Failed to load residents: {str(e)}")
        finally:
            close_connection(conn)
            
    def search_residents(self):
        """Filters residents based on search term."""
        search_term = self.search_var.get().strip()
        self.load_residents(search_term if search_term else None)
        
    def add_resident(self):
        """Adds a new resident to the database."""
        # Validate required fields
        first_name = self.form_vars['first_name'].get().strip()
        last_name = self.form_vars['last_name'].get().strip()
        phone = self.form_vars['phone'].get().strip()
        email = self.form_vars['email'].get().strip()
        block = self.form_vars['block_name'].get().strip().upper()
        room = self.form_vars['room_number'].get().strip()
        
        if not all([first_name, last_name, phone, email, block, room]):
            show_error("Please fill in all required fields (*)")
            return
            
        if not validate_phone(phone):
            show_error("Please enter a valid 10-digit phone number")
            return
            
        if not validate_email(email):
            show_error("Please enter a valid email address")
            return
            
        if self.email_exists(email):
            show_error("A resident with this email already exists")
            return
            
        full_name = f"{first_name} {last_name}"
        is_active = 1 if self.status_var.get() == "active" else 0
        
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Resident (full_name, email, phone, block_name, room_number, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (full_name, email, phone, block, room, is_active))
            conn.commit()
            
            show_success(f"Resident {full_name} added successfully!")
            self.clear_form()
            self.load_residents()
            
        except Exception as e:
            print(f"[ResidentsWindow] Error adding resident: {e}")
            show_error(f"Failed to add resident: {str(e)}")
        finally:
            close_connection(conn)
            
    def update_resident(self):
        """Updates the selected resident."""
        if not self.current_resident_id:
            show_error("Please select a resident to update")
            return
            
        # Validate required fields
        first_name = self.form_vars['first_name'].get().strip()
        last_name = self.form_vars['last_name'].get().strip()
        phone = self.form_vars['phone'].get().strip()
        email = self.form_vars['email'].get().strip()
        block = self.form_vars['block_name'].get().strip().upper()
        room = self.form_vars['room_number'].get().strip()
        
        if not all([first_name, last_name, phone, email, block, room]):
            show_error("Please fill in all required fields (*)")
            return
            
        if not validate_phone(phone):
            show_error("Please enter a valid 10-digit phone number")
            return
            
        if not validate_email(email):
            show_error("Please enter a valid email address")
            return
            
        full_name = f"{first_name} {last_name}"
        is_active = 1 if self.status_var.get() == "active" else 0
        
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Resident
                SET full_name = ?, email = ?, phone = ?, block_name = ?, room_number = ?, is_active = ?
                WHERE resident_id = ?
            """, (full_name, email, phone, block, room, is_active, self.current_resident_id))
            conn.commit()
            
            show_success(f"Resident {full_name} updated successfully!")
            self.clear_form()
            self.load_residents()
            
        except Exception as e:
            print(f"[ResidentsWindow] Error updating resident: {e}")
            show_error(f"Failed to update resident: {str(e)}")
        finally:
            close_connection(conn)
            
    def delete_resident(self):
        """Deletes the selected resident after confirmation."""
        if not self.current_resident_id:
            show_error("Please select a resident to delete")
            return
            
        # Get resident name for confirmation
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0], 'values')
            resident_name = values[1] if values else "this resident"
            
            if show_confirm(f"Are you sure you want to delete {resident_name}?\nThis action cannot be undone."):
                conn = get_connection()
                try:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM Resident WHERE resident_id = ?", (self.current_resident_id,))
                    conn.commit()
                    
                    show_success(f"Resident deleted successfully!")
                    self.clear_form()
                    self.load_residents()
                    
                except Exception as e:
                    print(f"[ResidentsWindow] Error deleting resident: {e}")
                    show_error(f"Failed to delete resident: {str(e)}")
                finally:
                    close_connection(conn)
                    
    def on_row_select(self, event):
        """Handles row selection in treeview."""
        selected = self.tree.selection()
        if not selected:
            return
            
        values = self.tree.item(selected[0], 'values')
        if values:
            self.current_resident_id = safe_int(values[0])
            
            full_name = values[1].split(' ', 1)
            first_name = full_name[0]
            last_name = full_name[1] if len(full_name) > 1 else ""
            
            # Populate form fields
            self.form_vars['first_name'].set(first_name)
            self.form_vars['last_name'].set(last_name)
            self.form_vars['phone'].set(values[2])
            self.form_vars['email'].set(values[3])
            self.form_vars['block_name'].set(values[4])
            self.form_vars['room_number'].set(values[5])
            
            # Set status
            status_text = values[6]
            is_active = "active" if "Active" in status_text else "inactive"
            self.status_var.set(is_active)
            
            # Enable update and delete buttons
            self.update_btn.config(state='normal')
            self.delete_btn.config(state='normal')
            self.add_btn.config(state='disabled')
            
    def clear_form(self):
        """Clears all form fields and resets button states."""
        for var in self.form_vars.values():
            var.set("")
        self.status_var.set("active")
        self.current_resident_id = None
        
        self.update_btn.config(state='disabled')
        self.delete_btn.config(state='disabled')
        self.add_btn.config(state='normal')
        
        # Clear treeview selection
        self.tree.selection_remove(self.tree.selection())
        
    def email_exists(self, email, exclude_id=None):
        """Checks if an email already exists in the database."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            if exclude_id:
                cursor.execute(
                    "SELECT COUNT(*) as count FROM Resident WHERE email = ? AND resident_id != ?",
                    (email, exclude_id)
                )
            else:
                cursor.execute("SELECT COUNT(*) as count FROM Resident WHERE email = ?", (email,))
            result = cursor.fetchone()
            return result['count'] > 0
        except Exception:
            return False
        finally:
            close_connection(conn)

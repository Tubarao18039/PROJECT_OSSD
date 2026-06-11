import tkinter as tk
from tkinter import ttk, messagebox

from database import get_connection, close_connection
from helpers import (
    show_error, show_success, show_confirm, center_window,
    format_currency, safe_float, safe_int
)

class ServicesWindow(tk.Frame):
    
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
    

    STATUS_OPTIONS = ['Active', 'Inactive']
    
    def __init__(self, parent, go_back_callback):

        super().__init__(parent, bg=self.COLORS['bg'])
        self.parent = parent
        self.go_back_callback = go_back_callback
        self.current_service_id = None
        

        self.grid_rowconfigure(0, weight=0) 
        self.grid_rowconfigure(1, weight=1)  
        self.grid_columnconfigure(0, weight=1)
        
        self.create_header()
        self.create_main_content()
        

        self.load_services()
        
    def create_header(self):
        """Creates the header bar with title and back button."""
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
            text="Service Management",
            font=('Helvetica', 20, 'bold'),
            bg=self.COLORS['primary'],
            fg=self.COLORS['text_light']
        )
        title_label.grid(row=0, column=1, padx=20, pady=15)
        
        # Stats label (will be updated)
        self.stats_label = tk.Label(
            header_frame,
            text="Total Services: 0",
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
        """Creates the form panel for adding/editing services."""
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
            text="🧺 Service Information",
            font=('Helvetica', 14, 'bold'),
            bg=self.COLORS['header_bg'],
            fg=self.COLORS['primary']
        )
        title_label.pack(pady=12)
        
        # Form fields container
        fields_frame = tk.Frame(form_frame, bg=self.COLORS['card_bg'])
        fields_frame.pack(fill='both', padx=25, pady=20)
        
        # Service Name
        tk.Label(
            fields_frame,
            text="Service Name *:",
            font=('Helvetica', 11, 'bold'),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text']
        ).grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        self.name_entry = tk.Entry(
            fields_frame,
            font=('Helvetica', 11),
            bg='#FAFAFA',
            relief='solid',
            bd=1,
            highlightthickness=1,
            highlightcolor=self.COLORS['primary']
        )
        self.name_entry.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(0, 15), ipady=8)
        
        # Service Price
        tk.Label(
            fields_frame,
            text="Service Price (₹) *:",
            font=('Helvetica', 11, 'bold'),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text']
        ).grid(row=2, column=0, sticky='w', pady=(0, 5))
        
        self.price_entry = tk.Entry(
            fields_frame,
            font=('Helvetica', 11),
            bg='#FAFAFA',
            relief='solid',
            bd=1
        )
        self.price_entry.grid(row=3, column=0, sticky='ew', pady=(0, 15), ipady=8)
        
        # Currency symbol hint
        tk.Label(
            fields_frame,
            text="(e.g., 50.00)",
            font=('Helvetica', 9, 'italic'),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text_secondary']
        ).grid(row=3, column=1, sticky='w', padx=(10, 0), pady=(0, 15))
        
        # Estimate Time
        tk.Label(
            fields_frame,
            text="Estimate Time (minutes) *:",
            font=('Helvetica', 11, 'bold'),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text']
        ).grid(row=4, column=0, sticky='w', pady=(0, 5))
        
        time_frame = tk.Frame(fields_frame, bg=self.COLORS['card_bg'])
        time_frame.grid(row=5, column=0, sticky='ew', pady=(0, 15))
        
        self.time_entry = tk.Entry(
            time_frame,
            font=('Helvetica', 11),
            bg='#FAFAFA',
            relief='solid',
            bd=1,
            width=15
        )
        self.time_entry.pack(side='left', ipady=8)
        
        tk.Label(
            time_frame,
            text="minutes",
            font=('Helvetica', 11),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text_secondary']
        ).pack(side='left', padx=(10, 0))
        
        # Status
        tk.Label(
            fields_frame,
            text="Status *:",
            font=('Helvetica', 11, 'bold'),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text']
        ).grid(row=6, column=0, sticky='w', pady=(0, 5))
        
        self.status_combo = ttk.Combobox(
            fields_frame,
            values=self.STATUS_OPTIONS,
            state='readonly',
            font=('Helvetica', 11),
            width=20
        )
        self.status_combo.grid(row=7, column=0, sticky='w', pady=(0, 15))
        self.status_combo.set('Active')
        
        # Required fields hint
        hint_label = tk.Label(
            fields_frame,
            text="* Required fields",
            font=('Helvetica', 8, 'italic'),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text_secondary']
        )
        hint_label.grid(row=8, column=0, columnspan=2, sticky='w', pady=(10, 5))

        self.create_form_buttons(fields_frame)
        
        # Configure grid weights
        fields_frame.grid_columnconfigure(0, weight=1)
        fields_frame.grid_columnconfigure(1, weight=0)
        
    def create_form_buttons(self, parent):
        """Creates the form action buttons."""
        button_frame = tk.Frame(parent, bg=self.COLORS['card_bg'])
        button_frame.grid(row=9, column=0, columnspan=2, sticky='ew', pady=(15, 0))
        
        # Configure grid for buttons 
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        
        # Add Button
        self.add_btn = tk.Button(
            button_frame,
            text="➕ Add Service",
            font=('Helvetica', 11, 'bold'),
            bg=self.COLORS['success'],
            fg='white',
            activebackground='#45A049',
            activeforeground='white',
            relief='flat',
            cursor='hand2',
            padx=15,
            pady=10,
            command=self.add_service
        )
        self.add_btn.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        

        self.update_btn = tk.Button(
            button_frame,
            text="✏️ Update Service",
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
            command=self.update_service
        )
        self.update_btn.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        # Clear Button (below)
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
        
        # Hover effects for buttons
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
        """Creates the table panel for displaying services."""
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
            text="📋 Available Services",
            font=('Helvetica', 14, 'bold'),
            bg=self.COLORS['header_bg'],
            fg=self.COLORS['primary']
        )
        title_label.pack(pady=12)
        

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
        self.search_var.trace('w', lambda *args: self.search_services())
        
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=('Helvetica', 10),
            bg='#FAFAFA',
            relief='solid',
            bd=1
        )
        search_entry.pack(side='left', fill='x', expand=True, ipady=5)
        
        # Treeview frame with scrollbar
        tree_frame = tk.Frame(table_frame)
        tree_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # Create Treeview
        columns = ('ID', 'Service Name', 'Price', 'Est. Time', 'Status')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=12)
        
        # Define headings
        self.tree.heading('ID', text='ID')
        self.tree.heading('Service Name', text='Service Name')
        self.tree.heading('Price', text='Price')
        self.tree.heading('Est. Time', text='Est. Time')
        self.tree.heading('Status', text='Status')
        
        # Define column widths
        self.tree.column('ID', width=50, anchor='center')
        self.tree.column('Service Name', width=200)
        self.tree.column('Price', width=100, anchor='center')
        self.tree.column('Est. Time', width=100, anchor='center')
        self.tree.column('Status', width=100, anchor='center')
        
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
        

        self.tree.bind('<<TreeviewSelect>>', self.on_row_select)
        

        delete_frame = tk.Frame(table_frame, bg=self.COLORS['card_bg'])
        delete_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        self.delete_btn = tk.Button(
            delete_frame,
            text="🗑️ Delete Selected Service",
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
            command=self.delete_service
        )
        self.delete_btn.pack(fill='x')
        
        # Hover effect for delete button
        self.delete_btn.bind("<Enter>", lambda e: self.delete_btn.config(bg=self.COLORS['danger_dark']))
        self.delete_btn.bind("<Leave>", lambda e: self.delete_btn.config(bg=self.COLORS['danger']))
        
    def load_services(self, search_term=None):
        """
        Loads all services from database into treeview.
        
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
                    SELECT service_id, service_name, base_price, estimated_minutes, is_active
                    FROM Services
                    WHERE service_name LIKE ? OR description LIKE ?
                    ORDER BY service_id
                """
                search_pattern = f"%{search_term}%"
                cursor.execute(query, (search_pattern, search_pattern))
            else:
                cursor.execute("""
                    SELECT service_id, service_name, base_price, estimated_minutes, is_active
                    FROM Services
                    ORDER BY service_id
                """)
            
            rows = cursor.fetchall()
            
            # Status mapping
            status_display = {
                1: "✅ Active",
                0: "❌ Inactive"
            }
            
            for row in rows:
                time_display = f"{row['estimated_minutes']} min" if row['estimated_minutes'] else "N/A"
                
                self.tree.insert('', 'end', values=(
                    row['service_id'],
                    row['service_name'],
                    format_currency(row['base_price']),
                    time_display,
                    status_display.get(row['is_active'], "Unknown")
                ))
            
            # Update stats
            self.stats_label.config(text=f"Total Services: {len(rows)}")
            
        except Exception as e:
            print(f"[ServicesWindow] Error loading services: {e}")
            show_error(f"Failed to load services: {str(e)}")
        finally:
            close_connection(conn)
            
    def search_services(self):
        """Filters services based on search term."""
        search_term = self.search_var.get().strip()
        self.load_services(search_term if search_term else None)
        
    def validate_form(self):
        """Validates the form inputs."""
        name = self.name_entry.get().strip()
        price_str = self.price_entry.get().strip()
        time_str = self.time_entry.get().strip()
        
        if not name:
            show_error("Please enter the service name")
            return False
            
        if not price_str:
            show_error("Please enter the service price")
            return False
            
        try:
            price = safe_float(price_str)
            if price <= 0:
                show_error("Price must be greater than 0")
                return False
        except ValueError:
            show_error("Please enter a valid price (e.g., 50.00)")
            return False
            
        if not time_str:
            show_error("Please enter the estimated time")
            return False
            
        try:
            time_minutes = safe_int(time_str)
            if time_minutes <= 0:
                show_error("Estimated time must be greater than 0 minutes")
                return False
        except ValueError:
            show_error("Please enter a valid time in minutes (e.g., 30)")
            return False
            
        return True
        
    def add_service(self):
        """Adds a new service to the database."""
        if not self.validate_form():
            return
            
        name = self.name_entry.get().strip()
        price = safe_float(self.price_entry.get().strip())
        time_minutes = safe_int(self.time_entry.get().strip())
        status = 1 if self.status_combo.get() == "Active" else 0
        
        # Check if service already exists
        if self.service_exists(name):
            show_error(f"A service named '{name}' already exists")
            return
            
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Services (service_name, base_price, estimated_minutes, is_active, description)
                VALUES (?, ?, ?, ?, ?)
            """, (name, price, time_minutes, status, f"{name} service"))
            conn.commit()
            
            show_success(f"Service '{name}' added successfully!")
            self.clear_form()
            self.load_services()
            
        except Exception as e:
            print(f"[ServicesWindow] Error adding service: {e}")
            show_error(f"Failed to add service: {str(e)}")
        finally:
            close_connection(conn)
            
    def update_service(self):
        """Updates the selected service."""
        if not self.current_service_id:
            show_error("Please select a service to update")
            return
            
        if not self.validate_form():
            return
            
        name = self.name_entry.get().strip()
        price = safe_float(self.price_entry.get().strip())
        time_minutes = safe_int(self.time_entry.get().strip())
        status = 1 if self.status_combo.get() == "Active" else 0
        
        if self.service_exists(name, self.current_service_id):
            show_error(f"A service named '{name}' already exists")
            return
            
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Services
                SET service_name = ?, base_price = ?, estimated_minutes = ?, is_active = ?
                WHERE service_id = ?
            """, (name, price, time_minutes, status, self.current_service_id))
            conn.commit()
            
            show_success(f"Service '{name}' updated successfully!")
            self.clear_form()
            self.load_services()
            
        except Exception as e:
            print(f"[ServicesWindow] Error updating service: {e}")
            show_error(f"Failed to update service: {str(e)}")
        finally:
            close_connection(conn)
            
    def delete_service(self):
        """Deletes the selected service after confirmation."""
        if not self.current_service_id:
            show_error("Please select a service to delete")
            return
            
        # Get service name for confirmation
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0], 'values')
            service_name = values[1] if values else "this service"
            
            # Check if service is used in any orders
            if self.is_service_in_use(self.current_service_id):
                show_error(f"Cannot delete '{service_name}' because it is used in existing orders.\nPlease deactivate it instead.")
                return
                
            if show_confirm(f"Are you sure you want to delete '{service_name}'?\nThis action cannot be undone."):
                conn = get_connection()
                try:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM Services WHERE service_id = ?", (self.current_service_id,))
                    conn.commit()
                    
                    show_success(f"Service '{service_name}' deleted successfully!")
                    self.clear_form()
                    self.load_services()
                    
                except Exception as e:
                    print(f"[ServicesWindow] Error deleting service: {e}")
                    show_error(f"Failed to delete service: {str(e)}")
                finally:
                    close_connection(conn)
                    
    def is_service_in_use(self, service_id):
        """Checks if a service is used in any order items."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM OrderItems WHERE service_id = ?", (service_id,))
            result = cursor.fetchone()
            return result['count'] > 0
        except Exception:
            return False
        finally:
            close_connection(conn)
            
    def service_exists(self, name, exclude_id=None):
        """Checks if a service with the given name already exists."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            if exclude_id:
                cursor.execute(
                    "SELECT COUNT(*) as count FROM Services WHERE service_name = ? AND service_id != ?",
                    (name, exclude_id)
                )
            else:
                cursor.execute("SELECT COUNT(*) as count FROM Services WHERE service_name = ?", (name,))
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
            self.current_service_id = safe_int(values[0])
            
            # Populate form fields
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, values[1])
            
            # Extract price number from formatted string
            price_str = values[2].replace('₹', '').replace(',', '').strip()
            self.price_entry.delete(0, tk.END)
            self.price_entry.insert(0, price_str)
            
            # Extract time
            time_str = values[3].replace(' min', '').strip()
            self.time_entry.delete(0, tk.END)
            self.time_entry.insert(0, time_str if time_str != 'N/A' else '')
            
            # Set status
            status_text = values[4]
            if "Active" in status_text:
                self.status_combo.set("Active")
            else:
                self.status_combo.set("Inactive")
            
            # Enable update and delete buttons
            self.update_btn.config(state='normal')
            self.delete_btn.config(state='normal')
            self.add_btn.config(state='disabled')
            
    def clear_form(self):
        """Clears all form fields and resets button states."""
        self.name_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self.time_entry.delete(0, tk.END)
        self.status_combo.set("Active")
        self.current_service_id = None
        
        self.update_btn.config(state='disabled')
        self.delete_btn.config(state='disabled')
        self.add_btn.config(state='normal')
        
        # Clear treeview selection
        self.tree.selection_remove(self.tree.selection())
        
        # Focus on name field
        self.name_entry.focus()
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from auth import get_current_user, is_admin, is_resident, is_staff, logout_user, get_user_display_name
from helpers import format_date, center_window, show_confirm


class DashboardWindow(tk.Frame):
    """
    Dashboard Window - Main navigation hub for TeddyShine Laundry Management System.
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
        'shadow': '#BDBDBD',        
        'warning': '#FF9800',      
        'danger': '#F44336',      
    }
    
    # Button configuration for modules
    MODULES = {
        'residents': {
            'title': 'Residents',
            'icon': '👥',
            'description': 'Manage resident profiles',
            'color': '#2E7D32',
            'admin_only': False,
            'row': 0,
            'col': 0
        },
        'orders': {
            'title': 'Orders',
            'icon': '📋',
            'description': 'Create & track laundry orders',
            'color': '#388E3C',
            'admin_only': False,
            'row': 0,
            'col': 1
        },
        'services': {
            'title': 'Services',
            'icon': '🧺',
            'description': 'Manage laundry services',
            'color': '#43A047',
            'admin_only': False,
            'row': 0,
            'col': 2
        },
        'staff': {
            'title': 'Staff',
            'icon': '👨‍🔧',
            'description': 'Manage staff members',
            'color': '#4CAF50',
            'admin_only': True,
            'row': 1,
            'col': 0
        },
        'tracking': {
            'title': 'Tracking',
            'icon': '📍',
            'description': 'Track order progress',
            'color': '#66BB6A',
            'admin_only': False,
            'row': 1,
            'col': 1
        },
        'invoices': {
            'title': 'Invoices',
            'icon': '📄',
            'description': 'View & manage invoices',
            'color': '#81C784',
            'admin_only': False,
            'row': 1,
            'col': 2
        },
        'payments': {
            'title': 'Payments',
            'icon': '💰',
            'description': 'Process payments',
            'color': '#A5D6A7',
            'admin_only': False,
            'row': 2,
            'col': 0
        },
        'reports': {
            'title': 'Reports',
            'icon': '📊',
            'description': 'View analytics & reports',
            'color': '#C8E6C9',
            'admin_only': True,
            'row': 2,
            'col': 1
        }
    }
    
    def __init__(self, parent, switch_callback):
        """
        Initialize the Dashboard Window.
        """
        super().__init__(parent, bg=self.COLORS['bg'])
        self.parent = parent
        self.switch_callback = switch_callback
        
        self.current_user = get_current_user()
        
               
        # Configure grid weights
        self.grid_rowconfigure(0, weight=0)  
        self.grid_rowconfigure(1, weight=1) 
        self.grid_rowconfigure(2, weight=0)  
        self.grid_columnconfigure(0, weight=1)
        
        # Create UI sections
        self.create_top_bar()
        self.create_main_content()
        self.create_status_bar()
        
        self.update_status_bar()
        
    def create_top_bar(self):
        """Creates the top bar with welcome message and logout button."""
        top_frame = tk.Frame(
            self,
            bg=self.COLORS['primary'],
            height=80
        )
        top_frame.grid(row=0, column=0, sticky="ew")
        top_frame.grid_propagate(False)
        
        
        top_frame.grid_columnconfigure(0, weight=1)
        top_frame.grid_columnconfigure(1, weight=0)
        
        
        welcome_text = f"Welcome, {get_user_display_name()}"
        welcome_label = tk.Label(
            top_frame,
            text=welcome_text,
            font=('Helvetica', 18, 'bold'),
            bg=self.COLORS['primary'],
            fg=self.COLORS['text_light']
        )
        welcome_label.grid(row=0, column=0, padx=30, pady=20, sticky='w')
        
        # Logout button
        logout_btn = tk.Button(
            top_frame,
            text="🚪 Logout",
            font=('Helvetica', 11, 'bold'),
            bg=self.COLORS['primary_dark'],
            fg=self.COLORS['text_light'],
            activebackground=self.COLORS['primary'],
            activeforeground='white',
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=8,
            command=self.logout
        )
        logout_btn.grid(row=0, column=1, padx=30, pady=20, sticky='e')
        
        # Hover effect
        def on_enter(e):
            logout_btn.config(bg=self.COLORS['primary'])
            
        def on_leave(e):
            logout_btn.config(bg=self.COLORS['primary_dark'])
            
        logout_btn.bind("<Enter>", on_enter)
        logout_btn.bind("<Leave>", on_leave)
        
    def create_main_content(self):
        """Creates the main content area with navigation buttons."""

        canvas = tk.Canvas(self, bg=self.COLORS['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.COLORS['bg'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=canvas.winfo_reqwidth())
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=1, column=0, sticky="nsew")
        scrollbar.grid(row=1, column=1, sticky="ns")
        
        # Make canvas expandable
        self.grid_rowconfigure(1, weight=1)
        
        # Welcome card
        self.create_welcome_card(scrollable_frame)
        
        # Navigation buttons grid
        self.create_nav_buttons(scrollable_frame)
        
        # Update canvas width when window resizes
        def update_canvas_width(event):
            canvas.itemconfig(1, width=event.width)
            
        canvas.bind('<Configure>', update_canvas_width)
        
    def create_welcome_card(self, parent):
        """Creates a welcome card with user info and stats."""
        card_frame = tk.Frame(
            parent,
            bg=self.COLORS['card_bg'],
            relief='flat',
            highlightbackground=self.COLORS['border'],
            highlightthickness=1
        )
        card_frame.pack(fill='x', padx=40, pady=(30, 20))
        
        # Inner padding
        inner_frame = tk.Frame(card_frame, bg=self.COLORS['card_bg'])
        inner_frame.pack(fill='both', padx=20, pady=20)
        
        # Role badge
        role = self.current_user.get('role', 'User').title()
        role_colors = {
            'Admin': '#2E7D32',
            'Resident': '#4CAF50',
            'Staff': '#FF9800'
        }
        role_color = role_colors.get(role, '#757575')
        
        role_badge = tk.Label(
            inner_frame,
            text=role,
            font=('Helvetica', 10, 'bold'),
            bg=role_color,
            fg='white',
            padx=12,
            pady=4
        )
        role_badge.pack(anchor='w')
        
        # Welcome title
        name = self.current_user.get('name', 'User')
        title_label = tk.Label(
            inner_frame,
            text=f"Good {self.get_time_greeting()}, {name.split()[0]}!",
            font=('Helvetica', 22, 'bold'),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['primary']
        )
        title_label.pack(anchor='w', pady=(10, 5))
        
        # Subtitle
        if is_resident():
            room = self.current_user.get('room_number', 'N/A')
            block = self.current_user.get('block_name', 'N/A')
            subtitle = f"Resident • Block {block}, Room {room}"
        elif is_admin():
            subtitle = "Administrator • Full System Access"
        else:
            subtitle = "Staff Member • Limited Access"
            
        subtitle_label = tk.Label(
            inner_frame,
            text=subtitle,
            font=('Helvetica', 11),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text_secondary']
        )
        subtitle_label.pack(anchor='w')
        
        # Quick stats for admin
        if is_admin():
            self.create_quick_stats(inner_frame)
            
    def get_time_greeting(self):
        """Returns appropriate greeting based on time of day."""
        hour = datetime.now().hour
        if hour < 12:
            return "Morning"
        elif hour < 17:
            return "Afternoon"
        else:
            return "Evening"
            
    def create_quick_stats(self, parent):
        """Creates quick statistics cards for admin view."""
        stats_frame = tk.Frame(parent, bg=self.COLORS['card_bg'])
        stats_frame.pack(fill='x', pady=(20, 0))
        
        # Stats data
        stats = [
            {'label': 'Total Orders', 'value': '156', 'icon': '📋', 'color': '#2E7D32'},
            {'label': 'Pending Orders', 'value': '23', 'icon': '⏳', 'color': '#FF9800'},
            {'label': 'Active Residents', 'value': '89', 'icon': '👥', 'color': '#2196F3'},
            {'label': 'Revenue (MTD)', 'value': '₹45,280', 'icon': '💰', 'color': '#4CAF50'}
        ]
        
        for i, stat in enumerate(stats):
            stat_card = tk.Frame(
                stats_frame,
                bg=stat['color'],
                relief='flat'
            )
            stat_card.grid(row=0, column=i, padx=5, pady=5, sticky='nsew')
            
            # Configure grid weights
            stats_frame.grid_columnconfigure(i, weight=1)
            
            # Inner content
            inner = tk.Frame(stat_card, bg=stat['color'])
            inner.pack(fill='both', padx=15, pady=10)
            
            icon_label = tk.Label(
                inner,
                text=stat['icon'],
                font=('Segoe UI Emoji', 24),
                bg=stat['color'],
                fg='white'
            )
            icon_label.pack(side='left', padx=(0, 10))
            
            text_frame = tk.Frame(inner, bg=stat['color'])
            text_frame.pack(side='left', fill='both', expand=True)
            
            value_label = tk.Label(
                text_frame,
                text=stat['value'],
                font=('Helvetica', 18, 'bold'),
                bg=stat['color'],
                fg='white'
            )
            value_label.pack(anchor='w')
            
            label_label = tk.Label(
                text_frame,
                text=stat['label'],
                font=('Helvetica', 9),
                bg=stat['color'],
                fg='white'
            )
            label_label.pack(anchor='w')
            
    def create_nav_buttons(self, parent):
        """Creates the navigation buttons grid."""
        buttons_frame = tk.Frame(parent, bg=self.COLORS['bg'])
        buttons_frame.pack(fill='both', expand=True, padx=40, pady=20)
        
        # Configure grid for buttons
        for i in range(3):
            buttons_frame.grid_columnconfigure(i, weight=1)
        
        # Add buttons based on user role
        for module_id, module_config in self.MODULES.items():
            
            if module_config['admin_only'] and not is_admin():
                continue
                
            self.create_module_button(
                buttons_frame,
                module_id,
                module_config['title'],
                module_config['icon'],
                module_config['description'],
                module_config['color'],
                module_config['row'],
                module_config['col']
            )
            
    def create_module_button(self, parent, module_id, title, icon, description, color, row, col):
        """Creates a single module navigation button."""
        
        button_card = tk.Frame(
            parent,
            bg=self.COLORS['card_bg'],
            relief='flat',
            highlightbackground=self.COLORS['border'],
            highlightthickness=1,
            cursor='hand2'
        )
        button_card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        
        
        def on_click(e=None):
            if self.switch_callback:
                self.switch_callback(module_id)
                
        button_card.bind("<Button-1>", on_click)
        
        icon_frame = tk.Frame(
            button_card,
            bg=color,
            height=80
        )
        icon_frame.pack(fill='x', pady=(0, 10))
        icon_frame.pack_propagate(False)
        
        icon_label = tk.Label(
            icon_frame,
            text=icon,
            font=('Segoe UI Emoji', 36),
            bg=color,
            fg='white'
        )
        icon_label.pack(expand=True)
        
        # Content
        content_frame = tk.Frame(button_card, bg=self.COLORS['card_bg'])
        content_frame.pack(fill='both', padx=15, pady=10)
        
        title_label = tk.Label(
            content_frame,
            text=title,
            font=('Helvetica', 14, 'bold'),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['primary']
        )
        title_label.pack(anchor='w')
        
        desc_label = tk.Label(
            content_frame,
            text=description,
            font=('Helvetica', 9),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text_secondary']
        )
        desc_label.pack(anchor='w', pady=(5, 0))
        
        # Hover effects
        def on_enter(e):
            button_card.config(highlightbackground=color, highlightthickness=2)
            
        def on_leave(e):
            button_card.config(highlightbackground=self.COLORS['border'], highlightthickness=1)
            
        button_card.bind("<Enter>", on_enter)
        button_card.bind("<Leave>", on_leave)
        
        # Also bind to child widgets
        for child in [title_label, desc_label, icon_label, content_frame, icon_frame]:
            child.bind("<Button-1>", on_click)
            child.bind("<Enter>", on_enter)
            child.bind("<Leave>", on_leave)
            
    def create_status_bar(self):
        """Creates the bottom status bar."""
        self.status_frame = tk.Frame(
            self,
            bg=self.COLORS['primary_dark'],
            height=35
        )
        self.status_frame.grid(row=2, column=0, sticky="ew")
        self.status_frame.grid_propagate(False)
        
        # Status labels
        self.date_label = tk.Label(
            self.status_frame,
            font=('Helvetica', 10),
            bg=self.COLORS['primary_dark'],
            fg=self.COLORS['text_light']
        )
        self.date_label.pack(side='right', padx=20, pady=8)
        
        self.status_label = tk.Label(
            self.status_frame,
            text="✅ System Ready",
            font=('Helvetica', 10),
            bg=self.COLORS['primary_dark'],
            fg=self.COLORS['text_light']
        )
        self.status_label.pack(side='left', padx=20, pady=8)
        
    def update_status_bar(self):
        """Updates the status bar with current date/time."""
        current_date = datetime.now().strftime("%A, %d %B %Y | %I:%M %p")
        self.date_label.config(text=current_date)
        
        # Update every minute
        self.after(60000, self.update_status_bar)
        
    def logout(self):
        """Handles logout action."""
        if show_confirm("Are you sure you want to logout?"):
            logout_user()
            if self.switch_callback:
                self.switch_callback("logout")
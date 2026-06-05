import tkinter as tk
from tkinter import ttk,messagebox
from datetime import datetime
from database import get_connection, close_connection
from auth import login_user, register_user
from helpers import( show_error,show_success,center_window,validate_email,validate_phone,safe_int)

class LoginWindow(tk.Frame):
    
   COLORS={
        'bg': '#E8F0E6',           
        'primary': '#2E7D32',       
        'primary_light': '#4CAF50',
        'secondary': '#81C784',      
        'text': '#1B5E20',          
        'text_light': '#F5F5F5',    
        'border': '#A5D6A7',         
        'error': '#D32F2F',         
        'success': '#388E3C'        
   }
   
def __init__(self, parent,switch_callback):
    super().__init__(parent,bg=self.COLORS['bg'])
    self.parent=parent
    self.switch_callback=switch_callback
    self.current_user=None
    
    #Configure grid weights
    self.grid_rowconfigure(0, weight=1)
    self.grid_columnconfigure(0, weight=1)
    
    #create main container
    self.create_main_container()
    
    def create_main_container(self):
        self.main_frame=tk.Frame(
            self,bg=self.COLORS['bg']
        )
        self.main_frame.grid(row=0, column=0, sticky="msew")
        
        self.main_frame.grid_rowconfigure(0,weight=1)
        self.main_frame.grid_rowconfigure(4,weight=1)
        self.main_frame.grid_columnconfigure(0,weight=1)
        self.main_frame.grid_columnconfigure(2,weight=1)
        
        #Form container
        self.form_container= tk.Frame(
            self.main_frame,
            bg='white',
            highlightbackground=self.COLORS['border'],
            highlightthickness=1,
            relief='flat'
        )
        self.form_container.grid(row=1, column=1, padx=40, pady=40, sticky="nsew")

        self.create_header()
        self.create_tabs()
        
        def create_header(self):
            """Creates the app header with logo and title."""
            logo_frame= tk.Frame(self.form_container, bg='white')
            logo_frame.pack(pady=(30,10))
            
            logo_label= tk.Label(
                logo_frame,
                text="🧺",
                font=('segoe UI Emoji',48),
                bg='white',
                fg=self.COLORS['primary']
            )


            logo_label.pack()
            
            title_label=tk.Label(
                self.form_container,
                text="TeddyShine Laundary",
                font=('Helvetica', 28,'bold'),
                bg=self.COLORS['primary']
            )
            title_label.pack()
            
            subtitle_label= tk.Label(
                self.form_container,
                text="Professional Laundary Management Syatem",
                font=('Helvetica', 10),
                bg='white',
                fg=self.COLORS['text']
            )
            subtitle_label.pack(pady=(5,20))
def create_tabs(self):
      """Creates the notebook tabs for Login and Sign Up."""
      self.notebook= ttk.Notebook(self.form_container)
      self.notebook.pack(padx=10, pady=0, fill='both', expand=True)
      
      style= ttk.Style()
      style.configure('TNotebook.Tab', padding=[20, 5], font=('Helvetica', 11))
      
      self.login_frame=tk.Frame(self.notebook, bg='white')
      self.notebook.add(self.login_frame, text="Login")
      self.create_login_tab()
      
      self.signup_frame= tk.Frame(self.notebook, bg='white')
      self.notebook.add(self.signup_frame, text="Sign Up")
      self.create_signup_tab()
      
      def create_login_tab(self):
        """Creates the login form inside the Login tab."""
        email_label=tk.Label(
              self.login_frame,
              text="Email Address",
              font=('Helvetica', 11),
              bg='white',
              fg=self.COLORS['text']
          )
        email_label.pack(anchor='w', pady=(30, 5))
          
        self.email_entry=tk.Entry(
                self.login_frame,
              font=('Helvetica', 11),
              bg='#FAFAFA',
              relief='solid',
              bd=1,
                highlightthickness=1,
                highlightcolor=self.COLORS['primary']
          )
        self.email_entry.pack(fill='x', pady=(0, 15), ipady=8)
          
    #password field
        password_label= tk.Label(
                self.login_frame,
            text="password",
            font=('Helvetica', 11),
            bg='white',
            fg=self.COLORS['text']
        )
        password_label.pack(anchor='w', pady=(0, 5))

        self.password_entry= tk.Entry(
            self.login_frame,
            font=('Helvetica', 11),
            bg='#FAFAFA',
            relief='solid',
            bd=1,
            show='*',
            highlightthickness=1,
            highlightcolor=self.COLORS['primary']
        )
        self.password_entry.pack(fill='x', pady=(0, 20), ipady=8)

        # Bind Enter key to login
        self.password_entry.bind('<Return>', lambda e: self.login_action())

        #login button
        self.login_button=tk.Button(
            self.login_frame,
            text="Login",
            font=('Helvetica', 12,'bold'),
            bg=self.COLORS['primary'],
            fg=self.COLORS['text_light'],
            activebackground=self.COLORS['primary_light'],
            activeforeground='white',
            relief='flat',
            cursor='hand2',
            bd=0,
            padx=20,
            pady=10,
            command=self.login_action
        )
        self.login_button.pack(fill='x', pady=(10, 20))

        # Demo credentials 
        demo_label=tk.Label(
            self.login_frame,
            text="Demo Credentials:\nResident: Ali@gmail.com /password1234\n Admin: admin@teddyshine.com /admin1234",
            font=('Helvetica', 8),
            bg='white',
            fg='#757575',
            justify='left'
            )

def create_signup_tab(self):
    """Creates the registration form inside the Sign Up tab with scrollbar."""
    
    # Create a canvas with scrollbar
    canvas = tk.Canvas(self.signup_frame, bg='white', highlightthickness=0)
    scrollbar = tk.Scrollbar(self.signup_frame, orient="vertical", command=canvas.yview)
    
    scrollable_frame = tk.Frame(canvas, bg='white')
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Pack the canvas and scrollbar
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Bind mouse wheel for scrolling
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    canvas.bind("<MouseWheel>", on_mousewheel)
    scrollable_frame.bind("<MouseWheel>", on_mousewheel)
    
    first_name_label = tk.Label(
        scrollable_frame,  
        text="First Name",
        font=('Helvetica', 11),
        bg='white',
        fg=self.COLORS['text']
    )
    first_name_label.pack(anchor='w', pady=(10, 5))
    
    self.first_name_entry = tk.Entry(
        scrollable_frame,  
        bg='#FAFAFA',
        relief='solid',
        bd=1,
    )
    self.first_name_entry.pack(fill='x', pady=(0, 8), ipady=8)
    
    last_name_label = tk.Label(
        scrollable_frame,  
        text="Last Name",
        font=('Helvetica', 11),
        bg='white',
        fg=self.COLORS['text']
    )
    last_name_label.pack(anchor='w', pady=(0, 5))
    
    self.last_name_entry = tk.Entry(
        scrollable_frame,  
        bg='#FAFAFA',
        relief='solid',
        bd=1,
    )
    self.last_name_entry.pack(fill='x', pady=(0, 8), ipady=8)
    
    signup_email_label = tk.Label(
        scrollable_frame, 
        text="Email Address",
        font=('Helvetica', 11),
        bg='white',
        fg=self.COLORS['text']
    )
    signup_email_label.pack(anchor='w', pady=(0, 5))
    
    self.signup_email_entry = tk.Entry(
        scrollable_frame,  
        bg='#FAFAFA',
        relief='solid',
        bd=1,
    )
    self.signup_email_entry.pack(fill='x', pady=(0, 8), ipady=8)
    
    phone_label = tk.Label(
        scrollable_frame,  
        text="Phone Number",
        font=('Helvetica', 11),
        bg='white',
        fg=self.COLORS['text']
    )
    phone_label.pack(anchor='w', pady=(0, 5))
    
    self.phone_entry = tk.Entry(
        scrollable_frame, 
        font=('Helvetica', 11),
        bg='#FAFAFA',
        relief='solid',
        bd=1,
    )
    self.phone_entry.pack(fill='x', pady=(0, 8), ipady=8)
    
    # Room details frame
    room_frame = tk.Frame(scrollable_frame, bg='white')  
    room_frame.pack(fill='x', pady=(0, 8))
    
    block_label = tk.Label(
        room_frame,
        text="Block",
        font=('Helvetica', 11),
        bg='white',
        fg=self.COLORS['text']
    )
    block_label.pack(side='left', padx=(0, 10))
    
    self.block_entry = tk.Entry(
        room_frame,
        font=('Helvetica', 11),
        bg='#FAFAFA',
        relief='solid',
        bd=1,
        width=8
    )
    self.block_entry.pack(side='left', padx=(0, 20))
    
    room_label = tk.Label(
        room_frame,
        text="Room No",
        font=('Helvetica', 11),
        bg='white',
        fg=self.COLORS['text']
    )
    room_label.pack(side='left', padx=(0, 10))
    
    self.room_entry = tk.Entry(
        room_frame,
        font=('Helvetica', 11),
        bg='#FAFAFA',
        relief='solid',
        bd=1,
        width=8
    )
    self.room_entry.pack(side='left')
    
    signup_password_label = tk.Label(
        scrollable_frame,  
        text="Password",
        font=('Helvetica', 11),
        bg='white',
        fg=self.COLORS['text']
    )
    signup_password_label.pack(anchor='w', pady=(0, 5))
    
    self.signup_password_entry = tk.Entry(
        scrollable_frame,  
        font=('Helvetica', 11),
        bg='#FAFAFA',
        relief='solid',
        bd=1,
        show="•"
    )
    self.signup_password_entry.pack(fill='x', pady=(0, 8), ipady=8)
    
    confirm_label = tk.Label(
        scrollable_frame, 
        text="Confirm Password",
        font=('Helvetica', 11),
        bg='white',
        fg=self.COLORS['text']
    )
    confirm_label.pack(anchor='w', pady=(0, 5))
    
    self.confirm_entry = tk.Entry(
        scrollable_frame, 
        font=('Helvetica', 11),
        bg='#FAFAFA',
        relief='solid',
        bd=1,
        show="•"
    )
    self.confirm_entry.pack(fill='x', pady=(0, 15), ipady=8)
    
    self.register_button = tk.Button(
        scrollable_frame,  
        text="Create Account",
        font=('Helvetica', 12,'bold'),
        bg=self.COLORS['primary'],
        fg=self.COLORS['text_light'],
        activebackground=self.COLORS['primary_light'],
        activeforeground='white',
        relief='flat',
        cursor='hand2',
        bd=0,
        padx=20,
        pady=10,
        command=self.register_action
    )
    self.register_button.pack(fill='x', pady=(5, 15))
    
        
    def login_action(self):
           """Handles the login button click - authenticates user."""
           email=self.email_entry.get().strip()
           password=self.password_entry.get()
           
    if not email or not password:
                show_error("Please enter both email and password.")
                return 
        
    if not validate_email(email):
            show_error("Please enter a valid email address.")
            return
        
    success=login_user(email, password)
        
    if success:
            from auth import get_current_user
            user=get_current_user()
            show_success(f"Welcome back, {user.get('name', 'User')}!")
            
            #clear enteries
            self.email_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            
            #switch to main Dashboard
    if self.switch_callback:
            self.switch_callback()
    else:
            show_error("Invalid email or password. Please try again.")
            self.password_entry.delete(0, tk.END)
            self.password_entry.focus()
            
    def register_action(self):
          """Handles the registration button click - creates new user account."""
    first_name = self.first_name_entry.get().strip()
    last_name = self.last_name_entry.get().strip()
    email = self.signup_email_entry.get().strip()
    phone = self.phone_entry.get().strip()
    block = self.block_entry.get().strip().upper()
    room = self.room_entry.get().strip()
    password = self.signup_password_entry.get()
    confirm = self.confirm_entry.get()            
        
        #validation
    if not all([first_name, last_name, email,phone, block,room,password]):
            show_error("Please fill in all the fields.")
            return
    if not validate_email(email):
            show_error("Please enter a valid email address.")
            return
        
    if not validate_phone(phone):
            show_error("Please enter a valid 10-digit  phone number.")
            return
        
    if len(password) < 6:
            show_error("Password must be at least 6 characters long.")
            return
    if password != confirm:
            show_error("Passwords do not match. Please try again.")
            return
        
    if self.email_exists(email):
            show_error("An account with this email already exists. Please login instead.")
            self.notebook.select(0)
            return
        
     #create resident account
    resident_id=self.create_resident(first_name, last_name, email, phone, block, room)
       
    if resident_id:
            username= f"{first_name.lower()}_{last_name.lower()}_{room}"
            success= register_user(resident_id, username, password)
            
            if success:
                show_success("Account created successfully! Please login to continue.")
                self.clear_signup_form()
                self.notebook.select(0)
                
                self.email_entry.delete(0, tk.END)
                self.email_entry.insert(0, email)
            else:
                show_error("Failed to create account login credentials. Please contact support.")
    else:
            show_error("Failed to create account. Please try again.")
            
    def create_resident(self, first_name, last_name, email, phone, block, room):
             """Creates a new resident record in the database.
        Returns:
            int: Resident ID if successful, None otherwise"""
            
    full_name=f"{first_name} {last_name}"
        
    conn= get_connection()
    try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Resident (full_name, email, phone, block_name, room_number, is_active)
                VALUES (?, ?, ?, ?, ?, 1)
            """, (full_name, email, phone, block, room))
            conn.commit()    
            
             # Get the generated resident_id
            resident_id = cursor.lastrowid
            return resident_id       
         
    except Exception as e:
        print(f"[loginWindow] Error creating resident {e}")
        return None
    finally:
            close_connection(conn)
            
def email_exists(self, email):
         """Checks if an email already exists in the Resident table."""
         conn= get_connection()
         try:
             cursor =conn.cursor()
             cursor.execute("SELECT COUNT(*) as count FROM Resident WHERE email = ?", (email,))
             result=cursor.fetchone()
             return result['count'] > 0
         except Exception as e:
            print(f"{LoginWindow} Error checking email: {e}")
            return False
         finally:
             close_connection(conn)
                     
def clear_signup_form(self):
         """Clears all fields in the signup form."""
         self.first_name_entry.delete(0, tk.END)
         self.last_name_entry.delete(0, tk.END)
         self.signup_email_entry.delete(0, tk.END)
         self.phone_entry.delete(0, tk.END)
         self.block_entry.delete(0, tk.END)
         self.room_entry.delete(0, tk.END)
         self.signup_password_entry.delete(0, tk.END)
         self.confirm_entry.delete(0, tk.END)            
             
            
                    
                 
            



        
 
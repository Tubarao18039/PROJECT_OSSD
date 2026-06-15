"""
 Database Schema Module
Module: schema.py
Purpose: Create all 15 database tables if they don't exist
"""

from database import get_connection, close_connection


# ==============================================
# TABLE CREATION FUNCTION
# ==============================================

def create_tables():
    """
    Creates all 15 tables in the correct foreign key order.
    Call this once from main.py before the app window opens.
    
    Table Creation Order (no circular dependencies):
    1. Resident
    2. SignUp
    3. Login
    4. Staff
    5. DeliverySlots
    6. LaundryItem
    7. ProcessStage
    8. Services
    9. Orders
    10. OrderItems
    11. Tracking
    12. Invoice
    13. Payments
    14. Records
    15. Print
    """
    
    conn = get_connection()
    
    if conn is None:
        print("[Schema Error] Cannot create tables - database connection failed")
        return False
    
    try:
        cursor = conn.cursor()
        
        # ==============================================
        # TABLE 1: Resident
        # ==============================================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Resident (
                resident_id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT NOT NULL,
                room_number TEXT NOT NULL,
                block_name TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # ==============================================
        # TABLE 2: SignUp
        # ==============================================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS SignUp (
                signup_id INTEGER PRIMARY KEY AUTOINCREMENT,
                resident_id INTEGER NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                security_question TEXT,
                security_answer TEXT,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (resident_id) REFERENCES Resident(resident_id) ON DELETE CASCADE
            )
        ''')
        
        # ==============================================
        # TABLE 3: Login
        # ==============================================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Login (
                login_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                user_type TEXT NOT NULL CHECK(user_type IN ('resident', 'admin', 'staff')),
                login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                session_token TEXT,
                is_active INTEGER DEFAULT 1
            )
        ''')
        
        # ==============================================
        # TABLE 4: Staff
        # ==============================================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Staff (
                staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('Washer', 'Dryer', 'Ironer', 'Packer', 'Delivery', 'Admin')),
                hire_date DATE NOT NULL,
                salary REAL DEFAULT 0,
                is_available INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # ==============================================
        # TABLE 5: DeliverySlots
        # ==============================================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS DeliverySlots (
                slot_id INTEGER PRIMARY KEY AUTOINCREMENT,
                slot_date DATE NOT NULL,
                slot_time TEXT NOT NULL,
                max_orders INTEGER DEFAULT 10,
                booked_orders INTEGER DEFAULT 0,
                is_available INTEGER DEFAULT 1
            )
        ''')
        
        # ==============================================
        # TABLE 6: LaundryItem
        # ==============================================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS LaundryItem (
                laundry_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL,
                category TEXT NOT NULL,
                base_price REAL NOT NULL,
                is_active INTEGER DEFAULT 1
            )
        ''')
        
        # ==============================================
        # TABLE 7: ProcessStage
        # ==============================================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ProcessStage (
                stage_id INTEGER PRIMARY KEY AUTOINCREMENT,
                stage_name TEXT NOT NULL UNIQUE,
                stage_order INTEGER NOT NULL,
                estimated_minutes INTEGER DEFAULT 30,
                is_active INTEGER DEFAULT 1
            )
        ''')
        
        # ==============================================
        # TABLE 8: Services
        # ==============================================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Services (
                service_id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT NOT NULL UNIQUE,
                description TEXT,
                base_price REAL NOT NULL,
                price_per_kg REAL,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # ==============================================
        # TABLE 9: Orders
        # ==============================================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_number TEXT UNIQUE NOT NULL,
                resident_id INTEGER NOT NULL,
                staff_id INTEGER,
                slot_id INTEGER,
                total_weight_kg REAL DEFAULT 0,
                total_amount REAL DEFAULT 0,
                discount_amount REAL DEFAULT 0,
                final_amount REAL DEFAULT 0,
                status TEXT DEFAULT 'Pending' CHECK(status IN ('Pending', 'Processing', 'Completed', 'Cancelled', 'Delivered')),
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expected_delivery_date DATE,
                actual_delivery_date DATE,
                special_instructions TEXT,
                FOREIGN KEY (resident_id) REFERENCES Resident(resident_id),
                FOREIGN KEY (staff_id) REFERENCES Staff(staff_id),
                FOREIGN KEY (slot_id) REFERENCES DeliverySlots(slot_id)
            )
        ''')
        
        # ==============================================
        # TABLE 10: OrderItems
        # ==============================================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS OrderItems (
                order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                laundry_item_id INTEGER,
                service_id INTEGER NOT NULL,
                quantity INTEGER DEFAULT 1,
                unit_price REAL NOT NULL,
                subtotal REAL NOT NULL,
                FOREIGN KEY (order_id) REFERENCES Orders(order_id) ON DELETE CASCADE,
                FOREIGN KEY (laundry_item_id) REFERENCES LaundryItem(laundry_item_id),
                FOREIGN KEY (service_id) REFERENCES Services(service_id)
            )
        ''')
        
        # ==============================================
        # TABLE 11: Tracking
        # ==============================================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Tracking (
                tracking_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                stage_id INTEGER NOT NULL,
                staff_id INTEGER,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                status TEXT DEFAULT 'InProgress' CHECK(status IN ('Pending', 'InProgress', 'Completed', 'Failed')),
                notes TEXT,
                FOREIGN KEY (order_id) REFERENCES Orders(order_id) ON DELETE CASCADE,
                FOREIGN KEY (stage_id) REFERENCES ProcessStage(stage_id),
                FOREIGN KEY (staff_id) REFERENCES Staff(staff_id)
            )
        ''')
        
        # ==============================================
        # TABLE 12: Invoice
        # ==============================================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Invoice (
                invoice_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL UNIQUE,
                invoice_number TEXT UNIQUE NOT NULL,
                subtotal REAL NOT NULL,
                discount_amount REAL DEFAULT 0,
                tax_amount REAL DEFAULT 0,
                total_amount REAL NOT NULL,
                amount_paid REAL DEFAULT 0,
                balance_due REAL DEFAULT 0,
                status TEXT DEFAULT 'Unpaid' CHECK(status IN ('Unpaid', 'Partial', 'Paid', 'Overdue')),
                generated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                due_date DATE,
                paid_date TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES Orders(order_id) ON DELETE CASCADE
            )
        ''')
        
        # ==============================================
        # TABLE 13: Payments
        # ==============================================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Payments (
                payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER NOT NULL,
                order_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                payment_method TEXT CHECK(payment_method IN ('Cash', 'Card', 'Online', 'Wallet')),
                payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                transaction_id TEXT UNIQUE,
                status TEXT DEFAULT 'Completed' CHECK(status IN ('Pending', 'Completed', 'Failed', 'Refunded')),
                notes TEXT,
                FOREIGN KEY (invoice_id) REFERENCES Invoice(invoice_id),
                FOREIGN KEY (order_id) REFERENCES Orders(order_id)
            )
        ''')
        
        # ==============================================
        # TABLE 14: Records
        # ==============================================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Records (
                record_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                action_type TEXT NOT NULL CHECK(action_type IN ('Created', 'Updated', 'Status_Changed', 'Payment', 'Deleted')),
                old_value TEXT,
                new_value TEXT,
                changed_by TEXT NOT NULL,
                changed_by_id INTEGER NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                FOREIGN KEY (order_id) REFERENCES Orders(order_id)
            )
        ''')
        
        # ==============================================
        # TABLE 15: Print
        # ==============================================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Print (
                print_id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER NOT NULL,
                receipt_number TEXT UNIQUE NOT NULL,
                printed_by TEXT NOT NULL,
                printed_by_id INTEGER NOT NULL,
                print_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_path TEXT,
                copies INTEGER DEFAULT 1,
                status TEXT DEFAULT 'Success' CHECK(status IN ('Success', 'Failed', 'Retry')),
                FOREIGN KEY (invoice_id) REFERENCES Invoice(invoice_id)
            )
        ''')
        
        # ==============================================
        # CREATE INDEXES FOR BETTER PERFORMANCE
        # ==============================================
        print("\n[Schema] Creating indexes for performance...")
        
        # Resident indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_resident_email ON Resident(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_resident_room ON Resident(block_name, room_number)")
        
        # Orders indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_resident ON Orders(resident_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_status ON Orders(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_date ON Orders(order_date)")
        
        # Tracking indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tracking_order ON Tracking(order_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tracking_status ON Tracking(status)")
        
        # Invoice & Payments indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoice_order ON Invoice(order_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoice_status ON Invoice(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_payments_invoice ON Payments(invoice_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_payments_date ON Payments(payment_date)")
        
        # Login & Records indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_login_user ON Login(user_id, user_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_records_order ON Records(order_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_records_timestamp ON Records(timestamp)")
        
        # Commit all changes
        conn.commit()
        
        print("[Schema] All 15 tables created successfully!")
        print("[Schema] Indexes created for optimized queries.")
        
        return True
        
    except Exception as e:
        print(f"[Schema Error] Failed to create tables: {e}")
        if conn:
            conn.rollback()
        return False
    
    finally:
        close_connection(conn)


# ==============================================
# VERIFICATION FUNCTION (optional)
# ==============================================

def verify_tables():
    """
    Verifies that all 15 tables exist in the database.
    Returns a dictionary with table names and their existence status.
    """
    expected_tables = [
        'Resident', 'SignUp', 'Login', 'Staff', 'DeliverySlots',
        'LaundryItem', 'ProcessStage', 'Services', 'Orders', 'OrderItems',
        'Tracking', 'Invoice', 'Payments', 'Records', 'Print'
    ]
    
    conn = get_connection()
    result = {}
    
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = [row['name'] for row in cursor.fetchall()]
            
            for table in expected_tables:
                result[table] = table in existing_tables
            
        except Exception as e:
            print(f"[Verify Error] {e}")
            result = {table: False for table in expected_tables}
        finally:
            close_connection(conn)
    else:
        result = {table: False for table in expected_tables}
    
    return result


# ==============================================
# DROP ALL TABLES (for development/reset)
# ==============================================

def drop_all_tables():
    """
    WARNING: Drops all 15 tables. Use only for development/reset.
    """
    tables = [
        'Print', 'Records', 'Payments', 'Invoice', 'Tracking',
        'OrderItems', 'Orders', 'Services', 'ProcessStage',
        'LaundryItem', 'DeliverySlots', 'Staff', 'Login',
        'SignUp', 'Resident'
    ]
    
    conn = get_connection()
    
    if conn:
        try:
            cursor = conn.cursor()
            for table in tables:
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
            conn.commit()
            print("[Schema] All tables dropped successfully.")
            return True
        except Exception as e:
            print(f"[Schema Error] Failed to drop tables: {e}")
            return False
        finally:
            close_connection(conn)
    
    return False


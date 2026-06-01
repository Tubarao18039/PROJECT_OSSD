🧺 Housing Society Laundry Management System
An open-source desktop application built with Python Tkinter to digitally manage laundry services for housing societies. The system provides role-based access for residents, staff, and administrators to efficiently handle laundry orders, tracking, billing, and reporting.

📋 Table of Contents
Overview
Features
Technology Stack
[Installation & How to Run](#-installation--how to-run)
Default Login Credentials
Project Structure
User Guide
License
Acknowledgments
Security Note
📖 Overview
The Housing Society Laundry Management System replaces traditional manual laundry management methods (registers, paper tokens, phone calls) with a reliable, efficient, and transparent digital solution. The system eliminates lost requests, delayed deliveries, billing errors, and a lack of transparency.

Key Benefits
✅ Reduces manual effort: Streamlines placing and tracking orders.
✅ Improves accuracy: Eradicates errors in billing and service records.
✅ Ensures transparency: Real-time order tracking accessible to residents.
✅ Provides history: Maintains a complete digital history of all transactions.
✅ Open Source: 100% free for any housing society to deploy and use.
✨ Features
👤 For Residents
📝 Place Laundry Orders: Select cloth type, quantity, and service (Wash, Iron, Dry Clean).
📊 Track Orders: Visual progress indicator (Pending → Received → Washing → Drying → Folded → Delivered).
💰 View Bills: Complete billing history with detailed itemized invoices.
User Registration: Self-registration portal linked with the resident's flat number.
📋 For Staff
View All Orders: Consolidated view of all pending and active orders.
🔄 Update Order Status: Double-click function to move orders through processing stages.
👁️ Real-time Updates: Changes reflect instantly on the resident's dashboard.
📊 For Admin
👥 User Management: Authorize, view, and delete resident/staff accounts.
📊 Reports Generation: Generate filtered daily, weekly, and monthly operational reports.
📈 Revenue Tracking: Monitor total revenue metrics and overall order statistics.
🔍 Complete Oversight: Ultimate control to monitor all orders and active system data.
⚙️ General Features
🔐 Role-Based Access Control: Separate, dedicated dashboards for each user type.
💾 SQLite Database: Lightweight, zero-configuration local database engine.
📱 Desktop Application: Works completely offline with no internet connection required.
🎨 User-Friendly GUI: Intuitive interface styled cleanly with standard Python Tkinter components.
🛠️ Technology Stack
Component	Technology
Frontend	Python Tkinter (Built-in)
Database	SQLite3 (Built-in)
Language	Python 3.6+
Version Control	Git & GitHub
License	MIT Open Source
💡 No external dependencies required! Everything utilized in this project relies entirely on Python's standard library.

📥 Installation & How to Run
Prerequisites
Python 3.6 or higher installed on your system.
Basic knowledge of running Python scripts via terminal/command prompt.
Steps
Clone or Download the Repository:
git clone [https://github.com/yourusername/laundry-management-system.git](https://github.com/yourusername/laundry-management-system.git)
cd laundry-management-system

Run the Application:
Launch the main file to initialize the SQLite database automatically and open the login screen.

Bash python main.py 🔑 Default Login Credentials (Optional: If your database_helper.py or seed_data includes pre-configured administrative accounts, document them here for easy testing access)

Admin Username: admin | Password: admin123

Staff Username: staff01 | Password: staff123

📁 Project Structure Plaintext laundry-management-system/ │ ├── main.py # Entry point - initializes DB & launches application ├── login_window.py # User authentication & registration handler ├── resident_dashboard.py # Resident portal (place orders, track, view bills) ├── staff_dashboard.py # Staff portal (view and update active orders) ├── admin_dashboard.py # Admin portal (user controls, reporting dashboards) ├── order_form.py # Selection interface for clothes, services, and pricing ├── order_status.py # Progress bar and visual order tracking component ├── billing.py # Invoice compilation and historical records ├── database_helper.py # Centralized SQLite database connector and queries ├── utils.py # Validation scripts and text formatting helper tools │ ├── laundry_system.db # SQLite database file (Auto-created on first run) └── README.md # Project documentation 📖 User Guide 👤 For Residents

Registering an Account Click "New User? Register Here" on the main login screen.
Fill out your details (Name, Username, Password, Email, Phone, and Flat Number).

Select your role as "Resident" and submit.

Log in using your newly generated credentials.

Placing an Order Click "📝 Place New Order" from your dashboard.
Select the cloth type, quantity, and requested service type.

Click "Add Item" (repeat this step to add multiple items to a single order).

Review the total calculated amount and click "Submit Order".

Tracking & Bills Track Orders: Go to "📊 Track Orders" and select an order to view its real-time progress.
Viewing Bills: Go to "💰 View Bills" and double-click any order row to review an individual itemized invoice.

📋 For Staff Updating Order Status Log into your account with your assigned staff credentials.

Review the consolidated table showing all pending and active orders.

Double-click on any order row to step it forward to its next phase.

The status updates sequentially: pending → received → washing → drying → folded → delivered.

Click "Refresh" at any time to sync modifications.

📊 For Admin

Managing Users Navigate to the "👥 Manage Users" tab.
View all active accounts categorized by residents and staff.

Highlight any user account and click "Delete User" to clean up records and clear associated data safely.

Generating Reports Navigate to the "📊 Reports" tab.
Filter data by selecting a timeframe: Daily, Weekly, or Monthly.

Click "Generate Report" to populate charts and summaries including:

Total order volume

Gross revenue metrics

Breakdown of completed vs. pending tasks

Granular historical order streams

📄 License MIT License

Copyright (c) 2026 Shehroz, Tuba, Shehreen

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

🙏 Acknowledgments The Python Tkinter community for extensive documentation on building lightweight graphical layouts.

SQLite for providing a resilient, serverless database module out of the box.

All open-source contributors whose collaborative spirits keep building accessible technology.

🔒 Security Note Password Security: Passwords are fully hashed using SHA-256 inside the database system to ensure they are never stored in plain text.

Data Management: All core system data lives strictly inside the single laundry_system.db file.

Production Recommendations: If adapting this software for real-world application deployments, prioritize scheduling regular database backups, establishing robust password validation criteria, and ensuring appropriate host system network firewalls

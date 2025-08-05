SS Star Flex - Inventory and Order Management System
A comprehensive web-based inventory and order management system built with Flask and PostgreSQL for managing card inventory, customer orders, and payment tracking.

🌟 Features
Core Functionality
User Authentication: Secure login system with role-based access (Admin/User)
Inventory Management: Add, edit, delete, and track card inventory with real-time allocation tracking
Order Management: Create orders with automatic ID generation (monthly format: mmyyyyxxx)
Payment Tracking: Record payments and transactions with automatic balance calculation
Customer Management: Store customer information including phone numbers
Advanced Features
Real-time Stock Tracking: Automatic allocation and availability calculations
Date Range Filtering: Filter orders and data by custom date ranges
Search & Filter: Advanced search and filtering across all modules
Dashboard Analytics: Summary cards showing key business metrics
Multi-user Support: Concurrent user access with session management
Export Functionality: Export orders and data for reporting
User Interface
Responsive Design: Works on desktop, tablet, and mobile devices
Modern UI: Clean, professional interface with Font Awesome icons
Real-time Feedback: Flash messages and loading states
Interactive Elements: Dynamic calculations and validations
🛠️ Technology Stack
Backend: Flask (Python)
Database: PostgreSQL
Frontend: HTML5, CSS3, JavaScript (Vanilla)
Authentication: Custom session-based authentication
Styling: Custom CSS with Font Awesome icons
📋 Prerequisites
Python 3.7 or higher
PostgreSQL 12 or higher
pip (Python package installer)
🚀 Installation & Setup
1. Clone the Repository:

git clone https://github.com/jothyanandanch/shop-management.git

2. Install Dependencies
pip install -r requirements.txt

3. Database Setup
Create PostgreSQL database create a database and change the name in dbconnection #I named it shop

Run the database initialization python init_db.py

4. Start the Application
📌 Usage

Add new card designs and stock quantities
Create customer records and link orders
Generate bills based on selected cards and quantity
View order history and inventory status
🧠 Future Enhancements

AI-powered demand prediction for stock planning
Customer insights through data analytics
Admin panel for managing users and roles

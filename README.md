# SS Star Flex - Inventory and Order Management System

A comprehensive web-based inventory and order management system built with Flask and PostgreSQL for managing card inventory, customer orders, and payment tracking.

---

## 🌟 Features

### Core Functionality
- **User Authentication**: Secure login system with role-based access (Admin/User)
- **Inventory Management**: Add, edit, delete, and track card inventory with real-time allocation tracking
- **Order Management**: Create orders with automatic ID generation (monthly format: `mmyyyyxxx`)
- **Payment Tracking**: Record payments and transactions with automatic balance calculation
- **Customer Management**: Store customer information including phone numbers

### Advanced Features
- **Real-time Stock Tracking**: Automatic allocation and availability calculations
- **Date Range Filtering**: Filter orders and data by custom date ranges
- **Search & Filter**: Advanced search and filtering across all modules
- **Dashboard Analytics**: Summary cards showing key business metrics
- **Multi-user Support**: Concurrent user access with session management
- **Export Functionality**: Export orders and data for reporting

### User Interface
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Modern UI**: Clean, professional interface with Font Awesome icons
- **Real-time Feedback**: Flash messages and loading states
- **Interactive Elements**: Dynamic calculations and validations

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Flask (Python) |
| **Database** | PostgreSQL |
| **Frontend** | HTML5, CSS3, JavaScript (Vanilla) |
| **Authentication** | Custom session-based authentication |
| **Styling** | Custom CSS with Font Awesome icons |

---

## 📋 Prerequisites

- Python 3.7 or higher
- PostgreSQL 12 or higher
- pip (Python package installer)

---

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/jothyanandanch/shop-management.git
cd shop-management
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Database Setup
1. Create a PostgreSQL database
2. Update the database name in `dbconnection.py`
3. Initialize the database:
   ```bash
   python init_db.py
   ```

### 4. Start the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

---

## 📌 Usage

1. **Inventory Management**: Add new card designs and stock quantities
2. **Customer Management**: Create customer records and link orders
3. **Order Processing**: Generate bills based on selected cards and quantity
4. **Analytics**: View order history and inventory status

---

## 🧠 Future Enhancements

- [ ] AI-powered demand prediction for stock planning
- [ ] Customer insights through data analytics
- [ ] Enhanced admin panel for managing users and roles

---

## 🤝 Contributing

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---


<div align="center">
  Made with ❤️ by Your Team
</div>

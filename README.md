# 🚜 Farmer Ledger (Rythu Lekka)

A robust, Flask-based inventory and financial management system designed specifically for agri-businesses (like chili and tomato trading). This web application streamlines tracking transactions between farmers and businessmen, manages ledgers, securely handles user accounts, and generates printable financial statements.

## ✨ Key Features

* **🔐 Secure Authentication:** * Custom login system with strong password enforcement and secure SQLite database hashing.
    * Google OAuth 2.0 integration for seamless "Login with Google".
    * Simulated OTP (One-Time Password) phone verification flow.
* **🧑‍🌾 Farmer Management:**
    * Calculate daily agricultural bills using custom metrics (Total Kilos, Bags, Market Price, Extra Amount).
    * Automatic "Manumulu" conversions (Total weight / 11.25).
* **💼 Businessman Sales:**
    * Track outgoing inventory (bags sold) to various businessmen.
    * Settle pending sales and maintain historical sales records.
* **📊 Financial Dashboard & Ledgers:**
    * Real-time dashboard showing Total Bags, Total Weight, and Total Business Revenue.
    * Individual farmer ledgers with date-to-date filtering to calculate exact pending balances.
    * Record and track payments made to farmers.
* **🖨️ Printable Statements:**
    * Generate clean, printable bill statements and payment receipts for physical record-keeping.

## 🛠️ Tech Stack

* **Backend:** Python 3, Flask
* **Database:** SQLite, Flask-SQLAlchemy
* **Authentication:** Flask-Login, Authlib (Google OAuth), Werkzeug Security
* **Frontend:** HTML5, CSS3, Jinja2 Templates
* **Deployment:** Gunicorn, Render
https://rythu-lekka.onrender.com/dashboard
## 🚀 Local Setup & Installation

Follow these steps to run the application on your local machine:

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/Abhinayreddylekkala/Farmer-Ledger.git](https://github.com/Abhinayreddylekkala/Farmer-Ledger.git)
   cd Farmer-Ledger
   

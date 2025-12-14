"""
Configuration file for Food Finder app.
Store your MySQL credentials and settings here.
"""

# ============================================================================
# MySQL DATABASE CONFIGURATION
# ============================================================================
# Set to True to enable MySQL. If False, app uses CSV files (dataset.csv, zomato.csv)
USE_MYSQL = True

# MySQL server connection details
MYSQL_HOST = 'localhost'          # Your MySQL server address (e.g., 'localhost', '127.0.0.1', or remote IP)
MYSQL_PORT = 3306                 # MySQL port (default: 3306)
MYSQL_USER = 'root'               # Your MySQL username (e.g., 'root')
MYSQL_PASSWORD = 'Koti@6102'      # Your MySQL password
MYSQL_DB = 'food_finder'          # Database name to create/use

# ============================================================================
# EMAIL CONFIGURATION (for contact form)
# ============================================================================
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'your_email@gmail.com'        # ⚠️ CHANGE THIS: Your Gmail address
MAIL_PASSWORD = 'your_app_password'           # ⚠️ CHANGE THIS: Gmail app password (not your regular password)
MAIL_DEFAULT_SENDER = 'your_email@gmail.com'  # Same as MAIL_USERNAME

# ============================================================================
# FLASK CONFIGURATION
# ============================================================================
SECRET_KEY = 'replace-this-with-a-strong-random-secret-key'  # Change this to a random string
DEBUG = False

# ============================================================================
# DATA STORAGE INFORMATION
# ============================================================================
# When USE_MYSQL = True:
#   - Restaurants data is stored in: MySQL database 'food_finder', table 'restaurants'
#   - Data persists in MySQL server until you delete records
#   - Access via: app routes like /api/restaurants, /results, /explore
#
# When USE_MYSQL = False:
#   - Restaurants data is loaded from: dataset.csv or zomato.csv (in same folder as app.py)
#   - Data is read into memory each time app starts
#   - Changes made by app do NOT persist to CSV (data is read-only)
# ============================================================================

"""
WHERE YOUR DATA IS STORED - Food Finder App
=============================================

This file explains where restaurant data is stored and how to access it.
"""

# ============================================================================
# OPTION 1: USING CSV FILES (Default)
# ============================================================================
"""
Location: In the same folder as app.py
Files:
  - dataset.csv
  - zomato.csv

How it works:
  1. When app.py starts, it reads dataset.csv or zomato.csv into memory
  2. Data is kept in a pandas DataFrame called 'raw_data'
  3. When you search/filter restaurants, it filters this DataFrame
  4. Changes do NOT get saved back to the CSV file (read-only)

Access data:
  - Web: http://localhost:5000/explore  (filter restaurants)
  - Web: http://localhost:5000/api/restaurants  (JSON API)
  
To modify CSV data:
  1. Edit the .csv file directly with Excel, notepad, or a Python script
  2. Restart app.py to reload the updated data
"""

# ============================================================================
# OPTION 2: USING MYSQL DATABASE (Recommended for production)
# ============================================================================
"""
Steps to set up and use MySQL:

STEP 1: Create MySQL database
───────────────────────────────
1. Install MySQL Server (https://dev.mysql.com/downloads/mysql/)
   
2. Open MySQL Command Line Client (or any MySQL tool like MySQL Workbench)
   
3. Run the following to create database and table:
   
   mysql> CREATE DATABASE IF NOT EXISTS food_finder CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   mysql> USE food_finder;
   mysql> CREATE TABLE IF NOT EXISTS restaurants (
     id INT AUTO_INCREMENT PRIMARY KEY,
     name VARCHAR(255),
     rating FLOAT,
     city VARCHAR(100),
     cost FLOAT,
     cuisine VARCHAR(255),
     address TEXT,
     link VARCHAR(255)
   ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


STEP 2: Configure credentials in config.py
───────────────────────────────────────────
Edit: config.py

Change these values:
  USE_MYSQL = True                    # Enable MySQL
  MYSQL_HOST = 'localhost'            # Your MySQL server (localhost, 127.0.0.1, or IP)
  MYSQL_PORT = 3306                   # MySQL port (default: 3306)
  MYSQL_USER = 'root'                 # Your MySQL username
  MYSQL_PASSWORD = 'your_password'    # ⚠️ YOUR MYSQL PASSWORD HERE ⚠️
  MYSQL_DB = 'food_finder'            # Database name


STEP 3: Import data (dataset.csv → MySQL)
──────────────────────────────────────────
Create a file called 'import_data.py' in the project folder with:

    import pandas as pd
    from sqlalchemy import create_engine
    
    # Configure connection
    host = 'localhost'
    user = 'root'
    password = 'your_mysql_password'  # Change this!
    database = 'food_finder'
    
    # Create connection string
    connection_string = f"mysql+pymysql://{user}:{password}@{host}/{database}?charset=utf8mb4"
    engine = create_engine(connection_string)
    
    # Read CSV
    df = pd.read_csv('dataset.csv')  # or 'zomato.csv'
    
    # Write to MySQL
    df.to_sql('restaurants', con=engine, if_exists='replace', index=False)
    print(f"✅ Imported {len(df)} restaurants into MySQL!")

Run it (PowerShell):
    python import_data.py


STEP 4: Verify data in MySQL
────────────────────────────
Open MySQL command line and run:
    mysql> USE food_finder;
    mysql> SELECT COUNT(*) FROM restaurants;
    mysql> SELECT * FROM restaurants LIMIT 5;


STEP 5: Test the app with MySQL
────────────────────────────────
Restart app.py:
    python app.py

Visit: http://localhost:5000/explore

If it works, data is now being read from MySQL! ✅


Data storage location in MySQL:
  Database: 'food_finder'
  Table: 'restaurants'
  Columns: id, name, rating, city, cost, cuisine, address, link


WHERE TO FIND MYSQL DATA ON YOUR COMPUTER:
────────────────────────────────────────────
Default MySQL data directory (Windows):
  C:\ProgramData\MySQL\MySQL Server 8.0\data\food_finder\

View data using MySQL clients:
  - MySQL Command Line Client: mysql -u root -p
  - MySQL Workbench: Visual GUI tool (download free)
  - DBeaver: Another visual tool (free)
  - PhpMyAdmin: Web-based (if you have Apache/PHP)

"""

# ============================================================================
# QUICK COMPARISON TABLE
# ============================================================================
"""
┌─────────────────────┬──────────────────┬──────────────────┐
│ Feature             │ CSV Files        │ MySQL Database   │
├─────────────────────┼──────────────────┼──────────────────┤
│ Setup complexity    │ ⭐ Easy          │ ⭐⭐ Medium       │
│ Data persistence    │ ❌ Read-only     │ ✅ Persistent    │
│ Search speed        │ ⭐⭐ Slow         │ ⭐⭐⭐ Fast      │
│ Scale (# records)   │ ~10K OK          │ Millions OK      │
│ Remote access       │ ❌ No            │ ✅ Yes           │
│ Backup/restore      │ Manual copy      │ SQL dumps        │
│ Best for            │ Development      │ Production       │
└─────────────────────┴──────────────────┴──────────────────┘
"""

# ============================================================================
# TROUBLESHOOTING
# ============================================================================
"""
ERROR: "Can't connect to MySQL server"
  Fix: 
    1. Make sure MySQL is running (Windows: Services → search "MySQL")
    2. Check MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD in config.py
    3. Test with: mysql -u root -p

ERROR: "Access denied for user 'root'@'localhost'"
  Fix:
    1. Your password in config.py is wrong
    2. Reset MySQL password or update config.py with correct password

ERROR: "Database 'food_finder' doesn't exist"
  Fix:
    1. Run the CREATE DATABASE command from STEP 1 above
    2. Or run schema.sql: mysql -u root -p < schema.sql

ERROR: "Table 'food_finder.restaurants' doesn't exist"
  Fix:
    1. Run the CREATE TABLE command from STEP 1 above
    2. Or run import_data.py to create and populate table

DATA NOT SHOWING UP?
  Check:
    1. Is USE_MYSQL = True in config.py?
    2. Did you run import_data.py to load CSV into MySQL?
    3. Check database has records: SELECT COUNT(*) FROM restaurants;
"""

# ============================================================================
# SECURITY NOTES
# ============================================================================
"""
⚠️ IMPORTANT: PROTECT YOUR config.py FILE

Your config.py contains:
  - MySQL password
  - Email password
  - Secret keys

NEVER share this file or commit it to GitHub!

To protect it:
  1. Add to .gitignore:
     config.py
     
  2. In production, use environment variables:
     import os
     MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'default_password')
     
  3. On your server/hosting, set environment variables instead of storing in file
"""

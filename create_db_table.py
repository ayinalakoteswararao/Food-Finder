"""
Create MySQL database and restaurants table
"""
import config
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

# Connect without specifying database first
encoded_password = quote_plus(config.MYSQL_PASSWORD)
connection_string = f"mysql+pymysql://{config.MYSQL_USER}:{encoded_password}@{config.MYSQL_HOST}:{config.MYSQL_PORT}/?charset=utf8mb4"

engine = create_engine(connection_string)

with engine.connect() as conn:
    # Create database
    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {config.MYSQL_DB} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
    
    # Create table
    conn.execute(text(f"USE {config.MYSQL_DB}"))
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS restaurants (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            rating FLOAT,
            city VARCHAR(100),
            cost FLOAT,
            cuisine VARCHAR(255),
            address TEXT,
            link VARCHAR(255)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """))
    conn.commit()
    print("✅ Database 'food_finder' and table 'restaurants' created!")

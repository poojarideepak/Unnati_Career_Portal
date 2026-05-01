"""
init_db.py — Run this first to create the database in XAMPP automatically.
Usage: python init_db.py
"""
import pymysql
from config import settings
from database import engine, Base
import models  # Import models to ensure they are registered with Base

def initialize():
    print("[INFO] Initializing Unnati Career Portal Database...")

    # 1. Connect to MySQL server (without selecting a DB)
    try:
        connection = pymysql.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD
        )
        with connection.cursor() as cursor:
            # 2. Create Database if it doesn't exist
            print(f"  [DB] Creating database '{settings.DB_NAME}' if it doesn't exist...")
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {settings.DB_NAME}")
        connection.commit()
        connection.close()
        print(f"  [OK] Database '{settings.DB_NAME}' is ready.")

    except Exception as e:
        print(f"  [ERROR] Error connecting to MySQL: {e}")
        print("     Make sure XAMPP (MySQL) is running!")
        return

    # 3. Create Tables using SQLAlchemy
    try:
        print("  [DB] Dropping old tables (if any)...")
        Base.metadata.drop_all(bind=engine)
        print("  [DB] Creating new tables...")
        Base.metadata.create_all(bind=engine)
        print("  [OK] All tables created successfully.")
    except Exception as e:
        print(f"  ❌ Error creating tables: {e}")
        return

    print("\n[SUCCESS] Setup complete! You can now run 'python seed.py' to add sample data, or 'python main.py' to start the app.")

if __name__ == "__main__":
    initialize()

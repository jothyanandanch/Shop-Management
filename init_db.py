# init_db.py
from db_config import get_db_connection
from psycopg2 import Error

def create_tables():
    """
    Connects to the database and creates the necessary tables if they don't exist.
    """
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        if conn is None:
            print("Failed to Establish Connection to Database.")
            return
        
        cursor = conn.cursor()
        
        # Fixed SQL commands for PostgreSQL
        commands = (
            """
            CREATE TABLE IF NOT EXISTS users (
                id BIGSERIAL NOT NULL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS cards (
                id BIGSERIAL PRIMARY KEY,
                card_type TEXT UNIQUE NOT NULL,
                quantity INTEGER NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                allocated INTEGER DEFAULT 0
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS orders (
                id BIGSERIAL PRIMARY KEY,
                customer_name TEXT NOT NULL,
                customer_id INTEGER NOT NULL,
                order_date DATE NOT NULL,
                delivery_status TEXT CHECK(delivery_status IN ('Pending', 'Delivered')),
                advance_paid DECIMAL(10,2) DEFAULT 0,
                total_amount DECIMAL(10,2) DEFAULT 0
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS order_cards (
                id BIGSERIAL PRIMARY KEY,
                order_id INTEGER REFERENCES orders(id),
                card_id INTEGER REFERENCES cards(id),
                quantity INTEGER NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id BIGSERIAL PRIMARY KEY,
                order_id INTEGER NOT NULL,
                transaction_date DATE NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES orders(id)
            )
            """
        )
        
        for command in commands:
            print(f"Executing: {command.strip().splitlines()[1].strip()}...")
            cursor.execute(command)
        
        conn.commit()
        print("All tables created or already exist successfully!")
        
    except Error as e:
        print(f"Error creating tables: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print("Database connection closed.")

if __name__ == "__main__":
    print("Starting database schema initialization...")
    create_tables()

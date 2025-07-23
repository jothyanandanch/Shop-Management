# models.py
from db_config import get_db_connection
from psycopg2 import Error
from decimal import Decimal

# ------------------- USER FUNCTIONS -------------------

def create_user(username, plain_text_password, role):
    """Creates a new user in the database with hashed password."""
    conn, cursor = None, None
    try:
        conn = get_db_connection()
        if conn is None:
            return False

        cursor = conn.cursor()

        # --- safety guard: reject if password looks like it is already hashed
        if plain_text_password.startswith("scrypt:") or len(plain_text_password) == 97:
            raise ValueError("Password appears to be already hashed, refusing to store")

        from auth import hash_password
        password_hash = hash_password(plain_text_password)

        cursor.execute(
            "INSERT INTO users(username, password_hash, role) VALUES(%s, %s, %s)",
            (username, password_hash, role)
        )
        conn.commit()
        return True

    except Exception as e:
        print("create_user error:", e)
        if conn: conn.rollback()
        return False
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


def get_user_by_username(username):
    """Fetches user details by username."""
    conn, cursor = None, None
    try:
        conn = get_db_connection()
        if conn is None:
            return None

        cursor = conn.cursor()
        command = """SELECT id, username, password_hash, role FROM users WHERE username = %s"""
        cursor.execute(command, (username,))
        return cursor.fetchone()

    except Error as e:
        print(f"Error fetching user '{username}': {e}")
        return None
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

# ------------------- CARD FUNCTIONS -------------------

def add_card(card_type, quantity, price):
    """Adds a new card to the inventory."""
    conn, cursor = None, None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        command = """INSERT INTO cards(card_type, quantity, price) VALUES(%s, %s, %s)"""
        cursor.execute(command, (card_type, quantity, Decimal(str(price))))
        conn.commit()
        print(f"Card '{card_type}' added.")
        return True

    except Error as e:
        print(f"Error adding card '{card_type}': {e}")
        if conn: conn.rollback()
        return False
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


def get_all_cards():
    """Returns all card records."""
    conn, cursor = None, None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        command = """SELECT id, card_type, quantity, price, allocated FROM cards"""
        cursor.execute(command)
        return cursor.fetchall()

    except Error as e:
        print(f"Error fetching cards: {e}")
        return []
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

# ------------------- ORDER FUNCTIONS -------------------

def create_order(customer_name, customer_id, order_date, delivery_status, advance_paid, total_amount):
    """Creates a new customer order."""
    conn, cursor = None, None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        command = """
        INSERT INTO orders(customer_name, customer_id, order_date, delivery_status, advance_paid, total_amount)
        VALUES(%s, %s, %s, %s, %s, %s) RETURNING id
        """
        cursor.execute(command, (
            customer_name,
            customer_id,
            order_date,
            delivery_status,
            Decimal(str(advance_paid)),
            Decimal(str(total_amount))
        ))
        order_id = cursor.fetchone()[0]
        conn.commit()
        return order_id

    except Error as e:
        print(f"Error creating order: {e}")
        if conn: conn.rollback()
        return None
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


def link_card_to_order(order_id, card_id, quantity):
    """Links a card and quantity to a specific order."""
    conn, cursor = None, None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        command = """INSERT INTO order_cards(order_id, card_id, quantity) VALUES(%s, %s, %s)"""
        cursor.execute(command, (order_id, card_id, quantity))
        conn.commit()
        return True

    except Error as e:
        print(f"Error linking card to order: {e}")
        if conn: conn.rollback()
        return False
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


def get_all_orders():
    """Fetches all orders from the database."""
    conn, cursor = None, None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        command = """SELECT * FROM orders"""
        cursor.execute(command)
        return cursor.fetchall()
    except Error as e:
        print(f"Error fetching orders: {e}")
        return []
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


def generate_customer_id():
    """Generate sequential customer ID in format ddmmXXX"""
    from datetime import datetime
    
    conn, cursor = None, None
    try:
        now = datetime.now()
        day = f"{now.day:02d}"      # 18
        month = f"{now.month:02d}"  # 07
        prefix = day + month        # 1807
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all customer IDs that start with today's date prefix
        cursor.execute("""
            SELECT customer_id FROM orders 
            WHERE CAST(customer_id AS TEXT) LIKE ?
            ORDER BY customer_id DESC 
            LIMIT 1
        """, (f"{prefix}%",))
        
        result = cursor.fetchone()
        
        if result:
            last_id = str(result[0])
            # Check if it's the right format and extract serial
            if len(last_id) == 7 and last_id.startswith(prefix):
                last_serial = int(last_id[4:])  # Get last 3 digits
                new_serial = last_serial + 1
            else:
                new_serial = 1
        else:
            new_serial = 1
        
        # Create new ID: ddmmXXX
        new_id = f"{prefix}{new_serial:03d}"
        return int(new_id)
        
    except Exception as e:
        print(f"Error generating customer ID: {e}")
        # Return today's first ID as fallback
        now = datetime.now()
        fallback_id = f"{now.day:02d}{now.month:02d}001"
        return int(fallback_id)
    finally:
        if cursor: cursor.close()
        if conn: conn.close()



# ------------------- BILLING FUNCTIONS -------------------

def record_transaction(order_id, transaction_date, amount, note):
    """Logs a payment for a specific order."""
    conn, cursor = None, None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        command = """INSERT INTO transactions(order_id, transaction_date, amount, note) VALUES(%s, %s, %s, %s)"""
        cursor.execute(command, (order_id, transaction_date, Decimal(str(amount)), note))
        conn.commit()
        return True

    except Error as e:
        print(f"Error recording transaction: {e}")
        if conn: conn.rollback()
        return False
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def get_pending_bills(threshold=50.00):
    """Fetches orders with unpaid amounts above a threshold."""
    conn, cursor = None, None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        command = """
        SELECT o.id, o.customer_name, o.total_amount, 
               COALESCE(SUM(t.amount), 0) AS paid,
               (o.total_amount - COALESCE(SUM(t.amount), 0)) AS pending
        FROM orders o
        LEFT JOIN transactions t ON o.id = t.order_id
        GROUP BY o.id
        HAVING (o.total_amount - COALESCE(SUM(t.amount), 0)) > %s
        """
        cursor.execute(command, (Decimal(str(threshold)),))
        return cursor.fetchall()

    except Error as e:
        print(f"Error fetching pending bills: {e}")
        return []
    finally:
        if cursor: cursor.close()
        if conn: conn.close()



def get_card_by_id(card_id):
    """Fetch card details by ID."""
    conn, cursor = None, None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, card_type, quantity, price FROM cards WHERE id = %s", (card_id,))
        return cursor.fetchone()
    except:
        return None
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def update_card(card_id, quantity, price):
    """Updates quantity and price for a given card."""
    conn, cursor = None, None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE cards SET quantity = %s, price = %s WHERE id = %s", (quantity, Decimal(str(price)), card_id))
        conn.commit()
        return True
    except:
        if conn: conn.rollback()
        return False
    finally:
        if cursor: cursor.close()
        if conn: conn.close()




def get_pending_orders():
    """Fetches orders with pending delivery status."""
    conn, cursor = None, None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        command = """
        SELECT id, customer_name, customer_id, order_date, total_amount, delivery_status
        FROM orders 
        WHERE delivery_status = 'Pending'
        ORDER BY order_date DESC
        """
        cursor.execute(command)
        return cursor.fetchall()
    except Error as e:
        print(f"Error fetching pending orders: {e}")
        return []
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

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
        if plain_text_password.startswith("scrypt:") or len(plain_text_password) >= 25:
            raise ValueError("Password appears to be refusing to store")

        from auth import hash_password
        password_hash = hash_password(plain_text_password)

        cursor.execute(
            "INSERT INTO users(username, password, role) VALUES(%s, %s, %s)",
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
        command = """SELECT id, username, password, role FROM users WHERE username = %s"""
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
    """Get all cards with allocated quantities"""
    conn, cursor = None, None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT c.id, c.card_type, c.quantity, c.price, 
                   COALESCE(c.allocated, 0) as allocated
            FROM cards c
            ORDER BY c.card_type
        """)
        
        cards = cursor.fetchall()
        print(f"Debug: get_all_cards returned: {cards}")  #debug
        return cards
        
    except Exception as e:
        print(f"Error fetching cards: {e}")
        return []
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


def delete_card_by_id(card_id):
    conn,cursor=None,None
    try:
        conn=get_db_connection()
        cursor=conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM order_cards WHERE card_id =%s

        """,(card_id,))
        order_count=cursor.fetchone()[0]
        if order_count>0:
            print(f"Warning: Card {card_id} has {order_count} order allocations")
        # Delete from order_cards first (foreign key constraint)
        cursor.execute("DELETE FROM order_cards WHERE card_id = %s", (card_id,))
        
        # Delete the card
        cursor.execute("DELETE FROM cards WHERE id = %s", (card_id,))
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"Error deleting card: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

# ------------------- ORDER FUNCTIONS -------------------

def create_order(customer_name, order_id, order_date, delivery_status, advance_paid, total_amount,payment_status,customer_phone):
    """Creates a new customer order."""
    conn, cursor = None, None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        command = """
        INSERT INTO orders(customer_name, order_id, order_date, delivery_status, advance_paid, total_amount,payment_status,customer_phone)
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s) RETURNING order_id
        """
        cursor.execute(command, (
            customer_name,
            order_id,
            order_date,
            delivery_status,
            Decimal(str(advance_paid)),
            Decimal(str(total_amount)),
            payment_status,
            customer_phone
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

        cards_command="""UPDATE cards SET allocated=COALESCE(allocated,0)+%s WHERE id=%s
        """
        cursor.execute(cards_command,(quantity,card_id))
        conn.commit()
        return True

    except Error as e:
        print(f"Error linking card to order: {e}")
        if conn: conn.rollback()
        return False
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def get_order_details(order_id):
    """Get order details by ID"""
    conn, cursor = None, None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, customer_name, order_id, order_date, total_amount, 
                   advance_paid, delivery_status, payment_status,customer_phone 
            FROM orders WHERE id = %s
        """, (order_id,))
        return cursor.fetchone()
    except Exception as e:
        print(f"Error fetching order details: {e}")
        return None
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def get_all_orders():
    """Get all orders with customer and payment information"""
    conn, cursor = None, None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, customer_name, order_id, order_date, total_amount, 
                   advance_paid, delivery_status, payment_status,customer_phone
            FROM orders 
            ORDER BY order_date DESC, id DESC
        """)
        
        return cursor.fetchall()
        
    except Exception as e:
        print(f"Error fetching orders: {e}")
        return []
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


def delete_order_by_id(order_id):
    """Delete an order and all its related data"""
    conn, cursor = None, None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print(f"Debug: Attempting to delete order {order_id}")  # Add debug
        
        # Check if order has card allocations
        cursor.execute("""
            SELECT COUNT(*) FROM order_cards WHERE order_id = %s
        """, (order_id,))
        
        card_allocations = cursor.fetchone()[0]
        print(f"Debug: Found {card_allocations} card allocations")  # Add debug
        
        if card_allocations > 0:
            # First, restore allocated quantities back to available
            cursor.execute("""
                UPDATE cards 
                SET allocated = COALESCE(allocated, 0) - oc.quantity
                FROM order_cards oc 
                WHERE cards.id = oc.card_id AND oc.order_id = %s
            """, (order_id,))
            print(f"Debug: Restored {cursor.rowcount} card allocations")
        
        # Check if order has payment transactions
        cursor.execute("""
            SELECT COUNT(*) FROM transactions WHERE order_id = %s
        """, (order_id,))
        
        transaction_count = cursor.fetchone()[0]
        print(f"Debug: Found {transaction_count} payment transactions")
        
        # Delete in correct order to handle foreign key constraints
        # 1. Delete payment transactions first
        cursor.execute("DELETE FROM transactions WHERE order_id = %s", (order_id,))
        print(f"Debug: Deleted {cursor.rowcount} transaction records")
        
        # 2. Delete order-card allocations
        cursor.execute("DELETE FROM order_cards WHERE order_id = %s", (order_id,))
        print(f"Debug: Deleted {cursor.rowcount} order_cards records")
        
        # 3. Delete the main order
        cursor.execute("DELETE FROM orders WHERE id = %s", (order_id,))
        print(f"Debug: Deleted {cursor.rowcount} order records")
        
        conn.commit()
        print("Debug: Order deletion transaction committed successfully")
        return True
        
    except Exception as e:
        print(f"Error deleting order: {e}")
        print(f"Error type: {type(e).__name__}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cursor: cursor.close()
        if conn: conn.close()



def generate_order_id():
    """Generate sequential customer ID in format mmyyyyxxx"""
    from datetime import datetime,timezone
    
    conn, cursor = None, None
    try:
        now = datetime.now(timezone.utc)
        month = f"{now.month:02d}"
        year = str(now.year)
        prefix = month + year
        
        # Create range boundaries for this month/year
        min_id = int(f"{prefix}000")  # 072025000
        max_id = int(f"{prefix}999")  # 072025999
        
        print(f"Debug: Month={month}, Year={year}, Prefix={prefix}")
        print(f"Debug: Searching between {min_id} and {max_id}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Use numeric range instead of LIKE
        cursor.execute("""
            SELECT order_id FROM orders 
            WHERE order_id >= %s AND order_id <= %s
            ORDER BY order_id DESC 
            LIMIT 1
        """, (min_id, max_id))
        
        result = cursor.fetchone()
        print(f"Debug: Last ID result = {result}")
        
        if result:
            last_id = result[0]
            # Extract the serial number (last 3 digits)
            last_serial = last_id % 1000  # Gets last 3 digits
            new_serial = last_serial + 1
            print(f"Debug: Last serial = {last_serial}, New serial = {new_serial}")
        else:
            new_serial = 1
            print(f"Debug: No existing records, starting with serial = 1")
        
        new_id = int(f"{prefix}{new_serial:03d}")
        print(f"Debug: Generated ID = {new_id}")
        return new_id
        
    except Exception as e:
        print(f"Error generating customer ID: {e}")
        now = datetime.now()
        fallback_id = int(f"{now.month:02d}{now.year}001")
        return fallback_id
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

def get_total_payments(order_id):
    """Get total additional payments made for an order"""
    conn, cursor = None, None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) as total_payments 
            FROM transactions WHERE order_id = %s
        """, (order_id,))
        result = cursor.fetchone()
        return float(result[0]) if result else 0.0
    except Exception as e:
        print(f"Error fetching total payments: {e}")
        return 0.0
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


def update_order_delivery_status(order_id, status):
    """Update order delivery status"""
    conn, cursor = None, None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE orders SET delivery_status = %s WHERE id = %s
        """, (status, order_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating delivery status: {e}")
        return False
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


def update_payment_status(order_id, status):
    """Update order payment status"""
    conn, cursor = None, None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE orders SET payment_status = %s WHERE id = %s
        """, (status, order_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating payment status: {e}")
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
        SELECT id, customer_name, order_id, order_date, total_amount, delivery_status,payment_status
        FROM orders 
        WHERE delivery_status = 'Pending' OR payment_status ='Pending'
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

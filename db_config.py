import psycopg2
from psycopg2 import Error

def get_db_connection():
    try:
        conn=psycopg2.connect(
            dbname='your-db',
            user='postgres',
            password='your-password',
            host='localhost',
            port='5432'
        )
        return conn
    except Error as e:
        print(f"Error Connecting to PostgreSQL databse: {e}")

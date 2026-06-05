import sqlite3
import os 
#db config
DB_NAME = "teddyshine.db"

def get_connection():# for connection funx
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row#enable column access by name
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def close_connection(conn):# for closing connection funx
    if conn:
        try:
            conn.close()
        except sqlite3.Error as e:
            print(f"Error closing database connection: {e}")

def close_connections(conn):# for closing connection funx
    if conn:
        try:
            conn.close()
        except sqlite3.Error as e:
            print(f"Error closing database connection: {e}")

def get_cursor(conn):# for getting cursor funx
    if conn:
        return conn.cursor()
    return None


def is_connected(conn):# for checking connection funx
    return conn is not None


def get_db_info():# for getting database info funx
    return{
        "database_name": DB_NAME,
        "database_path": os.path.abspath(DB_NAME),
        "exists": os.path.exists(DB_NAME)
    }   


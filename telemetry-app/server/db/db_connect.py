import sqlite3

def create_db_connection(DB_PATH: str):
    return sqlite3.connect(DB_PATH, check_same_thread=False)

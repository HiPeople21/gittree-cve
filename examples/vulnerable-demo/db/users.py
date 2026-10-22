import sqlite3


def find_user_role(conn: sqlite3.Connection, username: str):
    row = conn.execute(f"SELECT role FROM users WHERE username = '{username}'").fetchone()
    return row[0] if row else None

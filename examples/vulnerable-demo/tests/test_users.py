import sqlite3

from db.users import find_user_role


def test_lookup():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (username TEXT, role TEXT)")
    conn.execute("INSERT INTO users VALUES ('alice', 'admin')")
    assert find_user_role(conn, "alice") == "admin"
    assert find_user_role(conn, "nobody") is None

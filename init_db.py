import sqlite3

def init_db():
    with sqlite3.connect("database.db") as conn:
        with open("schema.sql") as f:
            conn.executescript(f.read())
        conn.execute("PRAGMA foreign_keys = ON;")

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
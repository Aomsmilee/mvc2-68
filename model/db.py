import os
import sqlite3
from contextlib import contextmanager

def ensure_db_dir(db_path: str) -> None:
    d = os.path.dirname(db_path)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)

@contextmanager
def get_conn(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

from model.db import get_conn

def list_reporters(db_path: str):
    with get_conn(db_path) as conn:
        return conn.execute(
            "SELECT user_id, name FROM users WHERE role='user' ORDER BY name"
        ).fetchall()

def list_checkers(db_path: str):
    with get_conn(db_path) as conn:
        return conn.execute(
            "SELECT user_id, name FROM users WHERE role='checker' ORDER BY name"
        ).fetchall()

def get_user(db_path: str, user_id: int):
    with get_conn(db_path) as conn:
        return conn.execute(
            "SELECT user_id, name, role FROM users WHERE user_id=?",
            (user_id,)
        ).fetchone()

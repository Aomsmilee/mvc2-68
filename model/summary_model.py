from model.db import get_conn

def get_summary(db_path: str):
    with get_conn(db_path) as conn:
        panic = conn.execute("""
            SELECT r.*, COUNT(p.report_id) AS report_count
            FROM rumours r
            LEFT JOIN reports p ON p.rumour_code = r.rumour_code
            WHERE r.status='panic'
            GROUP BY r.rumour_code
            ORDER BY report_count DESC, r.created_at DESC
        """).fetchall()

        vtrue = conn.execute("""
            SELECT r.*, COUNT(p.report_id) AS report_count
            FROM rumours r
            LEFT JOIN reports p ON p.rumour_code = r.rumour_code
            WHERE r.verified_status='true'
            GROUP BY r.rumour_code
            ORDER BY r.created_at DESC
        """).fetchall()

        vfalse = conn.execute("""
            SELECT r.*, COUNT(p.report_id) AS report_count
            FROM rumours r
            LEFT JOIN reports p ON p.rumour_code = r.rumour_code
            WHERE r.verified_status='false'
            GROUP BY r.rumour_code
            ORDER BY r.created_at DESC
        """).fetchall()

        return panic, vtrue, vfalse

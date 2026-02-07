from datetime import datetime
from model.db import get_conn

def list_reports_for_rumour(db_path: str, code: str):
    with get_conn(db_path) as conn:
        return conn.execute("""
            SELECT p.report_id, p.reported_at, p.report_type,
                   u.user_id AS reporter_id, u.name AS reporter_name
            FROM reports p
            JOIN users u ON u.user_id = p.reporter_id
            WHERE p.rumour_code=?
            ORDER BY p.reported_at DESC
        """, (code,)).fetchall()

def add_report(db_path: str, reporter_id: int, rumour_code: str, report_type: str):
    if report_type not in ("distortion","incitement","false_info"):
        raise ValueError("report_type ไม่ถูกต้อง")

    with get_conn(db_path) as conn:
        row = conn.execute(
            "SELECT verified_status FROM rumours WHERE rumour_code=?",
            (rumour_code,)
        ).fetchone()
        if row is None:
            raise ValueError("ไม่พบข่าวลือ")
        if row["verified_status"] is not None:
            raise ValueError("ข่าวนี้ถูกตรวจสอบแล้ว ห้ามรายงานเพิ่ม")

        conn.execute("""
            INSERT INTO reports(reporter_id, rumour_code, reported_at, report_type)
            VALUES (?,?,?,?)
        """, (reporter_id, rumour_code, datetime.now().isoformat(timespec="seconds"), report_type))

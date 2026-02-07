import re
from datetime import datetime
from model.db import get_conn

CODE_RE = re.compile(r"^[1-9][0-9]{7}$")  # 8 digits, first not 0

def list_rumours_sorted(db_path: str):
    # view#1 ต้องเรียงตามจำนวนรายงาน/ความร้อนแรง
    with get_conn(db_path) as conn:
        return conn.execute("""
            SELECT r.*,
                   COUNT(p.report_id) AS report_count
            FROM rumours r
            LEFT JOIN reports p ON p.rumour_code = r.rumour_code
            GROUP BY r.rumour_code
            ORDER BY report_count DESC, r.created_at DESC
        """).fetchall()

def get_rumour_with_count(db_path: str, code: str):
    with get_conn(db_path) as conn:
        return conn.execute("""
            SELECT r.*,
                   COUNT(p.report_id) AS report_count
            FROM rumours r
            LEFT JOIN reports p ON p.rumour_code = r.rumour_code
            WHERE r.rumour_code = ?
            GROUP BY r.rumour_code
        """, (code,)).fetchone()

def create_rumour(db_path: str, code: str, title: str, source: str, credibility: float):
    if not CODE_RE.match(code or ""):
        raise ValueError("Rumour code ต้องเป็นเลข 8 หลัก และตัวแรกห้ามเป็น 0")
    if not title.strip():
        raise ValueError("ต้องมีหัวข้อข่าว")
    if not source.strip():
        raise ValueError("ต้องมีแหล่งที่มา")
    if credibility < 0 or credibility > 100:
        raise ValueError("credibility ต้องอยู่ระหว่าง 0-100")

    created = datetime.now().isoformat(timespec="seconds")
    with get_conn(db_path) as conn:
        conn.execute("""
            INSERT INTO rumours(rumour_code,title,source,created_at,credibility,status)
            VALUES (?,?,?,?,?,'normal')
        """, (code, title.strip(), source.strip(), created, float(credibility)))

def set_panic_if_needed(db_path: str, code: str, threshold: int) -> int:
    with get_conn(db_path) as conn:
        cnt = conn.execute(
            "SELECT COUNT(*) cnt FROM reports WHERE rumour_code=?",
            (code,)
        ).fetchone()["cnt"]
        if int(cnt) > threshold:
            conn.execute("UPDATE rumours SET status='panic' WHERE rumour_code=?", (code,))
        return int(cnt)

def verify_rumour(db_path: str, code: str, verified_status: str, checker_id: int):
    if verified_status not in ("true","false"):
        raise ValueError("verified_status ต้องเป็น true หรือ false")
    now = datetime.now().isoformat(timespec="seconds")

    with get_conn(db_path) as conn:
        row = conn.execute(
            "SELECT verified_status FROM rumours WHERE rumour_code=?",
            (code,)
        ).fetchone()
        if row is None:
            raise ValueError("ไม่พบข่าวลือ")

        # ✅ ล็อก: ถ้าเคย verify แล้ว ห้ามเปลี่ยน
        if row["verified_status"] is not None:
            raise ValueError("ข่าวนี้ถูกตรวจสอบแล้ว ไม่สามารถตรวจสอบซ้ำได้")

        conn.execute("""
            UPDATE rumours
            SET verified_status=?, verified_by=?, verified_at=?
            WHERE rumour_code=?
        """, (verified_status, checker_id, now, code))

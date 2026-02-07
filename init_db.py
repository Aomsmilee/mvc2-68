import sqlite3
from datetime import datetime, timedelta
from config import DB_PATH, PANIC_THRESHOLD
from model.db import ensure_db_dir

SCHEMA = """
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS reports;
DROP TABLE IF EXISTS rumours;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name    TEXT NOT NULL,
    role    TEXT NOT NULL CHECK(role IN ('user','checker'))
);

CREATE TABLE rumours (
    rumour_code     TEXT PRIMARY KEY,
    title           TEXT NOT NULL,
    source          TEXT NOT NULL,
    created_at      TEXT NOT NULL,
    credibility     REAL NOT NULL,
    status          TEXT NOT NULL CHECK(status IN ('normal','panic')) DEFAULT 'normal',

    -- เพิ่มเพื่อรองรับ "แสดงข่าวที่ถูกยืนยันจริง/เท็จ" + rule "verified แล้วห้าม report"
    verified_status TEXT CHECK(verified_status IN ('true','false')),
    verified_by     INTEGER,
    verified_at     TEXT,

    CHECK(length(rumour_code)=8),
    CHECK(substr(rumour_code,1,1) <> '0'),
    FOREIGN KEY(verified_by) REFERENCES users(user_id)
);

CREATE TABLE reports (
    report_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    reporter_id  INTEGER NOT NULL,
    rumour_code  TEXT NOT NULL,
    reported_at  TEXT NOT NULL,
    report_type  TEXT NOT NULL CHECK(report_type IN ('distortion','incitement','false_info')),
    FOREIGN KEY(reporter_id) REFERENCES users(user_id),
    FOREIGN KEY(rumour_code) REFERENCES rumours(rumour_code),

    -- rule: user 1 คน report ข่าวเดิมซ้ำไม่ได้
    UNIQUE(reporter_id, rumour_code)
);
"""

def main():
    ensure_db_dir(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.executescript(SCHEMA)

    # users >= 10 (เพิ่ม checker ด้วย)
    users = [
        ("Alice","user"), ("Bob","user"), ("Chai","user"), ("Donut","user"), ("Eve","user"),
        ("Fah","user"), ("Game","user"), ("Hana","user"), ("Ice","user"), ("Jame","user"),
        ("Krit","checker"), ("Lina","checker"),
    ]
    conn.executemany("INSERT INTO users(name,role) VALUES (?,?)", users)

    base = datetime.now() - timedelta(days=5)
    rumours = [
        ("12345678","น้ำดื่มปนเปื้อน","Facebook",(base+timedelta(hours=1)).isoformat(timespec="seconds"),62.5,"normal"),
        ("23456789","สะพานจะปิดถาวร","Line",(base+timedelta(hours=2)).isoformat(timespec="seconds"),45.0,"normal"),
        ("34567891","พบสารเคมีในอากาศ","X",(base+timedelta(hours=3)).isoformat(timespec="seconds"),55.0,"normal"),
        ("45678912","โรงพยาบาลขาดเลือด","News",(base+timedelta(hours=4)).isoformat(timespec="seconds"),70.0,"normal"),
        ("56789123","ไฟฟ้าจะดับทั้งเมือง","TikTok",(base+timedelta(hours=5)).isoformat(timespec="seconds"),40.0,"normal"),
        ("67891234","แจกเงินด่วนวันพรุ่งนี้","SMS",(base+timedelta(hours=6)).isoformat(timespec="seconds"),30.0,"normal"),
        ("78912345","มีการอพยพด่วน","Facebook",(base+timedelta(hours=7)).isoformat(timespec="seconds"),80.0,"normal"),
        ("89123456","พบโรคระบาดใหม่","Line",(base+timedelta(hours=8)).isoformat(timespec="seconds"),50.0,"normal"),
    ]
    conn.executemany(
        "INSERT INTO rumours(rumour_code,title,source,created_at,credibility,status) VALUES (?,?,?,?,?,?)",
        rumours
    )

    def now_iso():
        return datetime.now().isoformat(timespec="seconds")

    user_ids = [r[0] for r in conn.execute(
        "SELECT user_id FROM users WHERE role='user' ORDER BY user_id LIMIT 10"
    ).fetchall()]

    seed_reports = []
    # ทำให้ 2 ข่าวเป็น panic (จำนวนรายงาน > threshold)
    for i, uid in enumerate(user_ids[:4]):
        seed_reports.append((uid,"78912345",now_iso(),["distortion","incitement","false_info","distortion"][i]))
    for i, uid in enumerate(user_ids[4:8]):
        seed_reports.append((uid,"12345678",now_iso(),["false_info","false_info","incitement","distortion"][i]))
    # ข่าวไม่ panic
    for i, uid in enumerate(user_ids[:3]):
        seed_reports.append((uid,"23456789",now_iso(),["distortion","incitement","false_info"][i]))

    conn.executemany(
        "INSERT INTO reports(reporter_id,rumour_code,reported_at,report_type) VALUES (?,?,?,?)",
        seed_reports
    )

    # อัปเดต panic ตาม rule
    rows = conn.execute("""
        SELECT rumour_code, COUNT(*) cnt
        FROM reports
        GROUP BY rumour_code
    """).fetchall()
    for code, cnt in rows:
        if cnt > PANIC_THRESHOLD:
            conn.execute("UPDATE rumours SET status='panic' WHERE rumour_code=?", (code,))

    # ทำให้มี verified true/false เพื่อแสดงใน summary
    checker_id = conn.execute(
        "SELECT user_id FROM users WHERE role='checker' ORDER BY user_id LIMIT 1"
    ).fetchone()[0]

    conn.execute("UPDATE rumours SET verified_status='true', verified_by=?, verified_at=? WHERE rumour_code=?",
                 (checker_id, now_iso(), "45678912"))
    conn.execute("UPDATE rumours SET verified_status='false', verified_by=?, verified_at=? WHERE rumour_code=?",
                 (checker_id, now_iso(), "67891234"))

    conn.commit()
    conn.close()
    print(f"Initialized DB at: {DB_PATH} (PANIC_THRESHOLD={PANIC_THRESHOLD})")

if __name__ == "__main__":
    main()

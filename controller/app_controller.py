import sqlite3
from config import PANIC_THRESHOLD
from model.rumours_model import list_rumours_sorted, get_rumour_with_count, create_rumour, set_panic_if_needed, verify_rumour
from model.reports_model import list_reports_for_rumour, add_report
from model.users_model import list_reporters, list_checkers, get_user
from model.summary_model import get_summary
from view.summary_view import SummaryView


class AppController:
    def __init__(self, db_path: str):
        self.db_path = db_path

        # views (จะ bind ใน main.py)
        self.list_view = None
        self.detail_view = None
        self.summary_view = None

    def bind_views(self, list_view, detail_view, summary_view):
        self.list_view = list_view
        self.detail_view = detail_view
        self.summary_view = summary_view

    # -------- View#1 --------
    def load_rumours_for_list(self):
        return list_rumours_sorted(self.db_path)

    def on_open_detail(self, rumour_code: str):
        self.detail_view.show_window()
        self.detail_view.load_rumour(rumour_code)

    # -------- View#2 --------
    def load_detail_data(self, rumour_code: str):
        rumour = get_rumour_with_count(self.db_path, rumour_code)
        if rumour is None:
            return None, []
        reports = list_reports_for_rumour(self.db_path, rumour_code)
        return rumour, reports

    def load_people(self):
        return list_reporters(self.db_path), list_checkers(self.db_path)

    def submit_report(self, rumour_code: str, reporter_id: int, report_type: str):
        try:
            add_report(self.db_path, reporter_id, rumour_code, report_type)
            cnt = set_panic_if_needed(self.db_path, rumour_code, PANIC_THRESHOLD)
            return {"ok": True, "count": cnt, "panic": cnt > PANIC_THRESHOLD}
        except sqlite3.IntegrityError:
            return {"ok": False, "error": "DUPLICATE_REPORT"}
        except ValueError as e:
            return {"ok": False, "error": str(e)}

    def submit_verify(self, rumour_code: str, checker_id: int, verified_status: str):
        user = get_user(self.db_path, checker_id)
        if user is None or user["role"] != "checker":
            return {"ok": False, "error": "ONLY_CHECKER"}

        try:
            verify_rumour(self.db_path, rumour_code, verified_status, checker_id)
            return {"ok": True}
        except ValueError as e:
            return {"ok": False, "error": str(e)}

    def create_new_rumour(self, code: str, title: str, source: str, credibility: float):
        try:
            create_rumour(self.db_path, code, title, source, credibility)
            return {"ok": True}
        except sqlite3.IntegrityError:
            return {"ok": False, "error": "RUMOUR_EXISTS"}
        except ValueError as e:
            return {"ok": False, "error": str(e)}

    # -------- View#3 --------
    def load_summary(self):
        return get_summary(self.db_path)

    # -------- Refresh ทุกหน้าจอ --------
    def refresh_all_views(self):
        if self.list_view:
            self.list_view.refresh()
        if self.detail_view:
            self.detail_view.refresh_if_open()
        if self.summary_view:
            self.summary_view.refresh()

    
    def on_open_summary(self):
        from view.summary_view import SummaryView

        root = self.list_view.frame.winfo_toplevel()

        # ถ้ายังไม่เคยสร้าง หรือเคยปิดไปแล้ว -> สร้างใหม่
        if self.summary_view is None or (hasattr(self.summary_view, "is_open") and not self.summary_view.is_open()):
            def clear_ref():
                self.summary_view = None

            self.summary_view = SummaryView(root, self, on_close=clear_ref)
        else:
            # ถ้าเปิดอยู่แล้ว ดึงขึ้นหน้า
            try:
                self.summary_view.win.lift()
            except Exception:
                pass

        self.summary_view.refresh()



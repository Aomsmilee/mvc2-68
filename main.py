# ทำข้อที่ 1: Rumor Tracking System (MVC) - Python only + GUI Views

import tkinter as tk
from tkinter import ttk, messagebox

from config import DB_PATH
from model.db import ensure_db_dir
from controller.app_controller import AppController
from view.rumours_list_view import RumoursListView
from view.rumour_detail_view import RumourDetailView
from view.summary_view import SummaryView

def main():
    ensure_db_dir(DB_PATH)

    root = tk.Tk()
    root.title("Rumor Tracking System (Main)")
    root.geometry("1100x650")

    controller = AppController(db_path=DB_PATH)

    # View #1 เป็นหน้าหลักใน root
    list_view = RumoursListView(root, controller)

    # View #2 เป็นหน้าต่างแยก (เปิดเมื่อกด Open Detail)
    detail_view = RumourDetailView(root, controller)

    # View #3 เป็นหน้าต่างแยก (เปิดเลยตั้งแต่เริ่ม เพื่อให้มี 3 views แยกชัด)
    summary_view = None

    controller.bind_views(list_view, detail_view, summary_view)

    # initial load
    list_view.refresh()

    # hint บอกผู้ใช้
    messagebox.showinfo(
        "How to use",
        "View #1 หนารวมข่าวลือ\n"
        "กด Open Detail เพื่อเปิด View #2 หน้ารายละเอียดข่าวลือ\n"
        "กด Open Summary เพื่อเปิด View #3 หน้าสรุปผล"
    )

    root.mainloop()

if __name__ == "__main__":
    main()

import tkinter as tk
from tkinter import ttk, messagebox

class RumoursListView:
    def __init__(self, root: tk.Tk, controller):
        self.controller = controller
        self.frame = ttk.Frame(root)
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)

        top = ttk.Frame(self.frame)
        top.pack(fill="x")

        ttk.Label(top, text="View #1: หน้ารวมข่าวลือ (เรียงตามจำนวนรายงาน)", font=("Arial", 14, "bold")).pack(side="left")
        ttk.Button(top, text="Refresh", command=self.refresh).pack(side="right")
        ttk.Button(top, text="Open Detail", command=self.open_selected).pack(side="right", padx=6)
        ttk.Button(top, text="Open Summary", command=self.open_summary).pack(side="right", padx=6)

        cols = ("code","title","source","created","cred","reports","status","verified")
        self.tree = ttk.Treeview(self.frame, columns=cols, show="headings", height=20)
        for c, w in [
            ("code", 90), ("title", 260), ("source", 110), ("created", 170),
            ("cred", 90), ("reports", 80), ("status", 90), ("verified", 90)
        ]:
            self.tree.heading(c, text=c.upper())
            self.tree.column(c, width=w, anchor="w")
        self.tree.pack(fill="both", expand=True, pady=10)

        self.tree.bind("<Double-1>", lambda e: self.open_selected())

    def refresh(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        rows = self.controller.load_rumours_for_list()
        for r in rows:
            ver = r["verified_status"] if r["verified_status"] else "-"
            self.tree.insert("", "end", values=(
                r["rumour_code"], r["title"], r["source"], r["created_at"],
                f'{float(r["credibility"]):.1f}', int(r["report_count"]),
                r["status"], ver
            ))

    def open_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "เลือกข่าวก่อน")
            return
        code = self.tree.item(sel[0], "values")[0]
        self.controller.on_open_detail(code)

    def open_summary(self):
        self.controller.on_open_summary()


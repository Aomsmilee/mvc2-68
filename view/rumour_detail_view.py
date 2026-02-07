import tkinter as tk
from tkinter import ttk, messagebox
from config import PANIC_THRESHOLD

class RumourDetailView:
    def __init__(self, root: tk.Tk, controller):
        self.controller = controller
        self.root = root
        self.win = None
        self.current_code = None

        # Role simulation state
        self.role_mode = tk.StringVar(value="user")  # "user" or "checker"

        # Widgets groups (will be set in show_window)
        self.user_widgets = []
        self.checker_widgets = []

    def show_window(self):
        if self.win and self.win.winfo_exists():
            self.win.lift()
            return

        self.win = tk.Toplevel(self.root)
        self.win.title("View #2: รายละเอียดข่าวลือ")
        self.win.geometry("1000x600")

        wrap = ttk.Frame(self.win)
        wrap.pack(fill="both", expand=True, padx=10, pady=10)

        left = ttk.Frame(wrap)
        left.pack(side="left", fill="both", expand=True)

        right = ttk.Frame(wrap)
        right.pack(side="right", fill="y", padx=(10, 0))

        # ---------------- Role Simulation (TOP MOST) ----------------
        role_bar = ttk.Frame(left)
        role_bar.pack(fill="x", pady=(0, 8))

        ttk.Label(role_bar, text="Role Simulation:", font=("Arial", 11, "bold")).pack(side="left")
        ttk.Radiobutton(
            role_bar, text="โหมด User ทั่วไป",
            value="user", variable=self.role_mode,
            command=self._apply_role_mode
        ).pack(side="left", padx=10)

        ttk.Radiobutton(
            role_bar, text="โหมดผู้ตรวจสอบ (Inspector)",
            value="checker", variable=self.role_mode,
            command=self._apply_role_mode
        ).pack(side="left", padx=10)

        # ---------------- Top input ----------------
        top = ttk.Frame(left)
        top.pack(fill="x")
        ttk.Label(top, text="Rumour code:").pack(side="left")
        self.code_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.code_var, width=15).pack(side="left", padx=6)
        ttk.Button(top, text="Load", command=self._load_clicked).pack(side="left")

        self.detail_text = tk.Text(left, height=10, wrap="word")
        self.detail_text.pack(fill="x", pady=10)

        ttk.Label(left, text="Reports history").pack(anchor="w")
        cols = ("id","reporter","type","at")
        self.reports_tree = ttk.Treeview(left, columns=cols, show="headings", height=16)
        for c, w in [("id",60),("reporter",220),("type",120),("at",220)]:
            self.reports_tree.heading(c, text=c.upper())
            self.reports_tree.column(c, width=w, anchor="w")
        self.reports_tree.pack(fill="both", expand=True)

        # ---------------- Right side - report ----------------
        ttk.Label(right, text="Report (user)", font=("Arial", 11, "bold")).pack(anchor="w")

        self.reporter_map = {}
        self.reporter_var = tk.StringVar()
        self.reporter_combo = ttk.Combobox(right, textvariable=self.reporter_var, state="readonly", width=26)
        self.reporter_combo.pack(anchor="w", pady=(4, 10))

        ttk.Label(right, text="Report type").pack(anchor="w")
        self.type_var = tk.StringVar(value="distortion")
        self.type_combo = ttk.Combobox(
            right, textvariable=self.type_var, state="readonly", width=26,
            values=["distortion","incitement","false_info"]
        )
        self.type_combo.pack(anchor="w", pady=(4, 10))

        self.report_btn = ttk.Button(right, text="Submit Report", command=self._submit_report)
        self.report_btn.pack(anchor="w", pady=(0, 16))

        ttk.Separator(right).pack(fill="x", pady=10)

        # ---------------- Verify ----------------
        ttk.Label(right, text="Verify (checker)", font=("Arial", 11, "bold")).pack(anchor="w")

        self.checker_map = {}
        self.checker_var = tk.StringVar()
        self.checker_combo = ttk.Combobox(right, textvariable=self.checker_var, state="readonly", width=26)
        self.checker_combo.pack(anchor="w", pady=(4, 10))

        ttk.Label(right, text="Verify as").pack(anchor="w")
        self.verify_var = tk.StringVar(value="true")
        self.verify_combo = ttk.Combobox(
            right, textvariable=self.verify_var, state="readonly",
            width=26, values=["true","false"]
        )
        self.verify_combo.pack(anchor="w", pady=(4, 10))

        self.verify_btn = ttk.Button(right, text="Verify", command=self._submit_verify)
        self.verify_btn.pack(anchor="w")

        ttk.Separator(right).pack(fill="x", pady=10)

        # ---------------- Optional create ----------------
        ttk.Label(right, text="(Optional) Create rumour", font=("Arial", 11, "bold")).pack(anchor="w")
        self.new_code = tk.StringVar()
        self.new_title = tk.StringVar()
        self.new_source = tk.StringVar()
        self.new_cred = tk.StringVar(value="50")

        ttk.Label(right, text="code").pack(anchor="w")
        ttk.Entry(right, textvariable=self.new_code, width=30).pack(anchor="w", pady=(2, 6))
        ttk.Label(right, text="title").pack(anchor="w")
        ttk.Entry(right, textvariable=self.new_title, width=30).pack(anchor="w", pady=(2, 6))
        ttk.Label(right, text="source").pack(anchor="w")
        ttk.Entry(right, textvariable=self.new_source, width=30).pack(anchor="w", pady=(2, 6))
        ttk.Label(right, text="credibility").pack(anchor="w")
        ttk.Entry(right, textvariable=self.new_cred, width=30).pack(anchor="w", pady=(2, 6))
        ttk.Button(right, text="Create", command=self._create_rumour).pack(anchor="w")

        # Group widgets for enable/disable by role
        self.user_widgets = [self.reporter_combo, self.type_combo, self.report_btn]
        self.checker_widgets = [self.checker_combo, self.verify_combo, self.verify_btn]

        self._refresh_people()
        self._apply_role_mode()  # apply default mode at start

    # ---------------- Role mode logic ----------------
    def _set_widgets_state(self, widgets, enabled: bool):
        for w in widgets:
            try:
                if enabled:
                    w.state(["!disabled"])
                else:
                    w.state(["disabled"])
            except Exception:
                # fallback
                try:
                    w.configure(state=("normal" if enabled else "disabled"))
                except Exception:
                    pass

    def _apply_role_mode(self):
        mode = self.role_mode.get()

        if mode == "user":
            self._set_widgets_state(self.user_widgets, True)
            self._set_widgets_state(self.checker_widgets, False)
        else:
            self._set_widgets_state(self.user_widgets, False)
            self._set_widgets_state(self.checker_widgets, True)

        # แต่ต้องเคารพ rule: verified แล้ว report ห้ามใช้เสมอ
        self._enforce_verified_rule_if_loaded()

    def _enforce_verified_rule_if_loaded(self):
        # ถ้ามีข่าวที่โหลดอยู่ ให้ตรวจว่า verified ไหม แล้วปิด report เสมอถ้า verified แล้ว
        if not self.current_code:
            return
        rumour, _ = self.controller.load_detail_data(self.current_code)
        if rumour is None:
            return
        if rumour["verified_status"] is not None:
            self._set_widgets_state(self.user_widgets, False)

    # ---------------- Data refresh ----------------
    def _refresh_people(self):
        reporters, checkers = self.controller.load_people()
        self.reporter_map = {f'{u["name"]} (#{u["user_id"]})': u["user_id"] for u in reporters}
        self.checker_map = {f'{u["name"]} (#{u["user_id"]})': u["user_id"] for u in checkers}

        rnames = list(self.reporter_map.keys())
        cnames = list(self.checker_map.keys())
        self.reporter_combo["values"] = rnames
        self.checker_combo["values"] = cnames
        if rnames: self.reporter_combo.current(0)
        if cnames: self.checker_combo.current(0)

    def load_rumour(self, rumour_code: str):
        self.current_code = rumour_code
        self.code_var.set(rumour_code)
        self._render_detail()

    def _load_clicked(self):
        code = self.code_var.get().strip()
        if not code:
            messagebox.showinfo("Info", "ใส่รหัสข่าวก่อน")
            return
        self.load_rumour(code)

    def _render_detail(self):
        if not self.current_code:
            return
        rumour, reports = self.controller.load_detail_data(self.current_code)
        if rumour is None:
            messagebox.showerror("Error", "ไม่พบข่าวลือ")
            return

        ver = rumour["verified_status"] if rumour["verified_status"] else "Not verified"

        self.detail_text.delete("1.0", "end")
        self.detail_text.insert("end",
            f'Code: {rumour["rumour_code"]}\n'
            f'Title: {rumour["title"]}\n'
            f'Source: {rumour["source"]}\n'
            f'Created: {rumour["created_at"]}\n'
            f'Credibility: {float(rumour["credibility"]):.1f}\n'
            f'Reports: {int(rumour["report_count"])}  (panic if > {PANIC_THRESHOLD})\n'
            f'Status: {rumour["status"]}\n'
            f'Verified: {ver}\n'
        )

        for i in self.reports_tree.get_children():
            self.reports_tree.delete(i)
        for p in reports:
            self.reports_tree.insert("", "end", values=(
                p["report_id"], f'{p["reporter_name"]} (#{p["reporter_id"]})', p["report_type"], p["reported_at"]
            ))

        # หลังโหลดข่าว ให้ apply role อีกครั้ง (และ enforce verified rule)
        self._apply_role_mode()

    # ---------------- Actions ----------------
    def _submit_report(self):
        if not self.current_code:
            messagebox.showinfo("Info", "Load ข่าวก่อน")
            return
        rname = self.reporter_var.get()
        if rname not in self.reporter_map:
            messagebox.showerror("Error", "เลือก reporter")
            return
        reporter_id = self.reporter_map[rname]
        report_type = self.type_var.get().strip()

        res = self.controller.submit_report(self.current_code, reporter_id, report_type)
        if res["ok"]:
            if res["panic"]:
                messagebox.showwarning("PANIC", f"Reported. Total={res['count']} → PANIC")
            else:
                messagebox.showinfo("OK", f"Reported. Total={res['count']}")
            self.controller.refresh_all_views()
            self._render_detail()
        else:
            if res["error"] == "DUPLICATE_REPORT":
                messagebox.showwarning("Duplicate", "ผู้ใช้คนนี้รายงานข่าวนี้ซ้ำไม่ได้")
            else:
                messagebox.showerror("Error", res["error"])

    def _submit_verify(self):
        if not self.current_code:
            messagebox.showinfo("Info", "Load ข่าวก่อน")
            return
        cname = self.checker_var.get()
        if cname not in self.checker_map:
            messagebox.showerror("Error", "เลือก checker")
            return
        checker_id = self.checker_map[cname]
        verified_status = self.verify_var.get().strip()

        res = self.controller.submit_verify(self.current_code, checker_id, verified_status)
        if res["ok"]:
            messagebox.showinfo("Verified", f"Verified as {verified_status.upper()} (ห้าม report เพิ่ม)")
            self.controller.refresh_all_views()
            self._render_detail()
        else:
            messagebox.showerror("Error", res["error"])

    def _create_rumour(self):
        try:
            cred = float(self.new_cred.get().strip())
        except ValueError:
            messagebox.showerror("Error", "credibility ต้องเป็นตัวเลข")
            return

        res = self.controller.create_new_rumour(
            self.new_code.get().strip(),
            self.new_title.get().strip(),
            self.new_source.get().strip(),
            cred
        )
        if res["ok"]:
            messagebox.showinfo("OK", "Created rumour")
            self.controller.refresh_all_views()
        else:
            messagebox.showerror("Error", res["error"])

    def refresh_if_open(self):
        if self.win and self.win.winfo_exists() and self.current_code:
            self._refresh_people()
            self._render_detail()

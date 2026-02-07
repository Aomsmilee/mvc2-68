import tkinter as tk
from tkinter import ttk

class SummaryView:
    def __init__(self, root: tk.Tk, controller, on_close=None):
        self.controller = controller
        self.on_close = on_close

        self.win = tk.Toplevel(root)
        self.win.title("View #3: สรุปผล")
        self.win.geometry("900x600")

        # ✅ hook ปุ่มกากบาท
        self.win.protocol("WM_DELETE_WINDOW", self._handle_close)

        wrap = ttk.Frame(self.win)
        wrap.pack(fill="both", expand=True, padx=10, pady=10)

        top = ttk.Frame(wrap)
        top.pack(fill="x")
        ttk.Label(top, text="View #3: สรุป (panic + verified true/false)", font=("Arial", 14, "bold")).pack(side="left")
        ttk.Button(top, text="Refresh", command=self.refresh).pack(side="right")

        ttk.Label(wrap, text="PANIC rumours").pack(anchor="w", pady=(10, 0))
        self.panic_box = tk.Text(wrap, height=10, wrap="word")
        self.panic_box.pack(fill="x", pady=(4, 10))

        ttk.Label(wrap, text="Verified TRUE").pack(anchor="w")
        self.true_box = tk.Text(wrap, height=10, wrap="word")
        self.true_box.pack(fill="x", pady=(4, 10))

        ttk.Label(wrap, text="Verified FALSE").pack(anchor="w")
        self.false_box = tk.Text(wrap, height=10, wrap="word")
        self.false_box.pack(fill="x", pady=(4, 10))

        self.refresh()

    def _handle_close(self):
        # ✅ แจ้ง controller ให้ล้าง reference แล้วค่อย destroy
        if callable(self.on_close):
            self.on_close()
        self.win.destroy()

    def is_open(self) -> bool:
        return self.win is not None and self.win.winfo_exists()

    def refresh(self):
        if not self.is_open():
            return

        panic, vtrue, vfalse = self.controller.load_summary()

        def fill(box: tk.Text, rows, mode: str):
            box.delete("1.0", "end")
            if not rows:
                box.insert("end", "- none\n")
                return
            for r in rows:
                if mode == "panic":
                    box.insert("end", f'- {r["rumour_code"]}: {r["title"]} ({int(r["report_count"])} reports)\n')
                else:
                    box.insert("end", f'- {r["rumour_code"]}: {r["title"]}\n')

        fill(self.panic_box, panic, "panic")
        fill(self.true_box, vtrue, "true")
        fill(self.false_box, vfalse, "false")

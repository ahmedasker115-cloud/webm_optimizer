import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
from classifier import classify, Category
from config import VIDEO_EXTS, OUTPUT_DIR_NAME
from queue import Queue
from workers import EncodeWorker
from processor import trim
import threading
import os
from logging_setup import logger

# colors (dark theme)
BG = "#000000"
FG = "#ffffff"
ACCENT = "#b30000"
PASS_COLOR = "#00b300"
COMPRESS_COLOR = "#ffb84d"
TRIM_COMPRESS_COLOR = "#ff4444"


class App:
    def __init__(self, root):
        self.root = root
        root.title("BN Optimizer")
        root.geometry("520x420")
        root.configure(bg=BG)

        self.label = tk.Label(root, text="Select folder to validate", font=("Segoe UI", 11), bg=BG, fg=FG)
        self.label.pack(pady=10)

        btn_frame = tk.Frame(root, bg=BG)
        btn_frame.pack()
        self.browse_btn = tk.Button(btn_frame, text="Browse Folder", command=self.browse, bg="#111111", fg=FG, activebackground=ACCENT)
        self.browse_btn.pack(side="left", padx=6)

        # Theme toggle (black / red)
        self.theme_btn = tk.Button(btn_frame, text="Theme: Black", command=self.toggle_theme, bg="#111111", fg=FG, activebackground=ACCENT)
        self.theme_btn.pack(side="left", padx=6)

        self.stats = tk.Label(root, text="", justify="left", bg=BG, fg=FG)
        self.stats.pack(pady=10)

        # listbox to display files and their classification
        self.listbox = tk.Listbox(root, width=72, height=12, bg="#0b0b0b", fg=FG, selectbackground=ACCENT)
        self.listbox.pack(pady=6)

        self.start_btn = tk.Button(root, text="Start Processing", state="disabled", command=self.start, bg="#111111", fg=FG, activebackground=ACCENT)
        self.start_btn.pack(pady=10)

        # progress bar and labels
        self.progress_var = tk.DoubleVar(value=0)
        self.progress = ttk.Progressbar(root, variable=self.progress_var, maximum=1.0)
        self.progress.pack(fill="x", padx=12, pady=(0, 6))
        self.current_label = tk.Label(root, text="", bg=BG, fg=FG)
        self.current_label.pack()
        self.count_label = tk.Label(root, text="0/0", bg=BG, fg=FG)
        self.count_label.pack()

    def browse(self):
        folder = Path(filedialog.askdirectory())
        if not folder:
            return

        self.input_dir = folder
        self.output_dir = folder / OUTPUT_DIR_NAME
        self.output_dir.mkdir(exist_ok=True)

        self.groups = {c: [] for c in Category}


        self.listbox.delete(0, tk.END)
        for f in sorted(folder.iterdir()):
            if f.suffix.lower() in VIDEO_EXTS:
                cat = classify(f)
                self.groups[cat].append(f)
                idx = self.listbox.size()
                self.listbox.insert(tk.END, f"{f.name} -> {cat.name}")
                # color code
                try:
                    if cat == Category.PASS:
                        self.listbox.itemconfig(idx, fg=PASS_COLOR)
                    elif cat == Category.COMPRESS_ONLY:
                        self.listbox.itemconfig(idx, fg=COMPRESS_COLOR)
                    elif cat == Category.TRIM_AND_COMPRESS:
                        self.listbox.itemconfig(idx, fg=TRIM_COMPRESS_COLOR)
                    else:
                        self.listbox.itemconfig(idx, fg=FG)
                except Exception:
                    pass

        text = (
            f"PASS: {len(self.groups[Category.PASS])}\n"
            f"COMPRESS ONLY: {len(self.groups[Category.COMPRESS_ONLY])}\n"
            f"TRIM ONLY: {len(self.groups[Category.TRIM_ONLY])}\n"
            f"TRIM + COMPRESS: {len(self.groups[Category.TRIM_AND_COMPRESS])}"
        )
        self.stats.config(text=text)
        self.start_btn.config(state="normal")

    def start(self):
        # run processing in background to keep the GUI responsive
        self.start_btn.config(state="disabled")
        self.browse_btn.config(state="disabled")

        def background():
            q = Queue()
            status_q = Queue()
            self._total = 0
            # compute total
            for cat in (Category.TRIM_ONLY, Category.COMPRESS_ONLY, Category.TRIM_AND_COMPRESS):
                self._total += len(self.groups[cat])

            # initialize progress
            self.root.after(0, lambda: self._update_progress(0, self._total, ""))

            worker = EncodeWorker(q, progress_queue=status_q)
            worker.start()

            # enqueue all tasks (including trim-only) so the single encoder handles them
            for f in self.groups[Category.TRIM_ONLY]:
                out = self.output_dir / f.name
                q.put((Category.TRIM_ONLY, f, out))

            for cat in (Category.COMPRESS_ONLY, Category.TRIM_AND_COMPRESS):
                for f in self.groups[cat]:
                    out = self.output_dir / f.name
                    q.put((cat, f, out))

            # request worker shutdown when queue is empty
            q.put(None)
            # monitor progress from status_q while waiting for worker
            processed = 0
            while True:
                try:
                    msg = status_q.get(timeout=0.2)
                except Exception:
                    # if worker finished and queue empty, break
                    if not worker.is_alive() and q.empty():
                        break
                    continue

                if msg and isinstance(msg, tuple) and msg[0] == 'end':
                    processed += 1
                    # update UI
                    self.root.after(0, lambda p=processed: self._update_progress(p, self._total, msg[1]))
                status_q.task_done()

            q.join()

            # notify on main thread
            self.root.after(0, lambda: messagebox.showinfo("Done", "Processing finished"))
            self.root.after(0, lambda: self.start_btn.config(state="normal"))
            self.root.after(0, lambda: self.browse_btn.config(state="normal"))

        # start UI poll for status queue updates if needed
        t = threading.Thread(target=background, daemon=True)
        t.start()

    def _update_progress(self, processed, total, current_file):
        try:
            if total <= 0:
                self.progress_var.set(0)
            else:
                self.progress_var.set(processed / total)
            self.current_label.config(text=f"Current: {Path(current_file).name if current_file else ''}")
            self.count_label.config(text=f"{processed}/{total}")
        except Exception:
            pass

        t = threading.Thread(target=background, daemon=True)
        t.start()

    def toggle_theme(self):
        # simple toggle between dark (black) and red accent
        current = self.theme_btn.cget("text")
        if "Black" in current:
            # switch to red theme
            bg = "#2b0000"
            fg = "#ffffff"
            self.theme_btn.config(text="Theme: Red")
        else:
            bg = "#000000"
            fg = "#ffffff"
            self.theme_btn.config(text="Theme: Black")

        try:
            self.root.configure(bg=bg)
            for widget in self.root.winfo_children():
                try:
                    widget.configure(bg=bg, fg=fg)
                except Exception:
                    pass
        except Exception:
            pass


def run():
    root = tk.Tk()
    App(root)
    root.mainloop()

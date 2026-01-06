import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from classifier import classify, Category
from config import VIDEO_EXTS, OUTPUT_DIR_NAME
from queue import Queue
from workers import EncodeWorker
from processor import trim


class App:
    def __init__(self, root):
        self.root = root
        root.title("BN Optimizer")
        root.geometry("420x320")

        self.label = tk.Label(root, text="Select folder to validate", font=("Segoe UI", 11))
        self.label.pack(pady=10)

        tk.Button(root, text="Browse Folder", command=self.browse).pack()

        self.stats = tk.Label(root, text="", justify="left")
        self.stats.pack(pady=10)

        self.start_btn = tk.Button(root, text="Start Processing", state="disabled", command=self.start)
        self.start_btn.pack(pady=10)

    def browse(self):
        folder = Path(filedialog.askdirectory())
        if not folder:
            return

        self.input_dir = folder
        self.output_dir = folder / OUTPUT_DIR_NAME
        self.output_dir.mkdir(exist_ok=True)

        self.groups = {c: [] for c in Category}

        for f in folder.iterdir():
            if f.suffix.lower() in VIDEO_EXTS:
                cat = classify(f)
                self.groups[cat].append(f)

        text = (
            f"PASS: {len(self.groups[Category.PASS])}\n"
            f"COMPRESS ONLY: {len(self.groups[Category.COMPRESS_ONLY])}\n"
            f"TRIM ONLY: {len(self.groups[Category.TRIM_ONLY])}\n"
            f"TRIM + COMPRESS: {len(self.groups[Category.TRIM_AND_COMPRESS])}"
        )
        self.stats.config(text=text)
        self.start_btn.config(state="normal")

    def start(self):
        q = Queue()
        worker = EncodeWorker(q)
        worker.start()

        for f in self.groups[Category.TRIM_ONLY]:
            out = self.output_dir / f.name
            trim(f, out)

        for cat in (Category.COMPRESS_ONLY, Category.TRIM_AND_COMPRESS):
            for f in self.groups[cat]:
                out = self.output_dir / f.name
                q.put((cat, f, out))

        q.join()
        messagebox.showinfo("Done", "Processing finished")


def run():
    root = tk.Tk()
    App(root)
    root.mainloop()

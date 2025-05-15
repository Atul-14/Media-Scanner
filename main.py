import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
from scanner import scan_folder

class VideoScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎞️ Video Format Scanner")
        self.root.geometry("1600x800")
        self.root.configure(bg="#121212")
        self.data = []

        self.status_text = tk.StringVar(value="Ready")

        self.columns = [
            "File", "Size", "Resolution", "BitDepth",
            "MKV", "MP4", "HEVC", "H264", "AV1", "HDR", "4K", "DolbyVision",
            "---",
            "DolbyAtmos", "AAC", "MP3", "AC3", "EAC3", "TRUEHD", "DTS", "OPUS", "FLAC", "VORBIS", "PCM"
        ]

        self.setup_gui()

    def setup_gui(self):
        top_frame = tk.Frame(self.root, bg="#121212")
        top_frame.pack(pady=10)

        scan_btn = tk.Button(top_frame, text="📂 Select Folder and Scan", command=self.select_folder,
                             bg="#26a69a", fg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=5)
        scan_btn.pack(side=tk.LEFT, padx=10)

        export_btn = tk.Button(top_frame, text="💾 Export to CSV", command=self.export_to_csv,
                               bg="#42a5f5", fg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=5)
        export_btn.pack(side=tk.LEFT, padx=10)

        clear_btn = tk.Button(top_frame, text="🗑️ Clear Results", command=self.clear_table,
                              bg="#ef5350", fg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=5)
        clear_btn.pack(side=tk.LEFT, padx=10)

        status_bar = tk.Label(self.root, textvariable=self.status_text, bg="#121212", fg="white",
                              font=("Segoe UI", 10, "italic"), anchor="w")
        status_bar.pack(fill=tk.X, padx=10, pady=(0, 5))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#1e1e1e", foreground="white", rowheight=25,
                        fieldbackground="#1e1e1e", font=("Segoe UI", 9))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#2e2e2e", foreground="white")

        tree_frame = tk.Frame(self.root)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        x_scroll = ttk.Scrollbar(tree_frame, orient="horizontal")
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)

        y_scroll = ttk.Scrollbar(tree_frame, orient="vertical")
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(tree_frame, columns=self.columns, show='headings',
                                 xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set)

        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100 if col not in ["File"] else 250, anchor=tk.CENTER)

        self.tree.pack(fill=tk.BOTH, expand=True)

        x_scroll.config(command=self.tree.xview)
        y_scroll.config(command=self.tree.yview)

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.status_text.set(f"Scanning folder: {folder}...")
            self.root.update()
            self.data = scan_folder(folder)
            self.populate_table()
            self.status_text.set("Ready")

    def populate_table(self):
        self.tree.delete(*self.tree.get_children())

        # Define tag styles once
        self.tree.tag_configure("check", foreground="limegreen", font=("Segoe UI", 10, "bold"))
        self.tree.tag_configure("cross", foreground="tomato", font=("Segoe UI", 10, "bold"))

        for item in self.data:
            row = [
                item.get("File", ""),
                item.get("Size", ""),
                item.get("Resolution", ""),
                item.get("BitDepth", "")
            ]

            tags = []

            for col in self.columns[4:]:
                if col == "---":
                    row.append("")
                else:
                    value = item.get(col, False)
                    symbol = "✔️" if value else "✖️"
                    tag = "check" if value else "cross"
                    row.append(symbol)
                    tags.append(tag)

            self.tree.insert("", tk.END, values=row, tags=tags)

    def clear_table(self):
        self.tree.delete(*self.tree.get_children())
        self.data = []
        self.status_text.set("Results cleared. Ready.")

    def export_to_csv(self):
        if not self.data:
            messagebox.showwarning("No Data", "Scan a folder first.")
            return

        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if not path:
            return

        with open(path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.columns)
            writer.writeheader()
            for item in self.data:
                row = {col: item.get(col, "") for col in self.columns if col != "---"}
                writer.writerow(row)

        messagebox.showinfo("Exported", f"CSV saved to:\n{path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoScannerApp(root)
    root.mainloop()
import os
import csv
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES  # NEW IMPORT
from datetime import datetime

from scanner import scan_folder, VIDEO_EXTENSIONS, get_video_info, detect_features

class VideoScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎞️ Video Format Scanner")
        self.root.geometry("1600x900")
        self.data = []

        self.theme = "dark"
        self.themes = {
            "dark": {
                "bg": "#1E1E1E",  # Dark grey background
                "fg": "#D4D4D4",  # Light grey foreground
                "button_bg": "#268BD2", # Blue button
                "button_fg": "#FDF6E3", # Light beige button text
                "tree_bg": "#282828",  # Slightly lighter dark grey tree
                "tree_fg": "#D4D4D4",
                "tree_header_bg": "#3C3C3C",
                "tree_header_fg": "#D4D4D4",
                "tick_fg": "#AECF96",  # Light green for tick
                "cross_fg": "#E9546B", # Light red for cross
            },
            "light": {
                "bg": "#F0F0F0",  # Light grey background
                "fg": "#333333",  # Dark grey foreground
                "button_bg": "#81A2BE", # Light blue button
                "button_fg": "#282A36", # Dark grey button text
                "tree_bg": "#FFFFFF",  # White tree
                "tree_fg": "#333333",
                "tree_header_bg": "#DCDCDC",
                "tree_header_fg": "#333333",
                "tick_fg": "#388E3C",  # Dark green for tick
                "cross_fg": "#D32F2F", # Dark red for cross
            },
        }

        self.status_text = tk.StringVar(value="Ready")

        self.video_formats = ["MKV", "MP4", "HEVC", "H264", "AV1", "HDR", "4K", "DolbyVision"]
        self.audio_formats = ["DolbyAtmos", "AAC", "MP3", "AC3", "EAC3", "TRUEHD", "DTS", "OPUS", "FLAC", "VORBIS", "PCM"]
        self.columns = ["File", "Size", "Resolution", "BitDepth", "Duration", "Modified"] + self.video_formats + self.audio_formats

        self.setup_gui()
        self.apply_theme()

    def get_media_duration(self, filepath):
        """Retrieves the duration of a media file using ffprobe."""
        try:
            cmd = [
                'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1', filepath
            ]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            duration = float(result.stdout.strip())
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            return f"{minutes}m {seconds}s"
        except Exception:
            return "N/A"

    def get_modification_time(self, filepath):
        """Retrieves the last modification time of a file."""
        try:
            timestamp = os.path.getmtime(filepath)
            dt_object = datetime.fromtimestamp(timestamp)
            return dt_object.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return "N/A"

    def setup_gui(self):
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(pady=10)

        self.scan_btn = tk.Button(self.top_frame, text="📂 Select Folder and Scan", command=self.select_folder)
        self.scan_btn.pack(side=tk.LEFT, padx=10)

        self.export_btn = tk.Button(self.top_frame, text="💾 Export to CSV", command=self.export_to_csv)
        self.export_btn.pack(side=tk.LEFT, padx=10)

        self.clear_btn = tk.Button(self.top_frame, text="🗑️ Clear Results", command=self.clear_table)
        self.clear_btn.pack(side=tk.LEFT, padx=10)

        self.theme_btn = tk.Button(self.top_frame, text="🌓 Toggle Theme", command=self.toggle_theme)
        self.theme_btn.pack(side=tk.LEFT, padx=10)

        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.apply_filter())
        self.search_entry = tk.Entry(self.top_frame, textvariable=self.search_var, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=10)

        self.status_frame = tk.Frame(self.root)
        self.status_frame.pack(fill=tk.X, padx=10)

        self.progress = ttk.Progressbar(self.status_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=(0, 5))

        self.status_bar = tk.Label(self.status_frame, textvariable=self.status_text, anchor="w")
        self.status_bar.pack(fill=tk.X, pady=(0, 2))

        self.tree_frame = tk.Frame(self.root)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)

        self.x_scroll = ttk.Scrollbar(self.tree_frame, orient="horizontal")
        self.x_scroll.pack(side=tk.BOTTOM, fill=tk.X)

        self.y_scroll = ttk.Scrollbar(self.tree_frame, orient="vertical")
        self.y_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(self.tree_frame, columns=self.columns, show='headings',
                                 xscrollcommand=self.x_scroll.set, yscrollcommand=self.y_scroll.set)

        for col in self.columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by(c, False))
            self.tree.column(col, width=100 if col != "File" else 300, anchor=tk.CENTER)

        self.tree.pack(fill=tk.BOTH, expand=True)

        self.x_scroll.config(command=self.tree.xview)
        self.y_scroll.config(command=self.tree.yview)

        self.tree.tag_configure("available", foreground=self.themes[self.theme]["tick_fg"])
        self.tree.tag_configure("missing", foreground=self.themes[self.theme]["cross_fg"])

        # Drag-and-drop folder support
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.drop_folder)

        self.tree.bind("<Motion>", self.on_hover)

    def apply_theme(self):
        t = self.themes[self.theme]
        self.root.configure(bg=t["bg"])
        for widget in [self.top_frame, self.status_frame, self.tree_frame, self.status_bar]:
            widget.configure(bg=t["bg"])
        self.status_bar.configure(fg=t["fg"])
        for button in [self.scan_btn, self.export_btn, self.clear_btn, self.theme_btn]:
            button.configure(bg=t["button_bg"], fg=t["button_fg"])
        self.search_entry.configure(bg=t["tree_bg"], fg=t["tree_fg"], insertbackground=t["tree_fg"])

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=t["tree_bg"], foreground=t["tree_fg"], fieldbackground=t["tree_bg"])
        style.configure("Treeview.Heading", background=t["tree_header_bg"], foreground=t["tree_header_fg"], font=("Segoe UI", 10, "bold"))
        self.tree.tag_configure("available", foreground=t["tick_fg"])
        self.tree.tag_configure("missing", foreground=t["cross_fg"])
        self.populate_table() # Re-populate to apply color changes
    def toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self.apply_theme()

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.status_text.set(f"Scanning folder: {folder}...")
            self.progress.start()
            self.root.update()
            thread = threading.Thread(target=self.threaded_scan, args=(folder,))
            thread.start()

    def threaded_scan(self, folder):
        results = []
        for root, _, files in os.walk(folder):
            for file in files:
                if os.path.splitext(file)[1].lower() in VIDEO_EXTENSIONS:  # Corrected line
                    path = os.path.join(root, file)
                    print(f"Scanning: {path}")
                    info = get_video_info(path)
                    if info:
                        features = detect_features(info, path)
                        duration = self.get_media_duration(path)
                        modified_time = self.get_modification_time(path)
                        features["Duration"] = duration
                        features["Modified"] = modified_time
                        results.append(features)
        self.data = results
        self.root.after(0, self.populate_table)
        self.root.after(0, lambda: self.status_text.set("Ready"))
        self.root.after(0, self.progress.stop)
    def populate_table(self):
        self.tree.delete(*self.tree.get_children())
        for item in self.data:
            row = [
                item.get("File", ""), item.get("Size", ""), item.get("Resolution", ""), item.get("BitDepth", ""),
                item.get("Duration", ""), item.get("Modified", ""),
                *["✔️" if item.get(col, False) else "✖️" for col in self.columns[6:]]
            ]
            tags = ["available" if item.get(self.columns[6:][i], False) else "missing" for i in range(len(self.columns[6:]))]
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
                row = {col: item.get(col, "") for col in self.columns}
                writer.writerow(row)

        messagebox.showinfo("Exported", f"CSV saved to:\n{path}")

    def apply_filter(self):
        query = self.search_var.get().lower()
        for i in self.tree.get_children():
            self.tree.delete(i)
        for item in self.data:
            if query in item.get("File", "").lower():
                row = [
                    item.get("File", ""), item.get("Size", ""), item.get("Resolution", ""), item.get("BitDepth", ""),
                    item.get("Duration", ""), item.get("Modified", ""),
                    *["✔️" if item.get(col, False) else "✖️" for col in self.columns[6:]]
                ]
                tags = ["available" if item.get(self.columns[6:][i], False) else "missing" for i in range(len(self.columns[6:]))]
                self.tree.insert("", tk.END, values=row, tags=tags)

    def sort_by(self, col, descending):
        data = [(self.tree.set(child, col), child) for child in self.tree.get_children()]
        data.sort(reverse=descending)
        for index, (val, child) in enumerate(data):
            self.tree.move(child, '', index)
        self.tree.heading(col, command=lambda c=col: self.sort_by(c, not descending))

    def drop_folder(self, event):
        paths = self.root.tk.splitlist(event.data)
        for path in paths:
            if os.path.isdir(path):
                self.status_text.set(f"Scanning dropped folder: {path}")
                self.progress.start()
                thread = threading.Thread(target=self.threaded_scan, args=(path,))
                thread.start()

    def on_hover(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            row_id = self.tree.identify_row(event.y)
            col_id = self.tree.identify_column(event.x)
            if row_id and col_id:
                value = self.tree.set(row_id, self.tree.column(col_id)['id'])
                self.tree.tooltip = getattr(self, 'tooltip', None)
                if self.tree.tooltip:
                    self.tree.tooltip.destroy()
                if len(value) > 40:
                    self.tree.tooltip = tk.Toplevel(self.tree)
                    self.tree.tooltip.wm_overrideredirect(True)
                    self.tree.tooltip.configure(bg="#333", padx=5, pady=3)
                    label = tk.Label(self.tree.tooltip, text=value, bg="#333", fg="white", font=("Segoe UI", 9))
                    label.pack()
                    x, y = event.x_root + 10, event.y_root + 10
                    self.tree.tooltip.wm_geometry(f"+{x}+{y}")

# Main entry point
if __name__ == "__main__":
    root = TkinterDnD.Tk()  # Use DnD-enabled root
    app = VideoScannerApp(root)
    root.mainloop()
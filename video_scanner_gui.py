import os
import subprocess
import json
import tkinter as tk
from tkinter import filedialog, ttk
import threading
import shutil

if not shutil.which("ffprobe"):
    raise EnvironmentError("ffprobe not found. Please install FFmpeg and add it to your system PATH.")


VIDEO_EXTENSIONS = ['.mp4', '.mkv', '.avi', '.mov', '.webm']

def get_video_info(filepath):
    filepath = os.path.normpath(filepath)
    if not os.path.isfile(filepath):
        print(f"File not found: {filepath}")
        return None

    try:
        cmd = [
            'ffprobe', '-v', 'error', '-print_format', 'json',
            '-show_format', '-show_streams', filepath
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Error scanning {filepath}: {e}")
        return None

def detect_features(info, filepath):
    container = os.path.splitext(filepath)[1][1:].lower()
    format_name = info.get("format", {}).get("format_long_name", "")
    size_mb = round(float(info.get("format", {}).get("size", 0)) / (1024 * 1024), 2)

    video_streams = [s for s in info.get("streams", []) if s["codec_type"] == "video"]
    audio_streams = [s for s in info.get("streams", []) if s["codec_type"] == "audio"]

    video_codec = video_streams[0].get("codec_name", "N/A") if video_streams else "N/A"
    resolution = f"{video_streams[0].get('width', 0)}x{video_streams[0].get('height', 0)}" if video_streams else "N/A"
    width = video_streams[0].get("width", 0)
    bit_depth = video_streams[0].get("bits_per_raw_sample") or video_streams[0].get("bits_per_sample")
    hdr = "smpte2084" in video_streams[0].get("color_transfer", "").lower() if video_streams else False
    dolby_vision = "dvhe" in video_streams[0].get("profile", "").lower() if video_streams else False

    atmos = any("atmos" in (stream.get("tags", {}).get("title", "").lower() or "") for stream in audio_streams)
    atmos = atmos or any(stream.get("codec_name") in ["truehd", "eac3"] for stream in audio_streams)

    return {
        "File": os.path.basename(filepath),
        "Size": f"{size_mb} MB",
        "MKV": container == "mkv",
        "MP4": container == "mp4",
        "HEVC": video_codec == "hevc",
        "H264": video_codec == "h264",
        "AV1": video_codec == "av1",
        "4K": width >= 3840,
        "HDR": hdr,
        "DolbyVision": dolby_vision,
        "DolbyAtmos": atmos,
        "Resolution": resolution,
        "BitDepth": f"{bit_depth or 'N/A'}-bit"
    }

# ---------------- GUI -----------------

class VideoScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Format Scanner")
        self.root.geometry("1200x600")
        self.setup_gui()

    def setup_gui(self):
        btn = tk.Button(self.root, text="Select Folder and Scan", command=self.select_folder)
        btn.pack(pady=10)

        self.status_label = tk.Label(self.root, text="Waiting for input...", anchor='w')
        self.status_label.pack(fill='x', padx=10)

        columns = [
            "File", "Size", "MKV", "MP4", "HEVC", "H264", "AV1", "4K",
            "HDR", "DolbyVision", "DolbyAtmos", "Resolution", "BitDepth"
        ]
        self.tree = ttk.Treeview(self.root, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor=tk.CENTER)
        self.tree.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree.configure(yscroll=scrollbar.set)

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            threading.Thread(target=self.scan_folder, args=(folder,), daemon=True).start()

    def scan_folder(self, folder):
        self.status_label.config(text="Scanning folder...")
        results = []
        for root, _, files in os.walk(folder):
            for file in files:
                if os.path.splitext(file)[1].lower() in VIDEO_EXTENSIONS:
                    path = os.path.join(root, file)
                    self.status_label.config(text=f"Scanning: {file}")
                    if not os.path.isfile(path):
                        print(f"Skipped missing file: {path}")
                        continue
                    info = get_video_info(path)
                    if info:
                        features = detect_features(info, path)
                        results.append(features)
                        self.add_row(features)
        self.status_label.config(text="Scan complete.")

    def add_row(self, item):
        row = [
            item["File"], item["Size"],
            "✅" if item["MKV"] else "❌",
            "✅" if item["MP4"] else "❌",
            "✅" if item["HEVC"] else "❌",
            "✅" if item["H264"] else "❌",
            "✅" if item["AV1"] else "❌",
            "✅" if item["4K"] else "❌",
            "✅" if item["HDR"] else "❌",
            "✅" if item["DolbyVision"] else "❌",
            "✅" if item["DolbyAtmos"] else "❌",
            item["Resolution"],
            item["BitDepth"]
        ]
        self.tree.insert("", tk.END, values=row)

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = VideoScannerApp(root)
    root.mainloop()

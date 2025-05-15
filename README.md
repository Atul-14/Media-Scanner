📘 Video Format Scanner – User Manual
====================================

Version: 1.0
Author: [Your Name or Company]
Platform: Windows
Interface: Desktop GUI (Tkinter)

🎯 Overview
-----------
The Video Format Scanner is a user-friendly Windows application that scans folders for video files and displays detailed information about each file. It detects video resolution, bit depth, audio formats (like Dolby Atmos, DTS), and video formats (like HDR, 4K, Dolby Vision), all in a clean, sortable table.

Ideal for home theater enthusiasts, media archivists, or anyone organizing large video libraries.

✅ Features
-----------
- 📂 Drag-and-drop folder support
- 🎞️ Scans common video formats (MP4, MKV, etc.)
- 🧠 Detects video/audio codecs: HDR, HEVC, Atmos, DTS, etc.
- 📏 Resolution, duration, and bit depth info
- 🔍 Search and filter by filename
- 🗂️ Sort by any column
- 💾 Export scan results to CSV
- 🌗 Dark and light themes
- 📊 Progress bar and real-time status
- 🗑️ Clear scan results
- ✨ Tooltips for long filenames

🖥️ System Requirements
-----------------------
- OS: Windows 10 or later
- Python: 3.8+
- Dependencies:
  - tkinter (comes with Python)
  - tkinterdnd2: For drag-and-drop support
    Install via pip:
    pip install tkinterdnd2

🚀 How to Use
-------------
1. Start the App
   Run the main.py file:
   python main.py

2. Select a Folder
   - Click "📂 Select Folder and Scan" to choose a folder with video files.
   - Or, simply drag a folder from File Explorer and drop it onto the app window.

3. View Results
   After scanning, a table will show:
   - File name, size, resolution, bit depth, duration, modified date
   - Format detection: green checkmarks ✅ for found, red ❌ for not found

4. Search & Filter
   Use the search box to filter by file name.

5. Sort Columns
   Click any column header to sort (e.g., by resolution or file size).

6. Export Results
   Click "💾 Export to CSV" to save results to a spreadsheet.

7. Clear Results
   Click "🗑️ Clear Results" to reset the table.

8. Toggle Theme
   Click "🌓 Toggle Theme" to switch between dark and light modes.

📂 Supported Formats
---------------------
- Video Codecs: MKV, MP4, HEVC, H.264, AV1, HDR, 4K, Dolby Vision
- Audio Codecs: Dolby Atmos, AAC, MP3, AC3, EAC3, TrueHD, DTS, Opus, FLAC, Vorbis, PCM

📌 Tips
-------
- The app does not modify any files.
- You can scan subfolders automatically — just drop the top-level folder.
- Tooltips show full filenames if they are too long to fit in the table.

🛠️ Troubleshooting
-------------------
| Issue                    | Solution                                      |
|--------------------------|-----------------------------------------------|
| Drag-and-drop doesn't work | Make sure tkinterdnd2 is installed         |
| App won't launch         | Ensure Python 3.8+ is installed               |
| Codec detection incorrect| Make sure ffprobe or your scanner.py supports the codec |
| Export fails             | Ensure you selected a writable location       |

📞 Support
----------
For help, feature requests, or bugs:
📧 Email: atulk1402@outlook.com
🐛 GitHub Issues: https://github.com/yourname/video-format-scanner/issues

📄 License
----------
MIT License – Free for personal and commercial use.
See LICENSE.txt for full terms.

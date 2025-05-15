import os
import subprocess
import json

VIDEO_EXTENSIONS = ['.mp4', '.mkv', '.avi', '.mov', '.webm']

AUDIO_FORMATS = ["aac", "mp3", "ac3", "eac3", "truehd", "dts", "opus", "flac", "vorbis", "pcm"]

def get_video_info(filepath):
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
    atmos = any("atmos" in (s.get("tags", {}).get("title", "").lower() or "") for s in audio_streams)
    atmos = atmos or any(s.get("codec_name") in ["truehd", "eac3"] for s in audio_streams)

    audio_codecs = {fmt: False for fmt in AUDIO_FORMATS}
    for stream in audio_streams:
        codec = stream.get("codec_name", "").lower()
        if codec in audio_codecs:
            audio_codecs[codec] = True

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
        "BitDepth": f"{bit_depth or 'N/A'}-bit",
        **{fmt.upper(): found for fmt, found in audio_codecs.items()}
    }

def scan_folder(folder):
    results = []
    for root, _, files in os.walk(folder):
        for file in files:
            if os.path.splitext(file)[1].lower() in VIDEO_EXTENSIONS:
                path = os.path.join(root, file)
                print(f"Scanning: {path}")
                info = get_video_info(path)
                if info:
                    results.append(detect_features(info, path))
    return results

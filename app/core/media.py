import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

def ffmpeg_executable():
    return shutil.which("ffmpeg") or _winget_binary("ffmpeg.exe") or __import__("imageio_ffmpeg").get_ffmpeg_exe()

def _winget_binary(name):
    if os.name != "nt":
        return None
    base = Path.home() / "AppData" / "Local" / "Microsoft" / "WinGet" / "Packages"
    matches = list(base.glob(f"Gyan.FFmpeg_*/ffmpeg-*/bin/{name}"))
    return str(matches[-1]) if matches else None

def ffprobe_executable():
    found = shutil.which("ffprobe") or _winget_binary("ffprobe.exe")
    if found:
        return found
    sibling = Path(ffmpeg_executable()).with_name("ffprobe.exe" if os.name == "nt" else "ffprobe")
    if sibling.exists():
        return str(sibling)
    raise RuntimeError("Thiếu FFprobe. Hãy cài FFmpeg đầy đủ và thêm thư mục bin vào PATH.")

def probe(path):
    result = subprocess.run([ffprobe_executable(), "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode:
        raise ValueError(f"Không đọc được file media {path}: {result.stderr.strip()}")
    return json.loads(result.stdout)

def duration(path):
    data = probe(path)
    value = float(data.get("format", {}).get("duration", 0))
    if value <= 0:
        raise ValueError(f"Không xác định được thời lượng: {path}")
    return value

def run_ffmpeg(args, cancel=None, cwd=None):
    kwargs = {"stdout": subprocess.DEVNULL}
    if os.name == "nt":
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    with tempfile.TemporaryFile() as errors:
        process = subprocess.Popen([ffmpeg_executable(), "-hide_banner", "-y", *map(str, args)], cwd=cwd, stderr=errors, **kwargs)
        try:
            while process.poll() is None:
                if cancel and cancel.is_set():
                    process.kill()
                    process.wait()
                    raise RuntimeError("Đã hủy tác vụ.")
                try:
                    process.wait(timeout=0.2)
                except subprocess.TimeoutExpired:
                    pass
            if process.returncode:
                errors.seek(0)
                raise RuntimeError(errors.read().decode("utf-8", "replace")[-3000:])
        finally:
            if process.poll() is None:
                process.kill()

def normalize_audio(source, output, cancel=None):
    run_ffmpeg(["-i", source, "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", output], cancel)

def validate_output(path, expected_size, expected_duration):
    data = probe(path)
    streams = data["streams"]
    video = next((s for s in streams if s["codec_type"] == "video"), None)
    audio = next((s for s in streams if s["codec_type"] == "audio"), None)
    if not video or not audio or video["codec_name"] != "h264" or audio["codec_name"] != "aac":
        raise RuntimeError("Video xuất thiếu stream H.264/AAC hợp lệ.")
    if (video["width"], video["height"]) != expected_size:
        raise RuntimeError("Video xuất sai độ phân giải.")
    if abs(float(data["format"]["duration"]) - expected_duration) > 0.6:
        raise RuntimeError("Thời lượng video xuất không khớp audio.")
    if video.get("pix_fmt") != "yuv420p":
        raise RuntimeError("Pixel format video không phải yuv420p.")
    return data

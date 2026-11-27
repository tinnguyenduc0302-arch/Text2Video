import re
import shutil
from pathlib import Path

IMAGE = {".jpg", ".jpeg", ".png"}
VIDEO = {".mp4", ".mov", ".avi", ".mkv"}
AUDIO = {".wav", ".mp3"}

def valid_file(value, extensions):
    path = Path(value)
    if not path.is_file() or path.suffix.lower() not in extensions or path.stat().st_size == 0:
        raise ValueError(f"File không hợp lệ hoặc không tồn tại: {value}")
    return path

def validate_folder(value, required_bytes=500_000_000):
    if not value:
        raise ValueError("Hãy chọn thư mục lưu video.")
    path = Path(value)
    if not path.is_dir():
        raise ValueError("Thư mục lưu video không tồn tại.")
    if shutil.disk_usage(path).free < required_bytes:
        raise ValueError("Không đủ dung lượng trống trong thư mục lưu video.")
    try:
        import tempfile
        with tempfile.NamedTemporaryFile(dir=path, prefix=".vtv-check-", delete=True):
            pass
    except OSError as exc:
        raise ValueError(f"Không thể ghi vào thư mục lưu video: {exc}") from exc
    return path

def parse_srt(path, audio_duration=None):
    raw = valid_file(path, {".srt"}).read_text(encoding="utf-8-sig")
    blocks = re.split(r"\r?\n\s*\r?\n", raw.strip())
    entries = []
    pattern = re.compile(r"^(\d{2,}):(\d{2}):(\d{2}),(\d{3})\s+-->\s+(\d{2,}):(\d{2}):(\d{2}),(\d{3})$")
    for index, block in enumerate(blocks, 1):
        lines = block.splitlines()
        if lines and lines[0].strip().isdigit():
            lines = lines[1:]
        if len(lines) < 2:
            raise ValueError(f"SRT mục {index}: thiếu timestamp hoặc nội dung.")
        match = pattern.fullmatch(lines[0].strip())
        if not match:
            raise ValueError(f"SRT mục {index}: timestamp sai định dạng.")
        numbers = list(map(int, match.groups()))
        start = ((numbers[0]*60 + numbers[1])*60 + numbers[2]) + numbers[3]/1000
        end = ((numbers[4]*60 + numbers[5])*60 + numbers[6]) + numbers[7]/1000
        if any(numbers[i] >= 60 for i in (1, 2, 5, 6)) or end <= start:
            raise ValueError(f"SRT mục {index}: khoảng thời gian không hợp lệ.")
        if entries and start < entries[-1][1]:
            raise ValueError(f"SRT mục {index}: chồng lấn mục trước.")
        if audio_duration is not None and end > audio_duration + 0.25:
            raise ValueError(f"SRT mục {index}: kết thúc {end:.2f}s vượt thời lượng audio {audio_duration:.2f}s.")
        entries.append((start, end, "\n".join(lines[1:])))
    if not entries:
        raise ValueError("File SRT không có phụ đề.")
    return entries

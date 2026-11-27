from pathlib import Path
from app.core.validation import parse_srt

def transcribe(audio, output):
    from faster_whisper import WhisperModel
    model = WhisperModel("small", device="cpu", compute_type="int8", local_files_only=True)
    segments, _ = model.transcribe(str(audio), beam_size=5)
    lines = []
    for index, item in enumerate(segments, 1):
        lines.extend((str(index), f"{timestamp(item.start)} --> {timestamp(item.end)}", item.text.strip(), ""))
    if not lines:
        raise RuntimeError("Không nhận dạng được lời nói để tạo phụ đề.")
    Path(output).write_text("\n".join(lines), encoding="utf-8-sig")
    return output

def timestamp(seconds):
    ms = round(seconds * 1000)
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def assert_subtitles(path, duration):
    return parse_srt(path, duration)

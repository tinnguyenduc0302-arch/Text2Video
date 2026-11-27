import tempfile
import time
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from app.config.defaults import SIZES
from app.core.media import duration, normalize_audio, probe, run_ffmpeg, validate_output
from app.core.model import checkpoint, sync
from app.core.subtitles import assert_subtitles, transcribe
from app.core.tts import synthesize
from app.core.validation import AUDIO, IMAGE, VIDEO, valid_file, validate_folder
from app.core.faces import create_detector, detect_one

def prepare_face(face, temp, audio_length, cancel=None):
    import cv2
    sample = temp / "face-check.jpg"
    run_ffmpeg(["-i", face, "-frames:v", "1", sample], cancel)
    frame = cv2.imread(str(sample))
    if frame is None:
        raise ValueError("Không đọc được ảnh/video nhân vật.")
    detect_one(frame, create_detector())
    if face.suffix.lower() in IMAGE:
        local = temp / ("character" + face.suffix.lower())
        shutil.copy2(face, local)
        return local
    local = temp / "character.mp4"
    run_ffmpeg(["-stream_loop", "-1", "-i", face, "-t", str(audio_length), "-an", "-r", "25", "-c:v", "libx264", "-pix_fmt", "yuv420p", local], cancel)
    return local

@dataclass
class RenderRequest:
    mode: int
    face: str
    folder: str
    text: str = ""
    voice: str = "vi-VN-HoaiMyNeural"
    audio: str = ""
    srt: str = ""
    model: str = "gan"
    quality: str = "1080p"
    aspect: str = "16:9"
    subtitles: bool = False
    zoom: int = 100
    vertical: int = 0

def output_path(folder):
    stem = "VoicetoVideo_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    path = Path(folder) / f"{stem}.mp4"
    index = 2
    while path.exists():
        path = Path(folder) / f"{stem}_{index}.mp4"
        index += 1
    return path

def render(req, report=lambda step, value: None, cancel=None):
    started = time.monotonic()
    report("Đang kiểm tra dữ liệu", 0)
    face = valid_file(req.face, IMAGE | VIDEO).resolve()
    folder = validate_folder(req.folder).resolve()
    checkpoint(req.model)
    if req.mode in (2, 3):
        audio_source = valid_file(req.audio, AUDIO).resolve()
        audio_length = duration(audio_source)
    elif req.mode == 1:
        if not req.text.strip():
            raise ValueError("Hãy nhập văn bản.")
        audio_source = None
    else:
        raise ValueError("Chế độ không hợp lệ.")
    if req.mode == 3:
        assert_subtitles(req.srt, audio_length)
    if not 50 <= req.zoom <= 200 or not -100 <= req.vertical <= 100:
        raise ValueError("Vị trí hoặc mức zoom không hợp lệ.")
    with tempfile.TemporaryDirectory(prefix="VoicetoVideo-") as temp_name:
        temp = Path(temp_name)
        if req.mode == 1:
            report("Đang tạo giọng nói (cần Internet)", 5)
            audio_source = temp / "tts.mp3"
            synthesize(req.text, req.voice, audio_source)
            audio_length = duration(audio_source)
        report("Đang chuẩn bị âm thanh", 10)
        normalized = temp / "audio.wav"
        normalize_audio(audio_source, normalized, cancel)
        subtitle = None
        if req.subtitles:
            report("Đang xử lý phụ đề", 15)
            if req.mode == 3:
                subtitle = Path(req.srt).resolve()
            else:
                subtitle = temp / "captions.srt"
                transcribe(normalized, subtitle)
                assert_subtitles(subtitle, audio_length)
        report("Đang nhận dạng khuôn mặt", 18)
        prepared_face = prepare_face(face, temp, audio_length, cancel)
        report("Đang đồng bộ khẩu hình", 20)
        raw = temp / "lipsync.avi"
        sync(prepared_face, normalized, raw, req.model, cancel)
        if cancel and cancel.is_set():
            raise RuntimeError("Đã hủy tác vụ.")
        report("Đang ghép audio và video", 85)
        width, height = SIZES[(req.quality, req.aspect)]
        target = output_path(folder)
        staging = temp / "output.mp4"
        zoom = req.zoom / 100
        offset = round(req.vertical * height * 0.003)
        foreground_width = round(width * zoom / 2) * 2
        foreground_height = round(height * zoom / 2) * 2
        filtergraph = (f"[0:v]split=2[bg][fg];"
                       f"[bg]scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},boxblur=20:1[back];"
                       f"[fg]scale={foreground_width}:{foreground_height}:force_original_aspect_ratio=decrease[front];"
                       f"[back][front]overlay=(W-w)/2:(H-h)/2+{offset},setsar=1,fps=25")
        if subtitle:
            # FFmpeg's subtitles filter parses paths; copy to task-local ASCII path first.
            local_srt = temp / "subtitles.srt"
            local_srt.write_bytes(subtitle.read_bytes())
            filtergraph += ",subtitles=subtitles.srt:force_style='FontName=Arial,FontSize=22,PrimaryColour=&HFFFFFF&,OutlineColour=&H000000&,Outline=2,Alignment=2,MarginV=48'"
        filtergraph += "[outv]"
        ffargs = ["-i", raw, "-i", audio_source, "-filter_complex", filtergraph, "-map", "[outv]", "-map", "1:a:0", "-t", str(audio_length), "-r", "25", "-fps_mode", "cfr", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", staging]
        run_ffmpeg(ffargs, cancel, cwd=temp)
        report("Đang kiểm tra video đầu ra", 95)
        info = validate_output(staging, (width, height), audio_length)
        pending = target.with_suffix(".partial")
        try:
            shutil.copy2(staging, pending)
            pending.replace(target)
        finally:
            pending.unlink(missing_ok=True)
    report("Hoàn thành", 100)
    return {"path": target, "duration": float(info["format"]["duration"]), "size": (width, height), "bytes": target.stat().st_size, "elapsed": time.monotonic() - started}

from app.core.media import duration, normalize_audio, probe, run_ffmpeg, validate_output

def test_audio_and_video_with_unicode_paths(tmp_path):
    folder = tmp_path / "thư mục có dấu"
    folder.mkdir()
    source = folder / "âm thanh.wav"
    normalized = folder / "chuẩn hóa.wav"
    video = folder / "kết quả.mp4"
    run_ffmpeg(["-f", "lavfi", "-i", "sine=frequency=440:duration=1", source])
    normalize_audio(source, normalized)
    assert abs(duration(normalized) - 1) < 0.05
    run_ffmpeg(["-f", "lavfi", "-i", "color=c=blue:s=320x240:r=25:d=1", "-i", normalized,
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-movflags", "+faststart", video])
    assert validate_output(video, (320, 240), 1)["streams"]

from pathlib import Path
import sys

ROOT = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parents[2]
MODELS = ROOT / "models" / "wav2lip"
MODEL_FILES = {"wav2lip": MODELS / "wav2lip.pth", "gan": MODELS / "wav2lip_gan.pth"}
SIZES = {("720p", "16:9"): (1280, 720), ("720p", "9:16"): (720, 1280), ("1080p", "16:9"): (1920, 1080), ("1080p", "9:16"): (1080, 1920)}
VOICES = {"Tiếng Việt · Nữ": "vi-VN-HoaiMyNeural", "Tiếng Việt · Nam": "vi-VN-NamMinhNeural", "English · Female": "en-US-JennyNeural", "English · Male": "en-US-GuyNeural"}

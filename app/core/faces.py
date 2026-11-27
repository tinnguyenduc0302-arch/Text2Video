from pathlib import Path
import cv2
import hashlib
from app.config.defaults import MODELS

DETECTOR_PATH = MODELS / "s3fd.pth"

def create_detector():
    if not DETECTOR_PATH.is_file() or DETECTOR_PATH.stat().st_size < 1_000_000:
        raise FileNotFoundError(f"Thiếu model nhận diện khuôn mặt {DETECTOR_PATH.name}. Hãy cài theo README.")
    with DETECTOR_PATH.open("rb") as stream:
        if hashlib.file_digest(stream, "sha256").hexdigest() != "619a31681264d3f7f7fc7a16a42cbbe8b23f31a256f75a366e5a1bcd59b33543":
            raise ValueError("Model nhận diện khuôn mặt sai SHA-256.")
    from face_alignment.detection.sfd import FaceDetector
    return FaceDetector(device="cpu", path_to_detector=str(DETECTOR_PATH))

def detect_one(image, detector):
    height, width = image.shape[:2]
    scale = min(1.0, 640 / max(height, width))
    small = cv2.resize(image, (round(width*scale), round(height*scale))) if scale < 1 else image
    found = detector.detect_from_image(small)
    strong = [box for box in found if box[4] >= 0.8]
    if len(strong) != 1:
        raise ValueError("Cần đúng một khuôn mặt rõ ràng trong khung hình.")
    x1, y1, x2, y2 = [round(float(v)/scale) for v in strong[0][:4]]
    return (x1, y1, x2, y2)

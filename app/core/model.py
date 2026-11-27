import multiprocessing as mp
import queue
import time
import hashlib
from app.config.defaults import MODEL_FILES

EXPECTED_SHA256 = {
    "wav2lip": "7ab9249147fd8d7884983567883222b7a86b6f94282354887825dfee7d608999",
    "gan": "180cfd49d31d47f195d5bfc62830ffe2c40724b7bbbce6faadc73ac6ab1a3b8e",
}

def checkpoint(kind):
    path = MODEL_FILES[kind]
    if not path.is_file() or path.stat().st_size < 1_000_000:
        raise FileNotFoundError(f"Thiếu checkpoint {path.name}. Hãy tải từ nguồn Wav2Lip chính thức và đặt vào {path.parent}. Không phân phối checkpoint khi chưa xác minh giấy phép.")
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    if digest != EXPECTED_SHA256[kind]:
        raise ValueError(f"Checkpoint {path.name} không khớp SHA-256 của file đã xác minh. Hãy tải lại từ nguồn chính thức.")
    return path

def _sync_child(face, audio, output, kind, messages):
    try:
        _sync_impl(face, audio, output, kind)
        messages.put(None)
    except Exception as exc:
        messages.put(f"{type(exc).__name__}: {exc}")

def sync(face, audio, output, kind, cancel=None):
    messages = mp.Queue()
    process = mp.Process(target=_sync_child, args=(face, audio, output, kind, messages))
    process.start()
    try:
        while process.is_alive():
            if cancel and cancel.is_set():
                process.terminate()
                process.join(timeout=5)
                if process.is_alive():
                    process.kill()
                raise RuntimeError("Đã hủy tác vụ.")
            process.join(timeout=0.2)
        try:
            error = messages.get(timeout=2)
        except queue.Empty:
            error = f"Tiến trình AI dừng với mã {process.exitcode}."
        if error:
            raise RuntimeError(error)
    finally:
        if process.is_alive():
            process.kill()
        process.join()
        messages.close()

def _sync_impl(face, audio, output, kind):
    path = checkpoint(kind)
    from lipsync import LipSync
    import shutil
    import torch
    from app.core.faces import create_detector, detect_one

    class LocalLipSync(LipSync):
        def detect_faces_in_frames(self, images):
            detector = create_detector()
            boxes = []
            for image in images:
                boxes.append(detect_one(image, detector))
            return boxes

        def _load_model_for_inference(self):
            return torch.jit.load(str(path), map_location="cpu").eval()

        def _merge_audio_video(self, audio_file, temp_video, outfile):
            shutil.copyfile(temp_video, outfile)

    lip = LocalLipSync(model="wav2lip", checkpoint_path=str(path), nosmooth=False, device="cpu", img_size=96, save_cache=False, wav2lip_batch_size=8)
    lip.sync(str(face), str(audio), str(output))

import asyncio

def synthesize(text, voice, output):
    import edge_tts
    if not text.strip():
        raise ValueError("Hãy nhập văn bản cần đọc.")
    try:
        asyncio.run(edge_tts.Communicate(text, voice).save(str(output)))
    except Exception as exc:
        raise RuntimeError(f"Không tạo được giọng nói Edge-TTS. Kiểm tra kết nối Internet: {exc}") from exc

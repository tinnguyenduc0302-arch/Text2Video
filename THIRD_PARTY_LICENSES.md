# Thành phần bên thứ ba

- Wav2Lip và các checkpoint: dự án của Rudrabha Mukhopadhyay và cộng sự. Repository chính thức nêu giới hạn **chỉ sử dụng nghiên cứu, học thuật và cá nhân, không thương mại**. Không đưa checkpoint vào repository hoặc bản cài.
- `lipsync` (PyPI): wrapper Python dùng bởi notebook gốc. Cần kiểm tra giấy phép cụ thể của bản cài trước khi phân phối nhị phân.
- S3FD face detector: tải từ URL do thư viện `face-alignment` công bố. Cần kiểm tra giấy phép trọng số trước khi phân phối.
- PySide6: LGPLv3/GPL/commercial của Qt for Python. Bản phân phối phải tuân thủ điều khoản Qt.
- PyTorch, OpenCV, FFmpeg, Edge-TTS, faster-whisper và dependencies liên quan: xem license đi kèm từng gói ở phiên bản cài đặt. FFmpeg có thể là LGPL hoặc GPL tùy bản build.
- Text2Video gốc: chưa thấy file LICENSE ở repository được clone; vì vậy không mặc nhiên xem mã notebook là được phép tái phân phối. Ứng dụng mới chỉ tham khảo ý tưởng và tên API.

Không tuyên bố quyền sử dụng thương mại cho bản này.

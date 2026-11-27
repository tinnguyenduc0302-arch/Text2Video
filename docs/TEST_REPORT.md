# Báo cáo kiểm thử 27/11/2026

Môi trường: Windows 11, Python 3.12.10, PyTorch 2.15 CPU, FFmpeg/FFprobe 9.1. Không đọc được CPU/GPU qua CIM trong sandbox; cấu hình Lenovo do người dùng cung cấp chưa được xác minh bằng công cụ hệ thống.

## Đã chạy

- `pytest`: 5 bài qua (SRT UTF-8 BOM tiếng Việt, timestamp vượt audio, tránh ghi đè, FFmpeg với đường dẫn Unicode, trạng thái GUI).
- GUI khởi tạo được bằng Qt offscreen. Chưa kiểm tra DPI và trải nghiệm thực tế bằng màn hình tương tác.
- `ffprobe` đọc được media mẫu. Kiểm thử audio WAV/video H.264 AAC tổng hợp 1 giây với đường dẫn có dấu qua.
- Mode 2: audio WAV + ảnh, GAN, 720p 16:9, không phụ đề: video 1,5 giây, 1280×720, H.264/AAC, 25 FPS, khoảng 24 giây xử lý.
- Mode 3: WAV + SRT tiếng Việt, checkpoint thường, 1080p 9:16, có phụ đề: video 1,5 giây, 1080×1920, H.264/AAC, khoảng 21 giây xử lý.
- Mode 1: Edge-TTS tiếng Việt + ảnh, GAN, 720p: video 4,08 giây, H.264/AAC, khoảng 19 giây xử lý.
- Mode 2: MP3 + ảnh, GAN, 720p, phụ đề tự động faster-whisper small local: video 4,10 giây, khoảng 41 giây xử lý. Whisper nhận dạng được câu tiếng Việt trong mẫu.
- Cả hai checkpoint TorchScript đã nạp; checkpoint thường chạy forward với tensor mẫu. SHA-256 của ba model được đối chiếu trong mã/script tải.
- Điều chỉnh bố cục: GAN với zoom 140%, dịch lên 30 ở khung dọc 720×1280 và zoom 80%, dịch xuống 25 ở khung ngang 1280×720 đều xuất video hợp lệ. Đã xem frame đầu của mẫu dọc, thấy ảnh nhân vật dịch lên với nền mờ; chưa đánh giá toàn bộ video.
- GUI test kiểm tra giá trị zoom/vị trí độc lập theo tỷ lệ ngang và dọc, reset về 100%/giữa.
- Bản onedir `dist/VoicetoVideo/VoicetoVideo.exe` build trên Windows 11 và khởi chạy được. Đã quan sát cửa sổ thật qua Windows UI Automation; giao diện hiển thị các thanh zoom/vị trí và nút tạo bị khóa khi chưa đủ dữ liệu. Shortcut Desktop/Start Menu đã trỏ đúng file chạy. Chưa chạy render bằng thao tác chuột từ bản exe.
- Sửa lỗi `AttributeError: 'NoneType' object has no attribute 'write'` khi bản GUI không có `stdout/stderr`; tiến trình AI nay cấp luồng ghi hợp lệ. Có test tái hiện trường hợp `stdout/stderr=None`.
- Bố cục hai cột và các ô nhập số đã khởi tạo và quan sát trong cửa sổ Windows. Test kiểm tra đồng bộ slider/ô số và giá trị riêng theo khung ngang/dọc.
- Mẫu 1,5 giây khung dọc 720×1280 với zoom 120%, dịch lên 20 và sang phải 40 đã xuất, qua FFprobe.

## Lỗi đã sửa

- PyAV 14 không có wheel phù hợp và thiếu C++ Build Tools: cài PyAV 17, giữ cảnh báo ràng buộc của `lipsync`.
- `-vsync` không được FFmpeg 9 nhận: chuyển sang `-fps_mode cfr`.
- Đường dẫn tương đối mất hiệu lực khi FFmpeg chạy trong thư mục tạm: đổi sang đường dẫn tuyệt đối.
- Di chuyển file tạm giữa ổ C và E bằng `replace` thất bại: copy sang file `.partial` cùng ổ rồi đổi tên.
- Qt hủy widget chọn file trước khi thêm vào layout: giữ tham chiếu widget.

## Chưa xác minh

- Test video 10 giây, 30 giây, 1 phút, 5 phút; RAM và khả năng xử lý video dài.
- Ảnh PNG, video MOV/AVI/MKV, nguồn video ngắn cần lặp, chất lượng khung nối.
- Khẩu hình bằng mắt, audio bằng tai, chất lượng phụ đề và vùng an toàn trên điện thoại.
- Hủy giữa lúc suy luận và FFmpeg, lỗi hết dung lượng/thiếu quyền, reset GUI sau hộp thoại thành công trên màn hình thật.
- Intel Arc/OpenVINO/NPU; bản hiện tại dùng CPU.
- Bản portable trên máy khác, bộ cài/gỡ cài đặt và render từ GUI bản exe.

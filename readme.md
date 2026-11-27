# VoicetoVideo v1.0.0 (đang phát triển)

Ứng dụng Windows tạo video nhân vật nói từ văn bản hoặc giọng ghi âm. Giao diện tiếng Việt, ba chế độ đầu vào, hai checkpoint Wav2Lip, phụ đề tùy chọn. Ba chế độ đã chạy thử với clip ngắn trên Windows 11; bản này vẫn cần kiểm thử video dài, chất lượng khẩu hình và bản portable trên máy khác.

Trong **Thiết lập video**, chọn khung ngang hoặc dọc rồi dùng hai thanh **Phóng to / thu nhỏ** và **Vị trí nhân vật**. Mỗi tỷ lệ khung hình ghi nhớ bố cục riêng trong tác vụ hiện tại. Khung xem trước cập nhật theo thanh trượt; video xuất dùng nền mờ để lấp vùng trống khi thu nhỏ hoặc dịch ảnh.

## Cài và chạy

Yêu cầu Windows 11, Python 3.12, FFmpeg và FFprobe. Chạy `scripts/setup.ps1`, rồi `scripts/download_models.ps1` để lấy ba model Wav2Lip, GAN, S3FD và cache faster-whisper small. Sau đó chạy `scripts/start.ps1`. Chế độ văn bản dùng Edge-TTS và cần Internet. Chế độ ghi âm và SRT chạy offline sau khi đã cài models.

Checkpoint Wav2Lip được lấy từ [repository chính thức](https://github.com/Rudrabha/Wav2Lip) và được xác minh SHA-256 trước khi sử dụng. Không dùng `Weights/demo.pth` trong repo gốc vì file chỉ có 2 byte. Checkpoint hiện là TorchScript, nên loader dùng `torch.jit.load` thay vì loader cũ trong `lipsync`.

`scripts/build.ps1` tạo bản onedir tại `dist/VoicetoVideo/VoicetoVideo.exe`. Đặt thư mục `models/wav2lip` cạnh file exe. Bản build không bao gồm checkpoint và chưa được thử trên máy khác. Để gỡ bản nguồn, xóa thư mục dự án sau khi sao lưu video cá nhân đã xuất; bản hiện tại chưa có trình gỡ cài đặt.

## Giới hạn hiện tại

- CPU là backend được cấu hình; Intel GPU/NPU chưa được benchmark.
- `lipsync` 0.1.0 ràng buộc PyAV <15; trên Python 3.12 bản đó cần biên dịch và thiếu Build Tools, nên dùng PyAV 17 wheel. Import và các clip ngắn đã chạy, nhưng `pip check` còn báo xung đột version.
- `lipsync` nạp toàn bộ frame video vào RAM; video dài 1–5 phút chưa được thử và có thể tốn nhiều bộ nhớ.
- Chất lượng khẩu hình và các điểm nối video lặp chưa được người kiểm tra bằng mắt/nghe đánh giá.
- Không sử dụng thương mại khi chưa có quyền phù hợp đối với checkpoint và mã bên thứ ba. Xem [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).

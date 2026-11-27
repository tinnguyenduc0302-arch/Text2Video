import threading
import time
from pathlib import Path

from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QApplication, QButtonGroup, QCheckBox, QComboBox, QFileDialog,
    QFormLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QMessageBox,
    QProgressBar, QPushButton, QRadioButton, QScrollArea, QTextEdit, QVBoxLayout, QWidget)

from app.config.defaults import VOICES
from app.core.pipeline import RenderRequest, render
from app.core.validation import AUDIO, IMAGE, VIDEO, parse_srt, valid_file, validate_folder

class RenderWorker(QThread):
    progress = Signal(str, int)
    succeeded = Signal(object)
    failed = Signal(str)

    def __init__(self, request):
        super().__init__()
        self.request = request
        self.cancel_event = threading.Event()

    def run(self):
        try:
            result = render(self.request, lambda label, value: self.progress.emit(label, value), self.cancel_event)
            if self.cancel_event.is_set():
                self.failed.emit("Đã hủy tác vụ.")
            else:
                self.succeeded.emit(result)
        except Exception as exc:
            self.failed.emit(str(exc))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VoicetoVideo 1.0.0")
        self.resize(900, 780)
        self.worker = None
        self.lockables = []
        self.started = None
        self.setStyleSheet("QMainWindow{background:#f5f8fa} QGroupBox{background:white;border:1px solid #dce5e9;border-radius:10px;margin-top:12px;padding:14px;font-weight:600} QGroupBox::title{subcontrol-origin:margin;left:18px;padding:0 4px;color:#12475b} QPushButton{background:#087c91;color:white;border:0;border-radius:6px;padding:8px 13px} QPushButton:disabled{background:#b8c5ca} QLineEdit,QTextEdit,QComboBox{border:1px solid #cbd9df;border-radius:5px;padding:6px;background:white}")
        root = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(14)
        title = QLabel("VoicetoVideo")
        title.setStyleSheet("font-size:25px;font-weight:700;color:#12475b")
        layout.addWidget(title)
        modes = QGroupBox("1. Chế độ tạo video")
        row = QHBoxLayout(modes)
        self.mode_buttons = [QRadioButton("Văn bản + ảnh/video"), QRadioButton("Ghi âm + ảnh/video"), QRadioButton("Ghi âm + SRT + ảnh/video")]
        self.lockables.extend(self.mode_buttons)
        self.mode_group = QButtonGroup(self)
        for i, button in enumerate(self.mode_buttons, 1):
            row.addWidget(button)
            self.mode_group.addButton(button, i)
            button.toggled.connect(self.update_mode)
        layout.addWidget(modes)
        inputs = QGroupBox("2. Dữ liệu đầu vào")
        form = QFormLayout(inputs)
        self.preview = QLabel("Chưa chọn nhân vật")
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setMinimumHeight(140)
        self.preview.setStyleSheet("background:#eaf1f4;border-radius:6px;color:#54717d")
        form.addRow(self.preview)
        self.face, face_button, face_row = self.file_row("Chọn ảnh/video", "Hình ảnh và video (*.jpg *.jpeg *.png *.mp4 *.mov *.avi *.mkv)")
        face_button.clicked.connect(self.refresh_preview)
        form.addRow("Nhân vật", face_row)
        self.text = QTextEdit()
        self.lockables.append(self.text)
        self.text.setPlaceholderText("Nhập văn bản để tạo giọng nói. Edge-TTS cần Internet.")
        self.text.setMaximumHeight(105)
        self.text.textChanged.connect(self.validate_form)
        self.text_label = QLabel("Văn bản")
        form.addRow(self.text_label, self.text)
        self.voice = QComboBox()
        self.lockables.append(self.voice)
        for label, code in VOICES.items():
            self.voice.addItem(label, code)
        self.voice_label = QLabel("Giọng đọc")
        form.addRow(self.voice_label, self.voice)
        self.audio, _, audio_row = self.file_row("Chọn WAV/MP3", "Âm thanh (*.wav *.mp3)")
        self.audio_label = QLabel("File ghi âm")
        form.addRow(self.audio_label, audio_row)
        self.srt, _, srt_row = self.file_row("Chọn SRT", "Phụ đề (*.srt)")
        self.srt_label = QLabel("File SRT")
        form.addRow(self.srt_label, srt_row)
        layout.addWidget(inputs)
        settings = QGroupBox("3. Thiết lập video")
        sform = QFormLayout(settings)
        self.model = QComboBox()
        self.lockables.append(self.model)
        self.model.addItem("Wav2Lip GAN (Vùng miệng sắc nét hơn, khẩu hình có thể kém chính xác hơn một chút)", "gan")
        self.model.addItem("Wav2Lip (Khẩu hình chính xác hơn, vùng miệng có thể hơi mờ)", "wav2lip")
        sform.addRow("Mô hình AI", self.model)
        self.quality = QComboBox()
        self.lockables.append(self.quality)
        self.quality.addItems(["Full HD 1080p", "HD 720p"])
        sform.addRow("Độ phân giải", self.quality)
        self.aspect = QComboBox()
        self.lockables.append(self.aspect)
        self.aspect.addItems(["▭  Khung ngang 16:9 (YouTube video dài)", "▯  Khung dọc 9:16 (TikTok, Facebook Reels, Instagram Reels, YouTube Shorts)"])
        self.aspect.currentIndexChanged.connect(self.update_preview_shape)
        sform.addRow("Khung hình", self.aspect)
        self.subtitles = QCheckBox("Ghép phụ đề vào video")
        self.lockables.append(self.subtitles)
        sform.addRow(self.subtitles)
        layout.addWidget(settings)
        export = QGroupBox("4. Xuất video")
        eform = QFormLayout(export)
        self.folder = QLineEdit()
        self.folder.setReadOnly(True)
        choose_folder = QPushButton("Chọn thư mục")
        self.lockables.append(choose_folder)
        choose_folder.clicked.connect(self.select_folder)
        folder_row = QWidget()
        folder_layout = QHBoxLayout(folder_row)
        folder_layout.setContentsMargins(0, 0, 0, 0)
        folder_layout.addWidget(self.folder)
        folder_layout.addWidget(choose_folder)
        eform.addRow("Thư mục lưu video", folder_row)
        self.create = QPushButton("TẠO VIDEO")
        self.create.clicked.connect(self.start_render)
        self.cancel = QPushButton("HỦY")
        self.cancel.clicked.connect(self.cancel_render)
        self.cancel.setEnabled(False)
        buttons = QWidget()
        brow = QHBoxLayout(buttons)
        brow.addWidget(self.create)
        brow.addWidget(self.cancel)
        eform.addRow(buttons)
        self.progress = QProgressBar()
        eform.addRow(self.progress)
        self.status = QLabel("Sẵn sàng")
        eform.addRow(self.status)
        layout.addWidget(export)
        scroll.setWidget(content)
        outer = QVBoxLayout(root)
        outer.addWidget(scroll)
        self.setCentralWidget(root)
        self.mode_buttons[0].setChecked(True)
        self.update_preview_shape()
        self.validate_form()

    def file_row(self, label, filter_text):
        field = QLineEdit()
        field.setReadOnly(True)
        field.textChanged.connect(self.validate_form)
        button = QPushButton(label)
        self.lockables.append(button)
        button.clicked.connect(lambda: self.select_file(field, filter_text))
        widget = QWidget()
        row = QHBoxLayout(widget)
        row.setContentsMargins(0, 0, 0, 0)
        row.addWidget(field)
        row.addWidget(button)
        return field, button, widget

    def select_file(self, field, filter_text):
        path, _ = QFileDialog.getOpenFileName(self, "Chọn file", "", filter_text)
        if path:
            field.setText(path)

    def select_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Chọn thư mục lưu video")
        if path:
            self.folder.setText(path)
            self.validate_form()

    def refresh_preview(self):
        path = Path(self.face.text())
        if path.suffix.lower() in IMAGE and path.exists():
            image = QPixmap(str(path))
            if image.isNull():
                self.preview.setText("Không đọc được ảnh")
            else:
                self.preview.setPixmap(image.scaled(self.preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        elif path.exists():
            self.preview.setText(f"Video: {path.name}")

    def update_preview_shape(self):
        self.preview.setMaximumWidth(250 if self.aspect.currentIndex() else 500)

    def update_mode(self):
        mode = self.mode_group.checkedId()
        for widget in (self.text, self.text_label, self.voice, self.voice_label):
            widget.setVisible(mode == 1)
        for widget in (self.audio.parentWidget(), self.audio_label):
            widget.setVisible(mode in (2, 3))
        for widget in (self.srt.parentWidget(), self.srt_label):
            widget.setVisible(mode == 3)
        self.validate_form()

    def validate_form(self):
        if not hasattr(self, "create") or (self.worker and self.worker.isRunning()):
            return
        mode = self.mode_group.checkedId()
        valid = bool(self.face.text() and Path(self.face.text()).is_file() and self.folder.text() and Path(self.folder.text()).is_dir())
        valid &= bool(self.text.toPlainText().strip()) if mode == 1 else bool(self.audio.text() and Path(self.audio.text()).is_file())
        if mode == 3:
            valid &= bool(self.srt.text() and Path(self.srt.text()).is_file())
        self.create.setEnabled(valid)

    def start_render(self):
        try:
            valid_file(self.face.text(), IMAGE | VIDEO)
            validate_folder(self.folder.text())
            if self.mode_group.checkedId() in (2, 3):
                valid_file(self.audio.text(), AUDIO)
            if self.mode_group.checkedId() == 3:
                parse_srt(self.srt.text())
        except Exception as exc:
            QMessageBox.warning(self, "Dữ liệu không hợp lệ", str(exc))
            return
        request = RenderRequest(self.mode_group.checkedId(), self.face.text(), self.folder.text(), self.text.toPlainText(), self.voice.currentData(), self.audio.text(), self.srt.text(), self.model.currentData(), "1080p" if self.quality.currentIndex() == 0 else "720p", "16:9" if self.aspect.currentIndex() == 0 else "9:16", self.subtitles.isChecked())
        self.worker = RenderWorker(request)
        self.worker.progress.connect(self.on_progress)
        self.worker.succeeded.connect(self.on_success)
        self.worker.failed.connect(self.on_failure)
        self.started = time.monotonic()
        for widget in self.lockables:
            widget.setEnabled(False)
        self.create.setEnabled(False)
        self.cancel.setEnabled(True)
        self.worker.start()

    def on_progress(self, label, value):
        if label == "Đang đồng bộ khẩu hình":
            self.progress.setRange(0, 0)
        else:
            if self.progress.maximum() == 0:
                self.progress.setRange(0, 100)
            self.progress.setValue(value)
        self.status.setText(f"{label} · {time.monotonic()-self.started:.0f}s")

    def cancel_render(self):
        if self.worker:
            self.worker.cancel_event.set()
            self.status.setText("Đang hủy tác vụ…")

    def on_failure(self, message):
        for widget in self.lockables:
            widget.setEnabled(True)
        self.cancel.setEnabled(False)
        self.status.setText("Đã hủy" if "hủy" in message else "Thất bại")
        QMessageBox.warning(self, "Không tạo được video", message)
        self.validate_form()

    def on_success(self, result):
        from PySide6.QtGui import QDesktopServices
        from PySide6.QtCore import QUrl
        path = result["path"]
        box = QMessageBox(self)
        box.setWindowTitle("TẠO VIDEO THÀNH CÔNG!")
        box.setText(f"{path.name}\n{path}\nThời lượng: {result['duration']:.1f}s\nĐộ phân giải: {result['size'][0]} × {result['size'][1]}\nDung lượng: {result['bytes']/1048576:.1f} MB\nThời gian xử lý: {result['elapsed']:.1f}s")
        open_button = box.addButton("Mở thư mục chứa video", QMessageBox.ActionRole)
        box.addButton("OK", QMessageBox.AcceptRole)
        box.exec()
        if box.clickedButton() == open_button:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(path.parent)))
        self.reset()

    def reset(self):
        for widget in self.lockables:
            widget.setEnabled(True)
        self.mode_buttons[0].setChecked(True)
        for field in (self.face, self.audio, self.srt, self.folder):
            field.clear()
        self.text.clear()
        self.preview.clear()
        self.preview.setText("Chưa chọn nhân vật")
        self.voice.setCurrentIndex(0)
        self.model.setCurrentIndex(0)
        self.quality.setCurrentIndex(0)
        self.aspect.setCurrentIndex(0)
        self.subtitles.setChecked(False)
        self.progress.setValue(0)
        self.status.setText("Sẵn sàng")
        self.cancel.setEnabled(False)
        self.worker = None
        self.validate_form()

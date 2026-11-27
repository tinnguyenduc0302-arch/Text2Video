from PySide6.QtWidgets import QApplication
from app.ui.main_window import MainWindow

def test_modes_and_reset(monkeypatch):
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    assert window.mode_group.checkedId() == 1
    assert not window.create.isEnabled()
    window.mode_buttons[2].setChecked(True)
    assert not window.srt.isHidden()
    assert window.text.isHidden()
    window.text.setPlainText('Xin chào')
    window.reset()
    assert window.mode_group.checkedId() == 1
    assert window.text.toPlainText() == ''
    assert window.model.currentData() == 'gan'
    assert not window.create.isEnabled()
    window.close()

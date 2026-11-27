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
    window.zoom.setValue(135)
    window.vertical.setValue(-25)
    window.aspect.setCurrentIndex(1)
    assert (window.zoom.value(), window.vertical.value()) == (100, 0)
    window.zoom.setValue(75)
    window.aspect.setCurrentIndex(0)
    assert (window.zoom.value(), window.vertical.value()) == (135, -25)
    window.text.setPlainText('Xin chào')
    window.reset()
    assert window.mode_group.checkedId() == 1
    assert window.text.toPlainText() == ''
    assert window.model.currentData() == 'gan'
    assert (window.zoom.value(), window.vertical.value()) == (100, 0)
    assert not window.create.isEnabled()
    window.close()

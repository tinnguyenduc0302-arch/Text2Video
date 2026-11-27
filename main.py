import sys
import multiprocessing
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from pathlib import Path
from app.config.defaults import ROOT
from app.ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    icon = ROOT / "assets" / "icons" / "voicetovideo.ico"
    if icon.exists():
        app.setWindowIcon(QIcon(str(icon)))
    window = MainWindow()
    window.show()
    return app.exec()

if __name__ == "__main__":
    multiprocessing.freeze_support()
    raise SystemExit(main())

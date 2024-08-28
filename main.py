from PySide6.QtWidgets import QApplication
from package.ui.main_widget import MainWidget
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWidget()
    window.show()
    sys.exit(app.exec())
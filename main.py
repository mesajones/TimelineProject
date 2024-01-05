import sys

from PyQt6.QtWidgets import QApplication

from gui.gui import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Create and Show Main Window
    window = MainWindow()
    window.show()

    # Run the application
    sys.exit(app.exec())

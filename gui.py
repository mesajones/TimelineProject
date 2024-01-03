import sys
from PyQt6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QMainWindow
from PyQt6.QtGui import QPen, QBrush
from PyQt6.QtCore import Qt, QRectF


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create a QGraphicsScene
        self.scene = QGraphicsScene()

        # Create items
        self.scene.addRect(QRectF(0, 0, 100, 100), QPen(Qt.GlobalColor.black), QBrush(Qt.GlobalColor.green))
        self.scene.addEllipse(QRectF(100, 100, 100, 100), QPen(Qt.GlobalColor.red), QBrush(Qt.GlobalColor.blue))

        # Create a QGraphicsView
        self.view = QGraphicsView(self.scene, self)
        self.setCentralWidget(self.view)

        # Window Title
        self.setWindowTitle("QGraphics Example")


# Application Instance
app = QApplication(sys.argv)

# Create and Show Main Window
window = MainWindow()
window.show()

# Run the application
sys.exit(app.exec())

import sys
from PyQt6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsItem, QMainWindow
from PyQt6.QtGui import QPen, QBrush, QColor, QFont
from PyQt6.QtCore import Qt, QRectF, QSizeF

from config.settings import DEFAULT_FONT, FOREGROUND, BACKGROUND, ACCENT, HALF_ACCENT, GREEN,  BLUE, ORANGE


foreground_brush = QBrush(QColor(FOREGROUND))
background_brush = QBrush(QColor(BACKGROUND))
background_brush_translucent = QBrush(QColor(BACKGROUND))
accent_brush = QBrush(QColor(ACCENT))
half_accent_brush = QBrush(QColor(HALF_ACCENT))

foreground_pen = QPen(QColor(FOREGROUND))
background_pen = QPen(QColor(BACKGROUND))
accent_pen = QPen(QColor(ACCENT))
half_accent_pen = QPen(QColor(HALF_ACCENT))

green_pen = QPen(QColor(GREEN))
blue_pen = QPen(QColor(BLUE))
orange_pen = QPen(QColor(ORANGE))


class BaseCueGraphic(QGraphicsItem):
    def __init__(self):
        super().__init__()
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setAcceptHoverEvents(True)

        self.text = 'Hello, world!'
        self.title_font = QFont(DEFAULT_FONT, 12)

        self.width, self.height = 200, 100
        self.resizable = True

        self.outline_pen = accent_pen

        self.rect = QRectF(0, 0, self.width, self.height)  # Initial size
        self.handleSize = 4.0  # Size of the resize handle
        self.resizing = False
        self.handle_hover = False

    def boundingRect(self):
        return self.rect.adjusted(-self.handleSize, -self.handleSize, self.handleSize, self.handleSize)

    def paint(self, painter, option, widget=None):
        if self.isSelected():
            self.outline_pen.setWidth(2)
        else:
            self.outline_pen.setWidth(1)
        painter.setPen(self.outline_pen)
        painter.setBrush(background_brush)
        painter.drawRect(self.rect)

        painter.setBrush(half_accent_brush)
        painter.drawRect(self.titleBarRect())
        painter.setFont(self.title_font)
        painter.setPen(foreground_pen)
        painter.drawText(self.titleTextBound(), self.text)

        # Draw a resize handle
        if self.handle_hover:
            painter.setPen(background_pen)
            painter.setBrush(accent_brush)
            painter.drawRect(self.resizeHandleRect())

    def resizeHandleBound(self):
        return QRectF(self.rect.right() - self.handleSize / 2,
                      self.rect.top() - self.handleSize / 2,
                      self.handleSize, self.rect.bottom() + self.handleSize)

    def resizeHandleRect(self):
        return QRectF(self.rect.right() - self.handleSize / 2,
                      self.rect.top() - 1,
                      self.handleSize, self.rect.bottom() + 2)

    def titleBarRect(self):
        return QRectF(self.rect.left(), self.rect.top(),
                      self.rect.width(), 16)

    def titleTextBound(self):
        return QRectF(self.titleBarRect().left() + 2, self.titleBarRect().top(),
                      self.titleBarRect().width(), self.titleBarRect().height())

    def mousePressEvent(self, event):
        if event.pos() in self.resizeHandleBound() and self.resizable:
            self.resizing = True
        else:
            self.resizing = False
        super().mousePressEvent(event)

    def hoverMoveEvent(self, event):
        if self.resizeHandleBound().contains(event.pos()):
            self.handle_hover = True
            self.update()  # Update the item to repaint with the handle
        else:
            self.handle_hover = False
            self.update()

    def hoverLeaveEvent(self, event):
        self.handle_hover = False
        self.update()

    def mouseMoveEvent(self, event):
        if self.resizing and self.resizable:
            self.resizeItem(event.pos())
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.resizing = False
        super().mouseReleaseEvent(event)

    def resizeItem(self, newPos):
        minimum_width = 100
        self.width = minimum_width if not newPos.x() - self.rect.left() >= minimum_width else newPos.x() - self.rect.left()
        self.rect.setSize(QSizeF(self.width, self.height))
        self.update()


class TimelineScene(QGraphicsScene):
    pass


class TimelineView(QGraphicsView):
    pass


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create a QGraphicsScene
        self.scene = QGraphicsScene()
        self.resize(800, 600)

        cue_graphic = BaseCueGraphic()

        # Create items
        self.scene.addItem(cue_graphic)

        # Create a QGraphicsView
        self.view = QGraphicsView(self.scene, self)
        self.setCentralWidget(self.view)

        # Window Title
        self.setWindowTitle("")


# Application Instance
app = QApplication(sys.argv)

# Create and Show Main Window
window = MainWindow()
window.show()

# Run the application
sys.exit(app.exec())

from PyQt6.QtCore import QRectF, QSizeF
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QGraphicsItem

from config.settings import DEFAULT_FONT
from gui.brushpen import accent_pen, background_brush, half_accent_brush, foreground_pen, background_pen, accent_brush


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

    def adjustForZoom(self, zoom_change):
        self.rect.setWidth(self.rect.width() * zoom_change)
        self.update()  # Redraw the item

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


class EOSCueGraphic(BaseCueGraphic):
    pass


class QLabCueGraphic(BaseCueGraphic):
    pass

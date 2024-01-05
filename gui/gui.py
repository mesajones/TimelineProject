from PyQt6.QtCore import QRectF, QPointF, Qt
from PyQt6.QtGui import QPainter, QWheelEvent
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsView, QMainWindow, QGraphicsRectItem, QApplication

from gui.brushpen import accent_pen, background_brush, half_accent_pen, foreground_pen
from gui.cuegraphics import BaseCueGraphic
from gui.ruler import RulerGraphic, RulerBackground

from config.settings import TIMECODE_FPS

from utils import timecode_to_position, position_to_timecode, timecode_to_float


class TimelineScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)


class TimelineView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHints(QPainter.RenderHint.Antialiasing)
        self.ruler_graphic = RulerGraphic(self)
        self.scene().addItem(self.ruler_graphic)
        self.base_cue_graphic = BaseCueGraphic()
        self.scene().addItem(self.base_cue_graphic)

    def scrollContentsBy(self, dx, dy):
        super().scrollContentsBy(dx, dy)
        self.ruler_graphic.updateVisibleMarks()

    def wheelEvent(self, event):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.KeyboardModifier.ControlModifier:
            factor = 1.1 if event.angleDelta().y() > 0 else 0.9
            self.ruler_graphic.scaleZoomFactor(factor)
            self.adjustScrollBars(self.ruler_graphic.zoom_factor)
        else:
            super().wheelEvent(event)

    def adjustScrollBars(self, zoom_factor):
        # Calculate the maximum value for the scroll bars
        max_scroll_value = self.calculateMaxScrollValue(zoom_factor)
        self.horizontalScrollBar().setMaximum(max_scroll_value)

    def calculateMaxScrollValue(self, zoom_factor):
        # Return a value based on zoom_factor
        # This is an example; you'll need to tailor it to your application
        return int(1000 * (1 / zoom_factor))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.resize(800, 600)

        self.timelineScene = TimelineScene()
        self.timelineView = TimelineView(self.timelineScene)
        self.setCentralWidget(self.timelineView)

        # Window Title
        self.setWindowTitle("Timeline App")

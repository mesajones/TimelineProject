from dataclasses import dataclass

from PyQt6.QtCore import QRectF, QPointF
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsRectItem

from config.settings import DEFAULT_FONT
from gui.brushpen import accent_pen, background_brush, half_accent_brush, foreground_pen, background_pen, accent_brush, \
    orange_brush, half_accent_pen
from utils import float_to_timecode


class RulerBackground(QGraphicsItem):
    def __init__(self, width, height):
        super().__init__()
        self.width = width
        self.height = height

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)

    def paint(self, painter, option, widget=None):
        painter.setBrush(orange_brush)
        painter.drawRect(self.boundingRect())


class RulerGraphic(QGraphicsItem):
    def __init__(self, viewport):
        super().__init__()
        self.zoom_factor = 0.1
        self.init_length = 90000
        self.length = int(self.init_length * self.zoom_factor)
        self.height = viewport.height()
        self.ruler_height = 60
        self.background_height = self.height - self.ruler_height
        self.setPos(0, 0)
        self.mark_font = QFont(DEFAULT_FONT, 10)

        self.outline_pen = accent_pen
        self.outline_pen.setWidth(1)

        self.all_marks = self.generate_marks()
        self.visible_marks = {}

    def get_visible_range(self):
        # Assuming self.scene() returns the QGraphicsScene this item belongs to
        # and self.scene().views() returns the list of QGraphicsView viewing the scene
        view = self.scene().views()[0]  # Assuming there's only one view

        # Getting the visible part of the scene in the view
        visible_rect = view.mapToScene(view.viewport().geometry()).boundingRect()

        # Start and end x-coordinates of the visible area
        visible_start = visible_rect.left() / self.zoom_factor
        visible_end = visible_rect.right() / self.zoom_factor

        return visible_start, visible_end

    def generate_marks(self):
        total_frames = 30 * 3600
        marks = {}
        for frame in range(total_frames):
            x_position = self.calculate_position(frame)
            marks[frame] = x_position
        return marks

    def calculate_position(self, frame_number):
        # Calculate the x-coordinate for a given frame number
        position = (frame_number / (30 * 3600)) * self.init_length
        return position

    def updateVisibleMarks(self):
        self.visible_marks = self.calculateVisibleMarks()
        self.update()

    def calculateVisibleMarks(self):
        visible_start, visible_end = self.get_visible_range()
        return {mark: pos * self.zoom_factor for mark, pos in self.all_marks.items() if visible_start - 10 <= pos <= visible_end + 10}

    def boundingRect(self):
        return QRectF(0, 0, self.length, self.background_height + self.ruler_height)

    def rulerRect(self):
        return QRectF(0, 0, self.length, self.ruler_height)

    def backgroundRect(self):
        return QRectF(0, 0, self.length, self.background_height)

    def scaleZoomFactor(self, factor):
        new_zoom_factor = self.zoom_factor * factor
        self.zoom_factor = max(0.1, min(30.0, new_zoom_factor))
        self.length = int(self.init_length * self.zoom_factor)
        print(self.zoom_factor, self.length)
        self.updateVisibleMarks()
        self.update()

    def paint(self, painter, option, widget=None):
        painter.setPen(self.outline_pen)
        painter.setBrush(background_brush)
        painter.drawRect(self.boundingRect())
        painter.drawRect(self.rulerRect())

        frame_threshold = self.zoom_factor > 8.0

        for mark, pos in self.visible_marks.items():
            height = self.ruler_height // 5
            frame = True
            second = False
            if mark % (30 * 60 * 60) == 0:
                height = self.ruler_height - 20
                frame = False
            elif mark % (30 * 60) == 0:
                height = self.ruler_height - 20
                frame = False
            elif mark % 30 == 0:
                frame = False
                number = mark / 30
                if self.zoom_factor < 0.2 and not number % 15 == 0:
                    continue
                if 0.2 <= self.zoom_factor < 1.0 and not number % 5 == 0:
                    continue
                if self.zoom_factor < 4.0:
                    second = True
                height = self.ruler_height - 40

            elif frame_threshold:
                if self.zoom_factor < 12.0 and 0 < (mark % 30) % 5 <= 5:
                    continue
                if 12.0 <= self.zoom_factor < 16.0 and not (mark % 30) % 3 == 0:
                    continue
                if 16.0 <= self.zoom_factor < 20.0 and (mark % 30) % 2 == 1:
                    continue
            else:
                continue
            self.draw_mark(painter, mark, pos, height, frame, second)

    def draw_mark(self, painter, mark, mark_pos, height, frame=False, second=False):
        painter.setPen(accent_pen)
        text = float_to_timecode(mark / 30)
        text_y = 14
        if frame:
            text = str(mark % 30)
            text_y = 45
        if second:
            text = str(int((mark / 30) % 60))
        if mark % 30 == 0 and not mark % (30 * 60) == 0:
            text_y = 30
        number_pos = mark_pos - (len(text) * 7) / 2
        painter.drawLine(int(mark_pos), self.ruler_height - height + 2, int(mark_pos), self.ruler_height)
        if frame or second:
            painter.setPen(half_accent_pen)
        if mark % 30 == 0:
            painter.setPen(accent_pen)
        painter.drawLine(int(mark_pos), self.ruler_height, int(mark_pos), self.height)
        painter.setPen(foreground_pen)
        painter.drawText(QPointF(int(number_pos), text_y), text)


class BackgroundGrid(QGraphicsRectItem):
    pass

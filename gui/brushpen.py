from PyQt6.QtGui import QBrush, QColor, QPen

from config.settings import FOREGROUND, BACKGROUND, ACCENT, HALF_ACCENT, GREEN, BLUE, ORANGE


foreground_brush = QBrush(QColor(FOREGROUND))
background_brush = QBrush(QColor(BACKGROUND))
background_brush_translucent = QBrush(QColor(BACKGROUND))
accent_brush = QBrush(QColor(ACCENT))
half_accent_brush = QBrush(QColor(HALF_ACCENT))

green_brush = QBrush(QColor(GREEN))
blue_brush = QBrush(QColor(BLUE))
orange_brush = QBrush(QColor(ORANGE))

foreground_pen = QPen(QColor(FOREGROUND))
background_pen = QPen(QColor(BACKGROUND))
accent_pen = QPen(QColor(ACCENT))
half_accent_pen = QPen(QColor(HALF_ACCENT))

green_pen = QPen(QColor(GREEN))
blue_pen = QPen(QColor(BLUE))
orange_pen = QPen(QColor(ORANGE))
"""Reusable widgets shared by the pages."""

from datetime import date, timedelta

from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen, QLinearGradient
from PySide6.QtWidgets import QFrame, QLabel, QSizePolicy, QVBoxLayout, QWidget

import engine
import theme


def make_card():
    card = QFrame()
    card.setObjectName("card")
    return card


def field_label(text):
    label = QLabel(text)
    label.setObjectName("fieldLabel")
    return label


class StatTile(QFrame):
    def __init__(self, name, unit, tone):
        super().__init__()
        self.setObjectName("tile")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(2)

        name_label = QLabel(name.upper())
        name_label.setObjectName("tileName")
        name_label.setProperty("tone", tone)
        self.value_label = QLabel("--")
        self.value_label.setObjectName("tileValue")
        self.unit_label = QLabel(unit)
        self.unit_label.setObjectName("tileUnit")

        layout.addWidget(name_label)
        layout.addWidget(self.value_label)
        layout.addWidget(self.unit_label)

    def set_value(self, text, unit=None):
        self.value_label.setText(text)
        if unit is not None:
            self.unit_label.setText(unit)


class MacroBar(QWidget):
    """Thin stacked bar showing the protein / carbs / fat calorie split."""

    def __init__(self):
        super().__init__()
        self.setFixedHeight(10)
        self.ratio = None

    def set_ratio(self, ratio):
        self.ratio = ratio
        self.update()

    def paintEvent(self, _event):
        if not self.ratio:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        clip = QPainterPath()
        clip.addRoundedRect(self.rect(), 5, 5)
        painter.setClipPath(clip)
        x = 0.0
        for fraction, key in zip(self.ratio, ("protein", "carbs", "fat")):
            w = self.width() * fraction
            painter.fillRect(int(x), 0, int(w) + 1, self.height(), QColor(theme.c[key]))
            x += w


class ProjectionChart(QWidget):
    """Line chart of projected weight over time, with a dashed target line."""

    LEFT, RIGHT, TOP, BOTTOM = 52, 16, 12, 28

    def __init__(self):
        super().__init__()
        self.setMinimumHeight(200)
        self.points = []
        self.target_kg = None
        self.imperial = False
        self.start = date.today()

    def set_data(self, points, target_kg, imperial):
        self.points = points
        self.target_kg = target_kg
        self.imperial = imperial
        self.start = date.today()
        self.update()

    def _disp(self, kg):
        return kg * engine.LB_PER_KG if self.imperial else kg

    def paintEvent(self, _event):
        if len(self.points) < 2:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        plot = QRectF(self.LEFT, self.TOP,
                      self.width() - self.LEFT - self.RIGHT,
                      self.height() - self.TOP - self.BOTTOM)
        weights = [self._disp(w) for _, w in self.points]
        lo, hi = min(weights), max(weights)
        pad = max((hi - lo) * 0.15, 1.0)
        lo, hi = lo - pad, hi + pad
        max_week = self.points[-1][0] or 1

        def to_xy(week, value):
            x = plot.left() + plot.width() * week / max_week
            y = plot.bottom() - plot.height() * (value - lo) / (hi - lo)
            return QPointF(x, y)

        muted = QColor(theme.c["muted"])
        grid = QColor(theme.c["border"])
        accent = QColor(theme.c["accent"])

        # Gridlines + y labels
        p.setFont(self.font())
        for i in range(5):
            value = lo + (hi - lo) * i / 4
            y = to_xy(0, value).y()
            p.setPen(QPen(grid, 1))
            p.drawLine(QPointF(plot.left(), y), QPointF(plot.right(), y))
            p.setPen(muted)
            p.drawText(QRectF(0, y - 10, self.LEFT - 8, 20),
                       Qt.AlignRight | Qt.AlignVCenter, f"{value:.0f}")

        # X labels as calendar dates
        for i in range(5):
            week = max_week * i / 4
            when = self.start + timedelta(weeks=week)
            pt = to_xy(week, lo)
            align = Qt.AlignHCenter
            rect = QRectF(pt.x() - 40, plot.bottom() + 6, 80, 18)
            p.setPen(muted)
            p.drawText(rect, align | Qt.AlignVCenter, f"{when:%b} {when.day}")

        # Target line
        if self.target_kg is not None:
            ty = to_xy(0, self._disp(self.target_kg)).y()
            p.setPen(QPen(muted, 1, Qt.DashLine))
            p.drawLine(QPointF(plot.left(), ty), QPointF(plot.right(), ty))

        # Area + line
        coords = [to_xy(w, self._disp(kg)) for w, kg in self.points]
        line = QPainterPath(coords[0])
        for pt in coords[1:]:
            line.lineTo(pt)
        area = QPainterPath(line)
        area.lineTo(coords[-1].x(), plot.bottom())
        area.lineTo(coords[0].x(), plot.bottom())
        area.closeSubpath()
        fill = QLinearGradient(0, plot.top(), 0, plot.bottom())
        top_c = QColor(accent)
        top_c.setAlpha(70)
        bot_c = QColor(accent)
        bot_c.setAlpha(0)
        fill.setColorAt(0, top_c)
        fill.setColorAt(1, bot_c)
        p.fillPath(area, fill)
        p.setPen(QPen(accent, 2.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.drawPath(line)

        # Endpoints
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(theme.c["card"]))
        for pt in (coords[0], coords[-1]):
            p.drawEllipse(pt, 6, 6)
        p.setBrush(accent)
        for pt in (coords[0], coords[-1]):
            p.drawEllipse(pt, 4, 4)

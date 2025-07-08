"""Simple color picker implemented with PySide6."""

import sys
import colorsys
import ctypes

import numpy as np
from PIL import Image
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QImage, QPainter, QPen, QColor
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QSlider,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
)


try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass


COLORS = {
    "bg_main": "#212121",
    "canvas_bg": "#212121",
    "slider_bg": "#414141",
    "slider_trough": "#515151",
    "label_fg": "#cbcbcb",
    "preview_bd": "#ffffff",
}


def gen_hue_wheel(dia: int) -> Image.Image:
    """Generate a hue circle as a PIL image."""
    data = np.zeros((dia, dia, 3), dtype=np.uint8)
    cx, cy = dia / 2, dia / 2
    r_max = dia / 2
    for y in range(dia):
        for x in range(dia):
            dx, dy = x - cx, y - cy
            r = np.hypot(dx, dy)
            if r <= r_max:
                h = (np.degrees(np.arctan2(dy, dx)) + 360) % 360 / 360
                rgb = colorsys.hsv_to_rgb(h, 1.0, 1.0)
                data[y, x] = [int(255 * c) for c in rgb]
    return Image.fromarray(data)


def gen_sv_square(size: int, hue: float, val: float) -> Image.Image:
    """Generate a saturation/value square as a PIL image."""
    data = np.zeros((size, size, 3), dtype=np.uint8)
    for i in range(size):
        for j in range(size):
            s = j / (size - 1)
            v = 1 - i / (size - 1)
            rgb = colorsys.hsv_to_rgb(hue, s, v * val)
            data[i, j] = [int(255 * c) for c in rgb]
    return Image.fromarray(data)


def pil_to_pixmap(img: Image.Image) -> QPixmap:
    """Convert PIL image to Qt pixmap."""
    img = img.convert("RGBA")
    data = img.tobytes("raw", "RGBA")
    qimg = QImage(data, img.width, img.height, QImage.Format_RGBA8888)
    return QPixmap.fromImage(qimg)


class ColorPickerWindow(QWidget):
    """Main window for the color picker."""

    def __init__(self) -> None:
        super().__init__()
        self.wheel_dia = 300
        self.wheel_r = self.wheel_dia // 2
        self.sv_size = 300
        self.cur_hue = 0.0
        self.cur_val = 1.0
        self.last_hex: str | None = None
        self._setup_ui()
        self.update_sv()

    # ------------------------------------------------------------------ UI
    def _setup_ui(self) -> None:
        self.setWindowTitle("自由取色器 - lin酱版")
        self.setFixedSize(650, 480)
        self.setStyleSheet(f"background-color:{COLORS['bg_main']}")

        main_layout = QVBoxLayout(self)
        canvas_layout = QHBoxLayout()
        main_layout.addLayout(canvas_layout)

        # hue wheel
        self.hue_base = pil_to_pixmap(gen_hue_wheel(self.wheel_dia))
        self.hue_label = QLabel()
        self.hue_label.setPixmap(self.hue_base)
        self.hue_label.setCursor(Qt.CrossCursor)
        canvas_layout.addWidget(self.hue_label)
        self.hue_label.mousePressEvent = self._on_hue_press  # type: ignore
        self.hue_label.mouseMoveEvent = self._on_hue_move  # type: ignore

        # saturation/value square
        self.sv_label = QLabel()
        self.sv_label.setCursor(Qt.CrossCursor)
        canvas_layout.addWidget(self.sv_label)
        self.sv_label.mousePressEvent = self._on_sv_press  # type: ignore
        self.sv_label.mouseMoveEvent = self._on_sv_move  # type: ignore

        # value slider
        self.val_slider = QSlider(Qt.Horizontal)
        self.val_slider.setRange(0, 100)
        self.val_slider.setValue(100)
        self.val_slider.valueChanged.connect(self._on_val_change)
        self.val_slider.setStyleSheet(
            f"background-color:{COLORS['slider_bg']}; color:{COLORS['label_fg']}"
        )
        main_layout.addWidget(self.val_slider)

        info_layout = QHBoxLayout()
        main_layout.addLayout(info_layout)

        self.preview = QLabel()
        self.preview.setFixedSize(40, 40)
        self.preview.setStyleSheet(
            f"background-color:{COLORS['bg_main']};"
            f"border:2px solid {COLORS['preview_bd']}"
        )
        info_layout.addWidget(self.preview)

        self.lbl = QLabel("点击取色")
        self.lbl.setStyleSheet(f"color:{COLORS['label_fg']}")
        info_layout.addWidget(self.lbl)
        info_layout.addStretch()

        # history window
        self.history_win = QWidget()
        self.history_win.setWindowTitle("历史取色记录")
        self.history_win.setFixedSize(360, 530)
        self.history_win.setStyleSheet(f"background-color:{COLORS['bg_main']}")
        h_layout = QVBoxLayout(self.history_win)
        self.history_lb = QListWidget()
        self.history_lb.setStyleSheet(
            f"background-color:{COLORS['slider_bg']}; color:{COLORS['label_fg']}"
        )
        h_layout.addWidget(self.history_lb)
        self.record_btn = QPushButton("记录")
        self.record_btn.setStyleSheet(
            f"background-color:{COLORS['slider_bg']}; color:{COLORS['label_fg']}"
        )
        self.record_btn.clicked.connect(self._record_color)
        h_layout.addWidget(self.record_btn)
        self.history_win.show()

    # ---------------------------------------------------------------- events
    def _draw_marker(self, base: QPixmap, x: int, y: int) -> QPixmap:
        pm = QPixmap(base)
        painter = QPainter(pm)
        painter.setPen(QPen(QColor("white"), 2))
        r = 8
        painter.drawLine(x - r, y, x + r, y)
        painter.drawLine(x, y - r, x, y + r)
        painter.end()
        return pm

    def _on_hue_press(self, event) -> None:
        self._update_hue(event.pos().x(), event.pos().y())
        self.hue_label.setPixmap(
            self._draw_marker(self.hue_base, event.pos().x(), event.pos().y())
        )

    def _on_hue_move(self, event) -> None:
        if event.buttons() & Qt.LeftButton:
            self._on_hue_press(event)

    def _on_sv_press(self, event) -> None:
        self._update_sv_color(event.pos().x(), event.pos().y())
        if self.sv_pixmap is not None:
            self.sv_label.setPixmap(
                self._draw_marker(self.sv_pixmap, event.pos().x(), event.pos().y())
            )

    def _on_sv_move(self, event) -> None:
        if event.buttons() & Qt.LeftButton:
            self._on_sv_press(event)

    # --------------------------------------------------------------- helpers
    def _update_hue(self, x: int, y: int) -> None:
        dx, dy = x - self.wheel_r, y - self.wheel_r
        if np.hypot(dx, dy) <= self.wheel_r:
            self.cur_hue = ((np.degrees(np.arctan2(dy, dx)) + 360) % 360) / 360
            self.update_sv()

    def _update_sv_color(self, x: int, y: int) -> None:
        if 0 <= x < self.sv_size and 0 <= y < self.sv_size:
            s = x / (self.sv_size - 1)
            v = 1 - y / (self.sv_size - 1)
            self._update_color(s, v * self.cur_val)

    def _on_val_change(self, value: int) -> None:
        self.cur_val = value / 100.0
        self.update_sv()

    def update_sv(self) -> None:
        img = gen_sv_square(self.sv_size, self.cur_hue, self.cur_val)
        self.sv_pixmap = pil_to_pixmap(img)
        self.sv_label.setPixmap(self.sv_pixmap)

    def _update_color(self, s: float, v: float) -> None:
        r, g, b = [int(255 * c) for c in colorsys.hsv_to_rgb(self.cur_hue, s, v)]
        hexc = f"#{r:02x}{g:02x}{b:02x}"
        self.last_hex = hexc
        self.preview.setStyleSheet(
            f"background-color:{hexc}; border:2px solid {COLORS['preview_bd']}"
        )
        self.lbl.setText(f"RGB=({r},{g},{b})   HEX={hexc}")

    def _record_color(self) -> None:
        if self.last_hex:
            self.history_lb.insertItem(0, self.last_hex)
            item = self.history_lb.item(0)
            item.setForeground(QColor(self.last_hex))
            if self.history_lb.count() > 20:
                self.history_lb.takeItem(20)


def main() -> None:
    app = QApplication(sys.argv)
    win = ColorPickerWindow()
    win.show()
    app.exec()


if __name__ == "__main__":
    main()


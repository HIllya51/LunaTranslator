from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence

from qtsymbols import (
    QApplication,
    QColor,
    QFont,
    QFontMetrics,
    QPainter,
    QPainterPath,
    QPen,
    QRect,
    Qt,
    QTimer,
    QWidget,
    QLabel,
)

_overlays = []

CONFIG = {
    "enable": 1,
    "text_color": "white",
    "stroke_color": "black",
    "stroke_width": 3,
    "min_font_size": 8,
    "max_font_size": 48,
    "font_family": "",
    "background_color": "rgba(0, 0, 0, 180)",
    "box_expansion": 6,
    "timeout_ms": 6000,
    "horizontal_padding": 4,
    "vertical_padding": 4,
}


def load_config():
    config_path = Path("userconfig/overlay.json")
    if not config_path.exists():
        return
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            CONFIG.update(data)
    except Exception:
        pass


def save_config():
    config_path = Path("userconfig/overlay.json")
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(CONFIG, f, ensure_ascii=False, indent=4)


def parse_color(color_str: str) -> QColor:
    color_str = str(color_str).strip().lower()
    if color_str.startswith("rgba"):
        try:
            content = color_str[color_str.find("(") + 1 : color_str.rfind(")")]
            parts = [x.strip() for x in content.split(",")]
            if len(parts) == 4:
                r, g, b = int(parts[0]), int(parts[1]), int(parts[2])
                a_str = parts[3]
                a = int(float(a_str) * 255) if "." in a_str else int(a_str)
                return QColor(r, g, b, a)
        except Exception:
            pass
    return QColor(color_str)


BOX_PATTERN = re.compile(
    r"\[(?P<x>\d+)\s+(?P<y>\d+)\|(?P<w>\d+)\s+(?P<h>\d+)\]\s*(?P<text>.*?)(?=\[\d+\s+\d+\|\d+\s+\d+\]|$)",
    re.DOTALL,
)


@dataclass
class TextBox:
    x: float
    y: float
    width: float
    height: float
    text: str


def parse_boxes(text: str) -> List[TextBox]:
    boxes: List[TextBox] = []
    text = re.sub(r"^\[Engine\].*?(\n|$)", "", text.strip())
    for match in BOX_PATTERN.finditer(text):
        value = match.group("text").strip()
        if not value:
            continue
        boxes.append(
            TextBox(
                x=int(match.group("x")),
                y=int(match.group("y")),
                width=int(match.group("w")),
                height=int(match.group("h")),
                text=value,
            )
        )
    return boxes


class StrokedLabel(QLabel):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(parse_color(CONFIG["background_color"]))
        painter.drawRoundedRect(self.rect(), 4, 4)

        text = self.text()
        if not text:
            return
        font = self.font()
        if CONFIG["font_family"]:
            font.setFamily(CONFIG["font_family"])
        painter.setFont(font)
        metrics = QFontMetrics(font)
        text_h = metrics.ascent() + metrics.descent()
        y = self.rect().top() + (self.rect().height() - text_h) / 2 + metrics.ascent()
        x = self.rect().left() + int(CONFIG["horizontal_padding"] / 2)

        path = QPainterPath()
        path.addText(x, y, font, text)
        painter.setPen(
            QPen(
                parse_color(CONFIG["stroke_color"]),
                float(CONFIG["stroke_width"]),
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
                Qt.PenJoinStyle.RoundJoin,
            )
        )
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(parse_color(CONFIG["text_color"]))
        painter.drawPath(path)


class Overlay(QWidget):
    def __init__(self, boxes: Sequence[TextBox]):
        super().__init__(None, Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.setWindowFlag(Qt.WindowType.Tool, True)
        if hasattr(Qt.WindowType, "WindowTransparentForInput"):
            self.setWindowFlag(Qt.WindowType.WindowTransparentForInput, True)

        screen = QApplication.primaryScreen()
        rect = screen.geometry()
        dpr = max(1.0, screen.devicePixelRatio())
        self.setGeometry(rect)
        self.labels = []
        self.boxes = list(boxes)
        self._render_boxes(self.boxes, dpr)

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.close)
        self.timer.start(int(CONFIG["timeout_ms"]))
        _overlays.append(self)

    def _render_boxes(self, boxes: Sequence[TextBox], dpr: float):
        box_expansion = float(CONFIG["box_expansion"])
        for box in boxes:
            scaled = TextBox(
                x=int(box.x / dpr) - box_expansion / 2,
                y=int(box.y / dpr) - box_expansion / 2,
                width=int(box.width / dpr) + box_expansion,
                height=int(box.height / dpr) + box_expansion,
                text=box.text,
            )
            self.labels.append(self._create_label(scaled))

    def update_content(self, boxes: Sequence[TextBox]):
        self.timer.start(int(CONFIG["timeout_ms"]))
        self.boxes = list(boxes)
        for label in self.labels:
            label.deleteLater()
        self.labels.clear()
        screen = QApplication.primaryScreen()
        dpr = max(1.0, screen.devicePixelRatio())
        self._render_boxes(self.boxes, dpr)
        self.show()

    def closeEvent(self, event):
        if self in _overlays:
            _overlays.remove(self)
        super().closeEvent(event)

    def _create_label(self, box: TextBox):
        label = StrokedLabel(box.text, self)
        label.setWordWrap(False)
        label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        font = QFont(label.font())
        if CONFIG["font_family"]:
            font.setFamily(CONFIG["font_family"])
        min_px = int(CONFIG["min_font_size"])
        max_px = int(CONFIG["max_font_size"])
        vpad = int(CONFIG["vertical_padding"])
        hpad = int(CONFIG["horizontal_padding"])
        px = int(min(max_px, max(min_px, box.height - vpad)))
        font.setPixelSize(px)
        metrics = QFontMetrics(font)
        target_w = max(1, int(box.width - hpad))
        target_h = max(1, int(box.height - vpad))
        while px > min_px:
            width = (
                metrics.horizontalAdvance(box.text)
                if hasattr(metrics, "horizontalAdvance")
                else metrics.width(box.text)
            )
            if width <= target_w and metrics.height() <= target_h:
                break
            px -= 1
            font.setPixelSize(px)
            metrics = QFontMetrics(font)
        label.setFont(font)
        label.setGeometry(QRect(int(box.x), int(box.y), int(box.width), int(box.height)))
        label.show()
        return label


def close_all():
    for item in _overlays[:]:
        item.close()


def show_overlay(data: str) -> int:
    load_config()
    if not CONFIG.get("enable", 1):
        return 0
    boxes = parse_boxes(data)
    if not boxes:
        return 1
    app = QApplication.instance()
    run_loop = False
    if app is None:
        app = QApplication([])
        run_loop = True
    if _overlays:
        _overlays[0].update_content(boxes)
    else:
        overlay = Overlay(boxes)
        overlay.show()
    if run_loop:
        return app.exec()
    return 0

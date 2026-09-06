from PySide6.QtCore import QPoint, QPropertyAnimation, Qt, Signal
from PySide6.QtGui import QIcon, QTransform
from PySide6.QtWidgets import QApplication, QPushButton

from .telemetry_panel import TelemetryPanel
from .enums import SlidingStrategy


class DraggableButton(QPushButton):
    dragged = Signal(int)

    DRAG_THRESHOLD = 30
    SLIDE_DURATION = 100

    def __init__(self, width: int, height: int, icon: QIcon):
        super().__init__()

        self._original_icon = icon
        self._drag_start_y = 0
        self._last_mouse_y = 0
        self.is_dragged = False
        self.is_slided_in = False

        self._configure_window()
        self._configure_button(width, height)
        self._configure_animation()

    # Configs
    def _configure_window(self) -> None:
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )

    def _configure_button(self, width: int, height: int) -> None:
        self.setFixedSize(width, height)
        self.setIcon(self._rotated_icon(180))

    def _configure_animation(self) -> None:
        self._animation = QPropertyAnimation(self, b"pos")
        self._animation.setDuration(self.SLIDE_DURATION)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._last_mouse_y = self._global_mouse_y(event)
            self.is_dragged = False

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not event.buttons() & Qt.MouseButton.LeftButton:
            super().mouseMoveEvent(event)
            return

        mouse_y = self._global_mouse_y(event)
        dy = mouse_y - self._last_mouse_y

        if dy:
            self.is_dragged = True
            self._move_vertically(dy)
            self.dragged.emit(dy)

        self._last_mouse_y = mouse_y

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragged = abs(
                self._global_mouse_y(event) - self._last_mouse_y # this got broken.
            ) >= self.DRAG_THRESHOLD

        super().mouseReleaseEvent(event)

    @staticmethod
    def _global_mouse_y(event) -> int:
        return event.globalPosition().toPoint().y()

    def _move_vertically(self, dy: int) -> None:
        self.move(self.x(), self.y() + dy)


    def slide(self,panel: TelemetryPanel,strategy: SlidingStrategy) -> None:
        screen = QApplication.primaryScreen().availableGeometry()

        if strategy == SlidingStrategy.IN:
            self._slide_in(screen, panel)
        else:
            self._slide_out(screen, panel)

        self._animation.start()

    def _slide_in(self, screen, panel: TelemetryPanel) -> None:
        button_x = screen.right() - panel.width()
        panel_x = button_x + self.width()

        self.is_slided_in = True
        self._set_icon_rotation(angle=0)

        self._animate_button_to(button_x)
        panel.slide(panel.x(), panel_x)

    def _slide_out(self, screen, panel: TelemetryPanel) -> None:
        button_x = screen.right() - self.width() + 1
        panel_x = screen.right() + 1

        self.is_slided_in = False
        self._set_icon_rotation(angle=180)

        self._animate_button_to(button_x)
        panel.slide(panel.x(), panel_x)

    def _animate_button_to(self, x: int) -> None:
        self._animation.stop()
        self._animation.setStartValue(self.pos())
        self._animation.setEndValue(QPoint(x, self.y()))


    def _set_icon_rotation(self, angle: float) -> None:
        self.setIcon(self._rotated_icon(angle))

    def _rotated_icon(self, angle: float) -> QIcon:
        pixmap = self._original_icon.pixmap(self.iconSize())

        transform = QTransform()
        transform.rotate(angle)

        return QIcon(pixmap.transformed(transform))
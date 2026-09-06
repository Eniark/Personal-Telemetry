from PySide6.QtCore import Qt, QPropertyAnimation, QPoint
from PySide6.QtWidgets import (
    QWidget,
)


class TelemetryPanel(QWidget):
    SLIDE_DURATION = 100
    def __init__(self):
        super().__init__()

        # Configs
        self._configure_window()
        self._configure_animation()
        self._configure_panel()

    def _configure_animation(self) -> None:
        self._animation = QPropertyAnimation(self, b"pos")
        self._animation.setDuration(self.SLIDE_DURATION)

    def _configure_window(self) -> None:
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
    def _configure_panel(self) -> None:
        self.setStyleSheet("""
            TelemetryPanel {
                background-color: #222;
                border-radius: 10px;
            }
        """)
        
    def on_button_dragged(self, dy: int):
        self.move(self.x(), self.y() + dy)

    def slide(self, start_x: int, end_x: int):
        self._animation.stop()

        self._animation.setStartValue(
            QPoint(start_x, self.y())
        )

        self._animation.setEndValue(
            QPoint(end_x, self.y())
        )

        self._animation.start()

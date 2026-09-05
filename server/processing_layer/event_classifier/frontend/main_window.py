from PySide6.QtCore import Qt, QPropertyAnimation, QPoint
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QHBoxLayout
)

from .draggable_button import DraggableButton
from .telemetry_table import TelemetryTable
from .enums import SlidingStrategy


class MainWindow(QWidget):
    def __init__(
        self,
        button: DraggableButton,
        table: TelemetryTable,
    ):
        super().__init__()

        self.button = button
        self.table = table

        self.is_slided_in = False

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )

        self.resize(700, 300)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.button, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.table)

        self.button.dragged.connect(
            self.on_button_dragged
        )
        self.animation = QPropertyAnimation(
            self,
            b"pos"
        )

        self.animation.setDuration(100)

    def slide(self, how: SlidingStrategy) -> None:
        screen = QApplication.primaryScreen().availableGeometry()

        if how == SlidingStrategy.IN:
            start_x = screen.right() + 1
            end_x = screen.right() - self.width() + 1
            self.is_slided_in = True
            self.button.rotate_icon(angle=180)
        elif SlidingStrategy.OUT:
            start_x = self.x()
            end_x  = screen.right() - self.button.width()
            self.is_slided_in = False
            self.button.rotate_icon(angle=0)


        self.move(start_x, self.y())

        self.animation.setStartValue(QPoint(start_x, self.y()))
        self.animation.setEndValue(QPoint(end_x, self.y()))

        self.show()
        self.animation.start()

    def on_button_dragged(self, dy):
        self.move(
            self.x(),
            self.y() + dy
        )
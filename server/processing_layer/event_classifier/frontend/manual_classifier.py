import sys

from ..configs import MEDIA_FOLDER

from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QPushButton, QWidget

from .draggable_button import DraggableButton
from .telemetry_panel import TelemetryPanel
from .enums import SlidingStrategy
from .telemetry_table import TelemetryTable

from PySide6.QtCore import Qt, QPropertyAnimation, QPoint
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QTabWidget,
    QLabel
)

from .draggable_button import DraggableButton
from .telemetry_table import TelemetryTable
from .enums import SlidingStrategy
from .tab import Tab



app = QApplication(sys.argv)

right_arrow_icon = MEDIA_FOLDER / "right-arrow.png"

BTN_WIDTH = 15
BTN_HEIGHT = 36

screen = app.primaryScreen()
geometry = screen.availableGeometry()
button2 = QPushButton()

# Create the edge button
button = DraggableButton(width=BTN_WIDTH, height=BTN_HEIGHT, icon=QIcon(str(right_arrow_icon)))
button.setFixedSize(50, 36)




headers = [
    "Event",
    "Category",
]
table = TelemetryTable(n_rows=3, n_cols=2, headers=headers)
panel = TelemetryPanel()

layout = QVBoxLayout(panel)
tabs = QTabWidget()

tabs.addTab(Tab(label="Classifier Report"), "Report")
tabs.addTab(Tab(label='Information'), "Dashboard")

layout.addWidget(tabs)
layout.addWidget(table)


button_x = geometry.right() - button.width()
button_y = geometry.center().y() - button.height() // 2
button.move(button_x, button_y)

panel_x = geometry.right()
panel_y = button_y

panel.move(panel_x, panel_y)

button2.move(100, 100)
button2.setFixedSize(100, 100)
panel.setFixedSize(700, 300)
button2.setParent(panel)

button.dragged.connect(panel.on_button_dragged)
button.show()
panel.show()


def on_click():
    if not button.is_dragged:
        slide_strategy = (
            SlidingStrategy.OUT
            if button.is_slided_in
            else SlidingStrategy.IN
        )

        button.slide(panel=panel, strategy=slide_strategy)

button.clicked.connect(on_click)
button2.clicked.connect(QApplication.quit)

sys.exit(app.exec())



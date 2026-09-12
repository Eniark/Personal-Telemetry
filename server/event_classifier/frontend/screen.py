import sys

from server.db.repository import ActivityRepository
from shared.configs import DB_PATH

from server.event_classifier.configs import MEDIA_FOLDER


from .draggable_button import DraggableButton
from .telemetry_panel import TelemetryPanel
from .enums import SlidingStrategy
from .telemetry_table import TelemetryTable

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QTabWidget,
    QLabel
)
from server.db.db_connect import create_db_connection
from .draggable_button import DraggableButton
from .telemetry_table import TelemetryTable
from .enums import SlidingStrategy
from .tab import Tab




db = create_db_connection(DB_PATH)
repository = ActivityRepository(db)

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



table = TelemetryTable(repository=repository)
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
panel.setFixedSize(1400, 300)
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



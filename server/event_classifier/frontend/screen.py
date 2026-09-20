import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
)

from server.db.db_connect import create_db_connection
from server.db.repository import ActivityRepository
from server.event_classifier.configs import MEDIA_FOLDER
from shared.configs import DB_PATH

from .draggable_button import DraggableButton
from .enums import SlidingStrategy
from .tab import Tab
from .telemetry_panel import TelemetryPanel
from .telemetry_table import TelemetryTable


BTN_WIDTH = 15
BTN_HEIGHT = 36
PANEL_WIDTH = 1400
PANEL_HEIGHT = 300


def create_repository() -> ActivityRepository:
    db = create_db_connection(DB_PATH)
    return ActivityRepository(db)



def create_panel(repository: ActivityRepository) -> TelemetryPanel:

    def create_tabs() -> QTabWidget:
        tabs = QTabWidget()

        tabs.addTab(Tab(label="Classifier Report"),"Report")
        tabs.addTab(Tab(label="Information"),"Dashboard")

        return tabs

    panel = TelemetryPanel()

    layout = QVBoxLayout(panel)
    layout.addWidget(create_tabs())
    layout.addWidget(TelemetryTable(repository=repository))

    panel.setFixedSize(PANEL_WIDTH, PANEL_HEIGHT)

    return panel


def create_button() -> DraggableButton:
    icon_path = MEDIA_FOLDER / "right-arrow.png"

    button = DraggableButton(
        width=BTN_WIDTH,
        height=BTN_HEIGHT,
        icon=QIcon(str(icon_path)),
    )
    button.setFixedSize(50, 36)

    return button


def position_widgets(button: DraggableButton, panel: TelemetryPanel) -> None:
    screen = QApplication.primaryScreen()
    geometry = screen.availableGeometry()

    button_x = geometry.right() - button.width()
    button_y = geometry.center().y() - button.height() // 2

    button.move(button_x, button_y)
    panel.move(geometry.right(), button_y)


def connect_signals(
    button: DraggableButton,
    panel: TelemetryPanel,
    quit_button: QPushButton,
) -> None:

    button.dragged.connect(panel.on_button_dragged)

    def on_button_clicked() -> None:
        if button.is_dragged:
            return

        strategy = (
            SlidingStrategy.OUT
            if button.is_slided_in
            else SlidingStrategy.IN
        )

        button.slide(
            panel=panel,
            strategy=strategy,
        )

    button.clicked.connect(on_button_clicked)
    quit_button.clicked.connect(QApplication.quit)


def main() -> int:
    app = QApplication(sys.argv)

    repository = create_repository()

    panel = create_panel(repository)
    button = create_button()

    temp_quit_button = QPushButton(parent=panel)
    temp_quit_button.setFixedSize(100, 100)
    temp_quit_button.move(100, 100)

    position_widgets(button, panel)
    connect_signals(button, panel, temp_quit_button)

    button.show()
    panel.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
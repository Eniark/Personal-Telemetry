import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
)
from PySide6.QtCore import Qt

from server.db.db_connect import create_db_connection
from server.db.repository import ActivityRepository
from server.event_classifier.configs import MEDIA_FOLDER
from shared.configs import DB_PATH

from .draggable_button import DraggableButton
from .enums import SlidingStrategy
from .telemetry_panel import TelemetryPanel
from .tables.table_widgets import OsEventsTable, BrowserEventsTable


def create_repository() -> ActivityRepository:
    db = create_db_connection(DB_PATH)
    return ActivityRepository(db)


def create_panel(repository: ActivityRepository) -> TelemetryPanel:

    refresh_button = QPushButton('Refresh')
    refresh_button.setFixedSize(100, 25)

    temp_clear_table_btn = QPushButton('Clear')
    temp_clear_table_btn.setFixedSize(100, 25)

    temp_quit_btn = QPushButton('Exit')
    temp_quit_btn.setFixedSize(100, 25)

    panel = TelemetryPanel()
    layout = QVBoxLayout(panel)
    button_layout = QHBoxLayout()
    browser_events_table = BrowserEventsTable(repository=repository)
    os_events_table = OsEventsTable(repository=repository, browser_events_table=browser_events_table, layout=layout)
    button_layout.addWidget(refresh_button)
    button_layout.addWidget(temp_clear_table_btn)
    button_layout.addWidget(temp_quit_btn)
    button_layout.addStretch()

    layout.addLayout(button_layout)
    layout.addWidget(os_events_table)
    refresh_button.clicked.connect(os_events_table.populate_table)
    temp_clear_table_btn.clicked.connect(os_events_table.temp__clear_tables)
    temp_quit_btn.clicked.connect(QApplication.quit)

    return panel


def create_button() -> DraggableButton:

    BTN_WIDTH = 50
    BTN_HEIGHT = 36
    icon_path = MEDIA_FOLDER / "right-arrow.png"

    button = DraggableButton(
        width=BTN_WIDTH,
        height=BTN_HEIGHT,
        icon=QIcon(str(icon_path)),
    )

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


def main() -> int:
    app = QApplication(sys.argv)

    repository = create_repository()

    panel = create_panel(repository)
    button = create_button()

    position_widgets(button, panel)
    connect_signals(button, panel)

    button.show()
    panel.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QTabWidget,
    QWidget
)

from shared.utils import create_db_connection
from server.db.repository import TelemetryRepository
from shared.configs import DB_PATH, MEDIA_FOLDER

from .draggable_button import DraggableButton
from .enums import SlidingStrategy
from .telemetry_panel import TelemetryPanel
from .tables.table_widgets import OsEventsTable, BrowserEventsTable


def create_repository() -> TelemetryRepository:
    db = create_db_connection(DB_PATH)
    return TelemetryRepository(db)


def create_panel(repository: TelemetryRepository, screen_size: int) -> TelemetryPanel:

    panel = TelemetryPanel(screen_size=screen_size)
    layout = QVBoxLayout(panel)

    tabs = QTabWidget()

    # TABLE TAB
    # ==============================================
    table_tab = QWidget()
    table_layout = QVBoxLayout(table_tab)

    button_layout = QHBoxLayout()

    refresh_button = QPushButton('Refresh')
    refresh_button.setFixedSize(100, 25)

    temp_quit_btn = QPushButton('Exit')
    temp_quit_btn.setFixedSize(100, 25)

    button_layout.addWidget(refresh_button)
    button_layout.addWidget(temp_quit_btn)
    button_layout.addStretch()

    browser_events_table = BrowserEventsTable(repository=repository)

    os_events_table = OsEventsTable(repository=repository)

    os_events_table.os_event_selected.connect(
        browser_events_table.populate_table
    )

    table_layout.addLayout(button_layout)
    table_layout.addWidget(os_events_table)
    table_layout.addWidget(browser_events_table)
    # ==============================================



    # DASHBOARD TAB
    # ==============================================
    dashboard_tab = QWidget()
    dashboard_layout = QVBoxLayout(dashboard_tab)
    # ==============================================


    tabs.addTab(table_tab, "Events")
    tabs.addTab(dashboard_tab, "Dashboard")

    layout.addWidget(tabs)

    refresh_button.clicked.connect(os_events_table.populate_table)
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

    screen_width = QApplication.primaryScreen().availableGeometry().width()
    panel = create_panel(repository, screen_width)
    button = create_button()

    position_widgets(button, panel)
    connect_signals(button, panel)

    button.show()
    panel.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
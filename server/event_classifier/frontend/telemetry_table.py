

from PySide6.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
)

from server.db.repository import ActivityRepository



class TelemetryTable(QTableWidget):
    def __init__(self, n_rows: int, n_cols: int, headers: list, repository: ActivityRepository):
        super().__init__()
        self.setRowCount(n_rows)
        self.setColumnCount(n_cols)

        self.setHorizontalHeaderLabels(headers)

        self.setItem(0, 0, QTableWidgetItem("Chrome"))
        self.setItem(1, 0, QTableWidgetItem("VS Code"))
        self.setItem(2, 0, QTableWidgetItem("Spotify"))

        self.repository = repository
        self.get_contents()
        
    def get_contents(self):
        events = self.repository.select_events()
        print(events[0])

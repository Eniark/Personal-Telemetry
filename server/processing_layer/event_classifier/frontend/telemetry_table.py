

from PySide6.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
)



class TelemetryTable(QTableWidget):
    def __init__(self, n_rows: int, n_cols: int, headers: list):
        super().__init__()
        self.setRowCount(n_rows)
        self.setColumnCount(n_cols)

        self.setHorizontalHeaderLabels(headers)

        self.setItem(0, 0, QTableWidgetItem("Chrome"))
        self.setItem(1, 0, QTableWidgetItem("VS Code"))
        self.setItem(2, 0, QTableWidgetItem("Spotify"))
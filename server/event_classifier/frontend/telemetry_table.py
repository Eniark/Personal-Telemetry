

from PySide6.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
    QComboBox,
    QPushButton,
    QHeaderView
)
from PySide6.QtCore import Qt
from server.processing_layer.enums import EventCategory

from server.db.repository import ActivityRepository



class TelemetryTable(QTableWidget):
    ADDITIONAL_COLUMNS = ['Class', 'Action']
    __COLUMN_CONFIGS = {
        "title": {
            "width": 250
        },
        "executable": {
            "width": 100
        },
        "event_start_time": {
            "text_alignment": "center"
        },
        "event_end_time": {
            "text_alignment": "center"
        },
        "Class": {
            "width": 100,
            "text_alignment": "center"
        },
        "Action": {
            "width": 100,
            "text_alignment": "center"
        },
    }
    def __init__(self, repository: ActivityRepository):
        super().__init__()
        self.repository = repository
        self.max_rows = 20
        self.populate_table()
    

    def __configure_table(self):
        # self.setColumnWidth(0, 200)
        widget_header = self.horizontalHeader()
        widget_header.setSectionResizeMode(QHeaderView.Stretch)
        widget_header.setSectionResizeMode(0, QHeaderView.Fixed)
        widget_header.setSectionResizeMode(1, QHeaderView.Fixed)
        widget_header.setSectionResizeMode(6, QHeaderView.Fixed)
        widget_header.setSectionResizeMode(7, QHeaderView.Fixed)

        for idx, name in enumerate(self.headers):
            column_config = self.__COLUMN_CONFIGS.get(name, {})
            width = column_config.get("width")
            if width:
                self.setColumnWidth(idx, width)

    def populate_table(self) -> None:
        headers, events = self.repository.get_events(get_headers=True, limit=None)
        events = events[:self.max_rows]
        column_count = len(events[0]) + len(TelemetryTable.ADDITIONAL_COLUMNS)

        self.setRowCount(len(events))
        self.setColumnCount(column_count)

        self.headers = headers + TelemetryTable.ADDITIONAL_COLUMNS
        self.setHorizontalHeaderLabels(self.headers)
        for row_idx, row in enumerate(events):
            action_button = QPushButton("Apply")
            event_category_dropdown = QComboBox()
            event_category_dropdown.addItems([category.value for category in EventCategory])
            for col_idx, value in enumerate(row):
                item = QTableWidgetItem(value)
                column_name = self.headers[col_idx]
                column_config = TelemetryTable.__COLUMN_CONFIGS.get(column_name, {})
                if column_config.get("text_alignment") == "center":
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                self.setItem(row_idx, col_idx, item)
            self.setCellWidget(row_idx, self.headers.index('Class'), event_category_dropdown)
            self.setCellWidget(row_idx, self.headers.index('Action'), action_button)


        self.__configure_table()

        


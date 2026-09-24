
import datetime
from PySide6.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
    QComboBox,
    QPushButton,
    QHeaderView,
    QVBoxLayout
)
from PySide6.QtCore import Qt
from server.processing_layer.enums import EventCategory
from server.event_classifier.backend.classifier import Classification
from server.processing_layer.sql_queries import SELECT_OS_EVENTS_QUERY, SELECT_BROWSER_EVENTS_QUERY
from server.db.repository import ActivityRepository
from server.processing_layer.enums import EventType
from .column import Column

class TelemetryTable(QTableWidget):
    TABLE_HEIGHT = 300
    def __init__(self, repository: ActivityRepository):
        super().__init__()
        self.repository = repository
        self.max_rows = 20
        self.visible_headers = list(filter(lambda column_config: not column_config.hidden, self.COLUMN_CONFIGS))

    def _preconfigure_table(self):
        self.setFixedHeight(self.TABLE_HEIGHT)
        widget_header = self.horizontalHeader()
        widget_header.setSectionResizeMode(QHeaderView.Stretch)
        widget_header.setSectionResizeMode(0, QHeaderView.Fixed)

        self.setRowCount(self.n_rows)
        self.setColumnCount(self.n_cols)
        self.setHorizontalHeaderLabels(self.visible_headers)
        
        for idx, name in enumerate(self.visible_headers):
            column_config = self.COLUMN_CONFIGS.get(name)
            if column_config:
                if column_config.width is not None:
                    self.setColumnWidth(idx, column_config.width)

                if column_config.hidden:
                    self.setColumnHidden(idx, True)

    def _postconfigure_table(self):
        for row_idx in range(self.rowCount()):
            for col_idx in range(self.columnCount() - 1):
                column_name = self.visible_headers[col_idx]
                column_config = self.COLUMN_CONFIGS.get(column_name)
                item = self.item(row_idx, col_idx)


                if item and column_config and column_config.text_alignment == "center":
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

class BrowserEventsTable(TelemetryTable):
    COLUMN_CONFIGS = {
        "event_start_time": Column(title="Event Start Time", text_alignment="center"),
        "event_end_time": Column(title="Event End Time", text_alignment="center"),
    }
    def __init__(self, repository: ActivityRepository):
        super().__init__(repository)
        self.populate_table()

    def _preconfigure_table(self):
        super()._preconfigure_table()

    def populate_table(self, os_event_id: str|None = None) -> None:

        headers, events = self.repository.get_events(query=SELECT_BROWSER_EVENTS_QUERY, params=(os_event_id,), get_headers=True, limit=None)
        events = events[:self.max_rows]
        query_column_count = 0
        if len(events) > 0:
            query_column_count = len(events[0])
        self.n_cols = query_column_count
        self.n_rows = len(events)
        headers = list(map(lambda x: OsEventsTable.map_headers_to_titles(x, self.COLUMN_CONFIGS), headers))
        self.visible_headers = headers

        self._preconfigure_table()
        for row_idx, row in enumerate(events):

            for col_idx, value in enumerate(row):
                value = str(value)
                self.setItem(row_idx, col_idx, QTableWidgetItem(value))
        self._postconfigure_table()

class OsEventsTable(TelemetryTable):
    COLUMN_CONFIGS = {
        "title": Column(title="title", width=250),
        "event_id": Column(title="Event Id", hidden=True),
        "type": Column(title="Type", hidden=True),
        "executable": Column(title="Executable", width=100),
        "event_start_time": Column(title="Event Start Time", text_alignment="center"),
        "event_end_time": Column(title="Event End Time", text_alignment="center"),
        "class": Column(title="Proposed Class", width=100, text_alignment="center"),
        "action": Column(title="Action", width=100, text_alignment="center"),
    }
    ADDITIONAL_COLUMNS = [COLUMN_CONFIGS['class'].title, COLUMN_CONFIGS['action'].title]
    def __init__(self, repository: ActivityRepository, browser_events_table: BrowserEventsTable, layout: QVBoxLayout):
        super().__init__(repository)
        self.browser_events_table = browser_events_table
        self.layout = layout
        self.populate_table()
    

    def _preconfigure_table(self):
        widget_header = self.horizontalHeader()
        widget_header.setSectionResizeMode(self.visible_headers.index('id'), QHeaderView.Fixed)
        widget_header.setSectionResizeMode(6, QHeaderView.Fixed)
        widget_header.setSectionResizeMode(7, QHeaderView.Fixed)

        super()._preconfigure_table()
        

    def delete_record(self) -> None:
        button = self.sender()

        for row in range(self.rowCount()):
            if self.cellWidget(row, self.visible_headers.index('Action')) is button:
                self.removeRow(row)
                break
    
    def show_events_table(self, item: QTableWidgetItem) -> None:
        row = item.row()
        event_id = self.item(row, 1).text()
        event_type =self.item(row, 2).text()
        if event_type == EventType.BROWSER.value:
            self.browser_events_table.populate_table(os_event_id=event_id)
            self.layout.addWidget(self.browser_events_table)
    
        else:
            self.browser_events_table.setParent(None)
            self.parentWidget().adjustSize()
    def update_classification(self, event_id: str, dropdown: QComboBox) -> None:
        classification = Classification(
            class_=dropdown.currentText(),
            classified_at=datetime.datetime.now(),
            classified_by='user'
        )

        self.repository.update_classification(event_id=event_id, classification=classification)
    
    @staticmethod
    def map_headers_to_titles(header: str, mapping: dict[str, Column]):
        column_config = mapping.get(header)
        if column_config is not None:
            return column_config.title
        else:
            return header
        
    def populate_table(self) -> None:

        headers, events = self.repository.get_events(query=SELECT_OS_EVENTS_QUERY, get_headers=True, limit=None)
        events = events[:self.max_rows]
        self.n_rows = len(events)
        if self.n_rows > 0:
            self.n_cols = len(events[0])
        self.n_cols = self.n_cols + len(OsEventsTable.ADDITIONAL_COLUMNS)
        headers = list(map(lambda x: OsEventsTable.map_headers_to_titles(x, self.COLUMN_CONFIGS), headers))
        self.visible_headers = headers + OsEventsTable.ADDITIONAL_COLUMNS


        self._preconfigure_table()
        for row_idx, row in enumerate(events):
            action_button = QPushButton("Apply")
            event_category_dropdown = QComboBox()
            event_category_dropdown.addItems([category.value for category in EventCategory])
            for col_idx, value in enumerate(row):
                value = str(value)
                self.setItem(row_idx, col_idx, QTableWidgetItem(value))
            self.setCellWidget(row_idx, self.visible_headers.index(self.COLUMN_CONFIGS['class'].title), event_category_dropdown)
            self.setCellWidget(row_idx, self.visible_headers.index(self.COLUMN_CONFIGS['action'].title), action_button)
            event_id = row[0]
            action_button.clicked.connect(lambda _, event_id=event_id, dropdown=event_category_dropdown: self.update_classification(event_id=event_id, dropdown=dropdown))
            action_button.clicked.connect(self.delete_record)


        self.itemClicked.connect(self.show_events_table)
        self._postconfigure_table()

        


from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
)

class Tab(QWidget):
    def __init__(self, label: str):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(label))

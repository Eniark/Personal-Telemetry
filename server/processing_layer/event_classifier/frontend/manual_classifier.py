import sys

from ..configs import MEDIA_FOLDER

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QPushButton

from .draggable_button import DraggableButton
from .main_window import MainWindow
from .enums import SlidingStrategy
from .telemetry_table import TelemetryTable

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
# Create the main window
main_window = MainWindow(button=button, table=table)
x = geometry.right() - button.width() - 500
y = geometry.center().y() - button.height() // 2
# button.move(button_x, button_y)
button2.move(0, 100)
button2.setFixedSize(50, 36)
button2.setParent(main_window)
main_window.move(x,y)
main_window.show()


def on_click():
    if not button.is_dragged:
        slide_strategy = (
            SlidingStrategy.OUT
            if main_window.is_slided_in
            else SlidingStrategy.IN
        )

        main_window.slide(how=slide_strategy)


button.clicked.connect(on_click)
button2.clicked.connect(QApplication.quit)

sys.exit(app.exec())
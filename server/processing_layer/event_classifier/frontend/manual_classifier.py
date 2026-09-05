import sys
from ..configs import MEDIA_FOLDER
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QPushButton
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize

app = QApplication(sys.argv)
right_arrow_icon = MEDIA_FOLDER / 'right-arrow.png'

screen = app.primaryScreen()
geometry = screen.availableGeometry()

button = QPushButton()
button.setIcon(QIcon(str(right_arrow_icon)))
button.setIconSize(QSize(15, 36))

button.clicked.connect(QApplication.quit)

button.setWindowFlags(
    Qt.WindowType.FramelessWindowHint
    # | Qt.WindowType.WindowStaysOnTopHint
    | Qt.WindowType.Tool
)

button.show()

# We need the actual size after showing the widget
button.move(
    geometry.right() - button.width(),
    geometry.center().y() - button.height() // 2
)

sys.exit(app.exec())
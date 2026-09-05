from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon, QTransform
from PySide6.QtWidgets import QPushButton


class DraggableButton(QPushButton):
    dragged = Signal(int) # used to send information to the widget that it should be dragged

    def __init__(self, width, height, icon):
        super().__init__()

        self.original_icon = icon

        self.setFixedSize(width, height)
        self.setIcon(self.original_icon)

        self.drag_threshold = 30 # number of pixels to consider an action as "dragging"
        self._drag__previous_mouse_y = 0
        self._current_mouse_y = self.y()
        self.is_dragged = False


    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag__previous_mouse_y = event.globalPosition().toPoint().y()

        super().mousePressEvent(event)


    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton: # here event.buttons() returns a bitmask
            mouse_y = event.globalPosition().toPoint().y()
            dy = mouse_y - self._drag__previous_mouse_y
            
            if dy != 0:
                self.is_dragged = True

            self.dragged.emit(dy) # emit the drag signal

            self._drag__previous_mouse_y = mouse_y

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton: # here event.button() returns the actual button
            mouse_y = event.globalPosition().toPoint().y()
            dy = mouse_y - self._current_mouse_y
            
            self.is_dragged = abs(dy) >= self.drag_threshold
            self._current_mouse_y = mouse_y

        super().mouseReleaseEvent(event)

    def rotate_icon(self, angle: float):
        pixmap = self.original_icon.pixmap(self.iconSize())

        transform = QTransform()
        transform.rotate(angle)

        rotated_pixmap = pixmap.transformed(transform)

        self.setIcon(QIcon(rotated_pixmap))
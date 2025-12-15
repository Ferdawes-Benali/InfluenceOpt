"""Coverage dial (small control for coverage %)."""
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QDial
from PyQt5.QtCore import Qt


class CoverageDial(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout()
        self.dial = QDial()
        self.dial.setRange(50, 100)
        self.dial.setValue(80)
        layout.addWidget(QLabel("Coverage %"))
        layout.addWidget(self.dial)
        self.setLayout(layout)

    def value(self) -> float:
        return self.dial.value() / 100.0

"""Budget slider widget with QSlider + QSpinBox pairing."""
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QSlider, QSpinBox, QLabel
from PyQt5.QtCore import Qt, pyqtSignal


class BudgetSlider(QWidget):
    valueChanged = pyqtSignal(int)

    def __init__(self, parent=None, maximum: int = 100000):
        super().__init__(parent)
        layout = QHBoxLayout()
        self.label = QLabel("Budget")
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(maximum)
        self.spin = QSpinBox()
        self.spin.setMinimum(0)
        self.spin.setMaximum(maximum)
        self.spin.setSuffix(" $")
        layout.addWidget(self.label)
        layout.addWidget(self.slider)
        layout.addWidget(self.spin)
        self.setLayout(layout)
        self.slider.valueChanged.connect(self.spin.setValue)
        self.spin.valueChanged.connect(self.slider.setValue)
        self.spin.valueChanged.connect(self.valueChanged.emit)

    def setValue(self, v: int) -> None:
        self.spin.setValue(v)

    def value(self) -> int:
        return self.spin.value()

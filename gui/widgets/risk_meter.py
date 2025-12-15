"""Risk meter widget: topic selector + slider max-risk."""
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QComboBox, QSlider, QLabel
from PyQt5.QtCore import Qt, pyqtSignal


class RiskMeter(QWidget):
    valueChanged = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout()
        self.topic = QComboBox()
        self.topic.addItems(["General", "Sensitive topic", "Health", "Politics"])
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(20)
        self.label = QLabel("Max risk: 20%")
        layout.addWidget(self.topic)
        layout.addWidget(self.slider)
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.slider.valueChanged.connect(self._on_val)

    def _on_val(self, v: int) -> None:
        self.label.setText(f"Max risk: {v}%")
        self.valueChanged.emit(v / 100.0)

    def value(self) -> float:
        return self.slider.value() / 100.0

"""Simple ROI estimator label showing conversion value minus cost."""
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QDoubleSpinBox
from typing import Optional


class RoiLabel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout()
        layout.addWidget(QLabel("Conv value per conversion:"))
        self.conv = QDoubleSpinBox()
        self.conv.setRange(0.0, 1000000.0)
        self.conv.setValue(100.0)
        self.label = QLabel("ROI: -")
        layout.addWidget(self.conv)
        layout.addWidget(self.label)
        self.setLayout(layout)

    def conv_value(self) -> float:
        return float(self.conv.value())

    def set_roi(self, roi: Optional[float]) -> None:
        if roi is None:
            self.label.setText("ROI: -")
        else:
            self.label.setText(f"ROI: {roi:.2f}")

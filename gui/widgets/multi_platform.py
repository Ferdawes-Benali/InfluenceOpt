"""Multi-platform selection and min/max percent filter."""
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QCheckBox, QLabel, QSpinBox, QVBoxLayout
from typing import Dict


class MultiPlatformBox(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Platforms"))
        row = QHBoxLayout()
        self.ig = QCheckBox("IG")
        self.tt = QCheckBox("TT")
        self.yt = QCheckBox("YT")
        self.tw = QCheckBox("TW")
        for cb in (self.ig, self.tt, self.yt, self.tw):
            cb.setChecked(True)
            row.addWidget(cb)
        layout.addLayout(row)
        pm = QHBoxLayout()
        pm.addWidget(QLabel("Min %"))
        self.min_spin = QSpinBox()
        self.min_spin.setRange(0, 100)
        self.min_spin.setValue(0)
        pm.addWidget(self.min_spin)
        pm.addWidget(QLabel("Max %"))
        self.max_spin = QSpinBox()
        self.max_spin.setRange(0, 100)
        self.max_spin.setValue(100)
        pm.addWidget(self.max_spin)
        layout.addLayout(pm)
        self.setLayout(layout)

    def selected_platforms(self) -> Dict[str, bool]:
        return {'IG': self.ig.isChecked(), 'TT': self.tt.isChecked(), 'YT': self.yt.isChecked(), 'TW': self.tw.isChecked()}

    def bounds(self) -> Dict[str, int]:
        return {'min_pct': self.min_spin.value(), 'max_pct': self.max_spin.value()}

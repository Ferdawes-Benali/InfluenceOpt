"""Left dock constraint panel aggregating widgets."""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QProgressBar, QDockWidget
from PyQt5.QtCore import pyqtSignal

from .widgets.budget_slider import BudgetSlider
from .widgets.risk_meter import RiskMeter


class ConstraintPanel(QWidget):
    solveRequested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Constraints"))
        self.budget = BudgetSlider(maximum=100000)
        self.risk = RiskMeter()
        from .widgets.audience_filter import AudienceFilter
        from .widgets.multi_platform import MultiPlatformBox
        from .widgets.roi_label import RoiLabel
        from .widgets.coverage_dial import CoverageDial
        from utils.settings import settings
        import json

        self.audience = AudienceFilter()
        self.platforms = MultiPlatformBox()
        self.roi = RoiLabel()
        self.coverage = CoverageDial()

        layout.addWidget(self.budget)
        layout.addWidget(self.risk)
        layout.addWidget(self.audience)
        layout.addWidget(self.platforms)
        layout.addWidget(self.coverage)
        layout.addWidget(self.roi)
        self.solve_btn = QPushButton("Solve")
        layout.addWidget(self.solve_btn)
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        self.setLayout(layout)
        self.solve_btn.clicked.connect(self.solveRequested.emit)

        # Load saved campaign if present
        try:
            s = settings()
            last = s.value('last_campaign')
            if last:
                d = json.loads(last)
                self.load_from_dict(d)
        except Exception:
            pass

        # Save settings when values change or when solved
        self.budget.valueChanged.connect(lambda v: self._save_settings())
        self.risk.valueChanged.connect(lambda v: self._save_settings())
        self.coverage.dial.valueChanged.connect(lambda v: self._save_settings())
        self.solve_btn.clicked.connect(self._save_settings)

    def as_dict(self) -> dict:
        return {
            'budget': float(self.budget.value()),
            'risk_max': float(self.risk.value()),
            'coverage': float(self.coverage.value()),
            'audience': self.audience.selected_filters(),
            'platforms': self.platforms.selected_platforms(),
            'platform_bounds': self.platforms.bounds(),
            'conv_value': float(self.roi.conv_value()),
        }

    def load_from_dict(self, d: dict) -> None:
        try:
            if 'budget' in d:
                self.budget.setValue(int(d['budget']))
            if 'risk_max' in d:
                self.risk.slider.setValue(int(float(d['risk_max']) * 100))
            if 'coverage' in d:
                self.coverage.dial.setValue(int(float(d['coverage']) * 100))
            if 'conv_value' in d:
                self.roi.conv.setValue(float(d['conv_value']))
            # platform selections
            if 'platforms' in d:
                p = d['platforms']
                self.platforms.ig.setChecked(p.get('IG', True))
                self.platforms.tt.setChecked(p.get('TT', True))
                self.platforms.yt.setChecked(p.get('YT', True))
                self.platforms.tw.setChecked(p.get('TW', True))
        except Exception:
            pass

    def _save_settings(self) -> None:
        try:
            s = settings()
            s.setValue('last_campaign', json.dumps(self.as_dict()))
        except Exception:
            pass


class ConstraintDock(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Constraints", parent)
        self.panel = ConstraintPanel(self)
        self.setWidget(self.panel)

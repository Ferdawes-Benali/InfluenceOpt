"""Enhanced constraint panel with visual feedback and real-time validation."""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                             QProgressBar, QDockWidget, QGroupBox, QHBoxLayout,
                             QFrame, QSizePolicy)
from PyQt5.QtCore import pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QColor, QPalette, QFont

from gui.widgets.budget_slider import BudgetSlider
from gui.widgets.risk_meter import RiskMeter


class StatusIndicator(QWidget):
    """Simple status indicator with colored circle."""
    
    def __init__(self, label: str, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create colored indicator
        self.indicator = QLabel("●")
        self.indicator.setStyleSheet("color: gray; font-size: 16pt;")
        
        # Label
        self.text = QLabel(label)
        
        layout.addWidget(self.indicator)
        layout.addWidget(self.text)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def set_status(self, status: str):
        """Set status color: 'ok', 'warning', 'error', 'info'."""
        colors = {
            'ok': 'color: #27ae60;',      # Green
            'warning': 'color: #f39c12;', # Orange
            'error': 'color: #e74c3c;',   # Red
            'info': 'color: #3498db;',    # Blue
        }
        style = colors.get(status, 'color: gray;') + ' font-size: 16pt;'
        self.indicator.setStyleSheet(style)

class MetricDisplay(QWidget):
    """Display a metric with large number and description."""
    
    def __init__(self, title: str, unit: str = "", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        self.value_label = QLabel("0")
        self.value_label.setFont(QFont('Arial', 24, QFont.Bold))
        self.value_label.setAlignment(Qt.AlignCenter)
        
        self.title_label = QLabel(title)
        self.title_label.setFont(QFont('Arial', 9))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("color: #7f8c8d;")
        
        self.unit = unit
        self.budget_status = StatusIndicator("Budget")
        layout.addWidget(self.budget_status)
        layout.addWidget(self.value_label)
        layout.addWidget(self.title_label)
        
        self.setLayout(layout)
        self.setStyleSheet("background-color: #ecf0f1; border-radius: 5px;")
    
    def set_value(self, value, color: str = None):
        """Update displayed value."""
        if isinstance(value, float):
            text = f"{value:,.2f}{self.unit}"
        elif isinstance(value, int):
            text = f"{value:,}{self.unit}"
        else:
            text = str(value)
        
        self.value_label.setText(text)
        
        if color:
            self.value_label.setStyleSheet(f"color: {color};")


class ConstraintPanel(QWidget):
    """Enhanced constraint panel with visual feedback."""
    
    solveRequested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        
        # Header
        header = QLabel("Campaign Constraints")
        header.setFont(QFont('Arial', 14, QFont.Bold))
        header.setStyleSheet("color: #2c3e50; padding: 5px;")
        main_layout.addWidget(header)
        
        # Status indicators
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout()
        
        self.budget_status = StatusIndicator("Budget")
        self.risk_status = StatusIndicator("Risk Level")
        self.coverage_status = StatusIndicator("Coverage")
        self.quality_status = StatusIndicator("Quality")
        
        status_layout.addWidget(self.budget_status)
        status_layout.addWidget(self.risk_status)
        status_layout.addWidget(self.coverage_status)
        status_layout.addWidget(self.quality_status)
        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group)
        
        # Budget & Reach
        budget_group = QGroupBox("Budget & Reach")
        budget_layout = QVBoxLayout()
        
        self.budget = BudgetSlider(maximum=100000)
        self.budget.valueChanged.connect(self._validate_constraints)
        budget_layout.addWidget(self.budget)
        
        # Budget bar
        self.budget_bar = QProgressBar()
        self.budget_bar.setMaximum(100)
        self.budget_bar.setValue(0)
        self.budget_bar.setTextVisible(True)
        self.budget_bar.setFormat("Used: %p%")
        budget_layout.addWidget(QLabel("Budget Usage:"))
        budget_layout.addWidget(self.budget_bar)
        
        budget_group.setLayout(budget_layout)
        main_layout.addWidget(budget_group)
        
        # Risk Management
        risk_group = QGroupBox("Risk Management")
        risk_layout = QVBoxLayout()
        
        self.risk = RiskMeter()
        self.risk.valueChanged.connect(self._validate_constraints)
        risk_layout.addWidget(self.risk)
        
        # Risk gauge
        self.risk_gauge = QProgressBar()
        self.risk_gauge.setMaximum(100)
        self.risk_gauge.setValue(0)
        self.risk_gauge.setTextVisible(True)
        self.risk_gauge.setFormat("Risk: %p%")
        risk_layout.addWidget(self.risk_gauge)
        
        risk_group.setLayout(risk_layout)
        main_layout.addWidget(risk_group)
        
        # Audience & Coverage
        from gui.widgets.audience_filter import AudienceFilter
        from gui.widgets.coverage_dial import CoverageDial
        
        audience_group = QGroupBox("Target Audience")
        audience_layout = QVBoxLayout()
        
        self.audience = AudienceFilter()
        self.coverage = CoverageDial()
        self.coverage.dial.valueChanged.connect(self._validate_constraints)
        
        audience_layout.addWidget(self.audience)
        audience_layout.addWidget(self.coverage)
        
        audience_group.setLayout(audience_layout)
        main_layout.addWidget(audience_group)
        
        # Platform Selection
        from gui.widgets.multi_platform import MultiPlatformBox
        
        platform_group = QGroupBox("Platforms")
        platform_layout = QVBoxLayout()
        
        self.platforms = MultiPlatformBox()
        platform_layout.addWidget(self.platforms)
        
        platform_group.setLayout(platform_layout)
        main_layout.addWidget(platform_group)
        
        # ROI Estimation
        from gui.widgets.roi_label import RoiLabel
        
        roi_group = QGroupBox("ROI Estimation")
        roi_layout = QVBoxLayout()
        
        self.roi = RoiLabel()
        roi_layout.addWidget(self.roi)
        
        # Metric displays
        metrics_row = QHBoxLayout()
        self.cost_display = MetricDisplay("Total Cost", "$")
        self.reach_display = MetricDisplay("Reach", "")
        self.roi_display = MetricDisplay("ROI", "$")
        
        metrics_row.addWidget(self.cost_display)
        metrics_row.addWidget(self.reach_display)
        metrics_row.addWidget(self.roi_display)
        
        roi_layout.addLayout(metrics_row)
        roi_group.setLayout(roi_layout)
        main_layout.addWidget(roi_group)
        
        # Solve button
        self.solve_btn = QPushButton("🚀 Optimize Campaign")
        self.solve_btn.setFont(QFont('Arial', 12, QFont.Bold))
        self.solve_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.solve_btn.clicked.connect(self.solveRequested.emit)
        main_layout.addWidget(self.solve_btn)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #27ae60;
                border-radius: 3px;
            }
        """)
        main_layout.addWidget(self.progress)
        
        # Info label
        self.info_label = QLabel("")
        self.info_label.setWordWrap(True)
        self.info_label.setFont(QFont('Arial', 9))
        self.info_label.setStyleSheet("color: #7f8c8d; padding: 5px;")
        main_layout.addWidget(self.info_label)
        
        main_layout.addStretch()
        self.setLayout(main_layout)
        
        # Load saved settings
        try:
            from utils.settings import settings
            import json
            s = settings()
            last = s.value('last_campaign')
            if last:
                d = json.loads(last)
                self.load_from_dict(d)
        except Exception:
            pass
        
        # Initial validation
        self._validate_constraints()
        
        # Auto-save timer
        self._autosave_timer = QTimer()
        self._autosave_timer.timeout.connect(self._save_settings)
        self._autosave_timer.start(5000)  # Save every 5 seconds
    
    def _validate_constraints(self):
        """Validate constraints and update status indicators."""
        # Budget status
        budget_val = self.budget.value()
        if budget_val < 1000:
            self.budget_status.set_status('warning')
            self.info_label.setText("⚠️ Budget is low. Consider increasing for better results.")
        elif budget_val > 50000:
            self.budget_status.set_status('ok')
            self.info_label.setText("✓ Budget looks good!")
        else:
            self.budget_status.set_status('ok')
            self.info_label.setText("")
        
        # Risk status
        risk_val = self.risk.value()
        if risk_val < 0.1:
            self.risk_status.set_status('ok')
        elif risk_val < 0.2:
            self.risk_status.set_status('warning')
        else:
            self.risk_status.set_status('error')
            self.info_label.setText("⚠️ High risk threshold! Results may include risky influencers.")
        
        # Coverage status
        coverage_val = self.coverage.value()
        if coverage_val < 0.6:
            self.coverage_status.set_status('warning')
        else:
            self.coverage_status.set_status('ok')
        
        # Quality status (placeholder)
        self.quality_status.set_status('info')
    
    def update_metrics(self, cost: float, reach: int, roi: float):
        """Update metric displays after solving."""
        # Update cost
        budget = self.budget.value()
        if cost > budget:
            self.cost_display.set_value(cost, "#e74c3c")
            self.budget_bar.setStyleSheet("QProgressBar::chunk { background-color: #e74c3c; }")
        else:
            self.cost_display.set_value(cost, "#27ae60")
            self.budget_bar.setStyleSheet("QProgressBar::chunk { background-color: #27ae60; }")
        
        if budget > 0:
            self.budget_bar.setValue(int(cost / budget * 100))
        
        # Update reach
        self.reach_display.set_value(reach)
        
        # Update ROI
        if roi >= 0:
            self.roi_display.set_value(roi, "#27ae60")
        else:
            self.roi_display.set_value(roi, "#e74c3c")
        
        self.roi.set_roi(roi)
    
    def as_dict(self) -> dict:
        """Export constraints as dictionary."""
        return {
            'budget': float(self.budget.value()),
            'risk_max': float(self.risk.value()),
            'coverage': float(self.coverage.value()),
            'audience': self.audience.selected_filters(),
            'platforms': self.platforms.selected_platforms(),
            'platform_bounds': self.platforms.bounds(),
            'conv_value': float(self.roi.conv_value()),
        }
    
    def load_from_dict(self, d: dict):
        """Load constraints from dictionary."""
        try:
            if 'budget' in d:
                self.budget.setValue(int(d['budget']))
            if 'risk_max' in d:
                self.risk.slider.setValue(int(float(d['risk_max']) * 100))
            if 'coverage' in d:
                self.coverage.dial.setValue(int(float(d['coverage']) * 100))
            if 'conv_value' in d:
                self.roi.conv.setValue(float(d['conv_value']))
            if 'platforms' in d:
                p = d['platforms']
                self.platforms.ig.setChecked(p.get('IG', True))
                self.platforms.tt.setChecked(p.get('TT', True))
                self.platforms.yt.setChecked(p.get('YT', True))
                self.platforms.tw.setChecked(p.get('TW', True))
        except Exception:
            pass
    
    def _save_settings(self):
        """Auto-save current settings."""
        try:
            from utils.settings import settings
            import json
            s = settings()
            s.setValue('last_campaign', json.dumps(self.as_dict()))
        except Exception:
            pass


class ConstraintDock(QDockWidget):
    """Enhanced dock widget for constraints."""
    
    def __init__(self, parent=None):
        super().__init__("Campaign Configuration", parent)
        self.panel = ConstraintPanel(self)
        self.setWidget(self.panel)
        
        # Styling
        self.setStyleSheet("""
            QDockWidget {
                font-family: Arial;
                font-size: 11pt;
            }
            QDockWidget::title {
                background-color: #34495e;
                color: white;
                padding: 8px;
                font-weight: bold;
            }
        """)
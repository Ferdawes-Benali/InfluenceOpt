"""Scenario manager GUI: list saved scenarios, compare, and export brief."""
from typing import Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QLineEdit, QListWidget, QLabel, QCheckBox, QSpinBox

from core.scenarios import ScenarioStore, Scenario
from utils.exporters import export_selection_csv, export_brief_pptx

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class ScenarioManager(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.store = ScenarioStore()

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(['Name', 'Budget', 'Reach'])
        layout.addWidget(self.table)

        btn_row = QHBoxLayout()
        self.save_btn = QPushButton('Save current')
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText('session name')
        self.save_as_btn = QPushButton('Save As...')
        self.del_btn = QPushButton('Delete selected')
        self.compare_btn = QPushButton('Compare (radar)')
        self.export_btn = QPushButton('Export brief')
        btn_row.addWidget(self.save_btn)
        btn_row.addWidget(self.name_edit)
        btn_row.addWidget(self.save_as_btn)
        btn_row.addWidget(self.del_btn)
        btn_row.addWidget(self.compare_btn)
        btn_row.addWidget(self.export_btn)
        layout.addLayout(btn_row)

        # Named sessions list & autosave controls
        subrow = QHBoxLayout()
        self.list_widget = QListWidget()
        subcol = QVBoxLayout()
        subcol.addWidget(QLabel('Saved sessions'))
        autosave_row = QHBoxLayout()
        self.autosave_cb = QCheckBox('Auto-save')
        self.autosave_interval = QSpinBox()
        self.autosave_interval.setRange(5, 3600)
        self.autosave_interval.setValue(30)
        autosave_row.addWidget(self.autosave_cb)
        autosave_row.addWidget(QLabel('interval (s)'))
        autosave_row.addWidget(self.autosave_interval)
        subcol.addLayout(autosave_row)
        # Restore history button
        self.restore_history_btn = QPushButton('Restore History')
        subcol.addWidget(self.restore_history_btn)
        subrow.addWidget(self.list_widget)
        subrow.addLayout(subcol)
        layout.addLayout(subrow)

        # Radar plot area
        self.figure = Figure(figsize=(4, 3))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.setLayout(layout)

        self.save_btn.clicked.connect(self._on_save)
        self.save_as_btn.clicked.connect(self._on_save_as)
        self.del_btn.clicked.connect(self._on_delete)
        self.compare_btn.clicked.connect(self._on_compare)
        self.export_btn.clicked.connect(self._on_export)
        self.list_widget.itemDoubleClicked.connect(self._on_load_named)
        self.autosave_cb.stateChanged.connect(self._on_autosave_changed)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._do_autosave)
        self.restore_history_btn.clicked.connect(self._open_restore_history)

        # refresh named list at startup
        self._refresh_named_list()

        # callback to get current scenario; set by parent
        self.current_getter = None  # type: Optional[callable]

    def set_current_getter(self, cb) -> None:
        self.current_getter = cb

    def _on_save(self) -> None:
        if not self.current_getter:
            QMessageBox.warning(self, "No source", "No current scenario source provided")
            return
        name, params, result = self.current_getter()
        s = Scenario(name, params, result)
        self.store.add(s)
        self._refresh_table()

    def _on_save_as(self) -> None:
        if not self.current_getter:
            QMessageBox.warning(self, "No source", "No current scenario source provided")
            return
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Name required", "Please enter a name for the session")
            return
        _, params, _ = self.current_getter()
        # save to sessions dir
        from core.scenarios import save_named_session
        from core.scenarios import get_default_appdir
        import os
        base = get_default_appdir()
        os.makedirs(base, exist_ok=True)
        # migrate any repo-local sessions into the platform app-data directory
        from core.scenarios import migrate_repo_sessions
        repo_local = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'sessions'))
        try:
            migrate_repo_sessions(repo_local, base)
        except Exception:
            pass
        target = os.path.join(base, f"{name}.json")
        if os.path.exists(target):
            rv = QMessageBox.question(self, 'Overwrite?', f"Named session '{name}' already exists. Overwrite?", QMessageBox.Yes | QMessageBox.No)
            if rv != QMessageBox.Yes:
                return
        save_named_session(self.name_edit.text().strip(), base, self.window().network_view.graph, params, self.store)
        self._refresh_named_list()

    def _refresh_named_list(self) -> None:
        from core.scenarios import list_named_sessions
        from core.scenarios import get_default_appdir
        import os
        base = get_default_appdir()
        items = list_named_sessions(base)
        self.list_widget.clear()
        for it in items:
            import time
            self.list_widget.addItem(f"{it['name']}  ({time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(it['mtime']))})")

    def _on_load_named(self, item) -> None:
        text = item.text()
        name = text.split()[0]
        from core.scenarios import load_named_session
        import os
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'sessions'))
        try:
            data = load_named_session(name, base)
            # load graph into network view
            if hasattr(self.window(), 'network_view'):
                nv = self.window().network_view
                nv.load_session({'nodes': [{'id': n, **d} for n, d in data['graph'].nodes(data=True)], 'edges': [{'source': u, 'target': v, **d} for u, v, d in data['graph'].edges(data=True)]})
            self.store = data['store']
            self._refresh_table()
        except Exception as e:
            QMessageBox.warning(self, 'Load failed', str(e))

    def _on_autosave_changed(self, state: int) -> None:
        if state:
            self._timer.start(self.autosave_interval.value() * 1000)
        else:
            self._timer.stop()

    def _do_autosave(self) -> None:
        # write autosave versioned file into sessions/ and register latest in QSettings
        if not self.current_getter:
            return
        _, params, _ = self.current_getter()
        from core.scenarios import get_default_appdir
        import os
        base = get_default_appdir()
        os.makedirs(base, exist_ok=True)
        from core.scenarios import save_versioned_autosave
        path = save_versioned_autosave(base, self.window().network_view.graph, params, self.store, max_versions=10)
        try:
            from utils.settings import settings
            s = settings()
            s.setValue('last_autosave', path)
        except Exception:
            pass

    def _open_restore_history(self) -> None:
        from .restore_history import RestoreHistoryDialog
        import os
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'sessions'))
        dlg = RestoreHistoryDialog(base, parent=self.window())
        dlg.exec_()

    def _on_delete(self) -> None:
        rows = sorted(set(i.row() for i in self.table.selectedIndexes()), reverse=True)
        for r in rows:
            self.store.remove(r)
        self._refresh_table()

    def _on_compare(self) -> None:
        indices = list(set(i.row() for i in self.table.selectedIndexes()))
        if not indices:
            QMessageBox.information(self, "Select", "Select up to 5 scenarios to compare")
            return
        metrics = self.store.compare_metrics(indices)
        self._draw_radar(metrics, indices)

    def _on_export(self) -> None:
        rows = list(set(i.row() for i in self.table.selectedIndexes()))
        if len(rows) != 1:
            QMessageBox.information(self, "Select", "Select exactly one scenario to export brief")
            return
        s = self.store.scenarios[rows[0]]
        path, _ = QFileDialog.getSaveFileName(self, "Export CSV", "scenario.csv", "CSV Files (*.csv)")
        if path:
            export_selection_csv(path, s.result.get('selected', []))
        # PPTX
        ppt_path, _ = QFileDialog.getSaveFileName(self, "Export PPTX", f"{s.name}.pptx", "PowerPoint Files (*.pptx)")
        if ppt_path:
            # ask for screenshot path
            png_path, _ = QFileDialog.getSaveFileName(self, "Save screenshot (PNG)", f"{s.name}.png", "PNG Files (*.png)")
            if png_path and hasattr(self, 'screenshot_cb') and callable(self.screenshot_cb):
                try:
                    self.screenshot_cb(png_path)
                except Exception:
                    # ignore screenshot failure; exporter will still work without an image
                    png_path = None
            export_brief_pptx(ppt_path, s, png_path)

    def _draw_radar(self, metrics, indices) -> None:
        labels = ['Budget', 'Reach', 'Risk', 'ROI']
        self.figure.clear()
        ax = self.figure.add_subplot(111, polar=True)
        N = len(labels)
        theta = [n / float(N) * 2 * 3.14159265 for n in range(N)]
        theta += theta[:1]
        for i, idx in enumerate(indices):
            vals = [metrics['budget'][i], metrics['reach'][i], metrics['risk'][i], metrics['roi'][i]]
            vals += vals[:1]
            ax.plot(theta, vals, label=self.store.scenarios[idx].name)
            ax.fill(theta, vals, alpha=0.25)
        ax.set_xticks(theta[:-1])
        ax.set_xticklabels(labels)
        ax.legend()
        self.canvas.draw()

    def _refresh_table(self) -> None:
        self.table.setRowCount(len(self.store.scenarios))
        for i, s in enumerate(self.store.scenarios):
            self.table.setItem(i, 0, QTableWidgetItem(s.name))
            self.table.setItem(i, 1, QTableWidgetItem(str(s.params.get('budget', ''))))
            self.table.setItem(i, 2, QTableWidgetItem(str(s.result.get('reach', ''))))

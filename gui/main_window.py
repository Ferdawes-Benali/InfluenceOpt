"""Main window for InfluenceOpt (skeleton)
"""
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog, QAction, QTabWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QPen
from typing import Optional

from .network_view import NetworkView


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("InfluenceOpt")
        self.resize(1200, 800)

        self._init_ui()

    def closeEvent(self, event) -> None:
        try:
            from utils.settings import settings
            s = settings()
            s.setValue('geometry', self.saveGeometry())
        except Exception:
            pass
        super().closeEvent(event)

    def _init_ui(self) -> None:
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Graph view
        self.network_tab = QWidget()
        self.network_layout = QVBoxLayout()
        self.network_view = NetworkView()
        self.network_layout.addWidget(self.network_view)
        self.network_tab.setLayout(self.network_layout)
        self.tabs.addTab(self.network_tab, "Network")

        # Scenario manager tab
        from .scenario_manager import ScenarioManager
        self.scenario_manager = ScenarioManager()
        self.scenario_manager.set_current_getter(self._get_current_scenario)
        # screenshot callback
        self.scenario_manager.screenshot_cb = lambda path: self.network_view.grab_screenshot(path)
        self.tabs.addTab(self.scenario_manager, "Scenarios")

        # Add constraints dock on left
        from .constraint_panel import ConstraintDock
        self.constraint_dock = ConstraintDock(self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.constraint_dock)
        self.constraint_dock.panel.solveRequested.connect(self._on_solve_requested)

        # Quick demo button
        demo_btn = QPushButton("Load Demo Dataset")
        demo_btn.clicked.connect(self._load_demo)
        self.network_layout.addWidget(demo_btn)

        # Solve button in toolbar
        solve_action = QAction("Solve", self)
        solve_action.triggered.connect(self._on_solve_requested)
        self.menuBar().addAction(solve_action)

        # Solve controls
        solve_btn = QPushButton("Solve")
        solve_btn.clicked.connect(self._solve)
        self.network_layout.addWidget(solve_btn)

        # Menu
        file_menu = self.menuBar().addMenu("File")
        open_action = QAction("Open dataset", self)
        open_action.triggered.connect(self._open_dataset)
        file_menu.addAction(open_action)

        help_menu = self.menuBar().addMenu("Help")
        help_action = QAction("How-to", self)
        help_action.triggered.connect(self._show_help)
        help_menu.addAction(help_action)

        # Session save/load
        save_action = QAction("Save session", self)
        save_action.triggered.connect(self._save_session)
        file_menu.addAction(save_action)
        load_action = QAction("Load session", self)
        load_action.triggered.connect(self._load_session)
        file_menu.addAction(load_action)

        # Restore geometry from settings
        try:
            from utils.settings import settings
            s = settings()
            geo = s.value('geometry')
            if geo:
                self.restoreGeometry(geo)
            # Check for autosave and offer to restore
            last_autosave = s.value('last_autosave')
            if last_autosave:
                import os
                if os.path.exists(last_autosave):
                    from PyQt5.QtWidgets import QMessageBox
                    rv = QMessageBox.question(self, 'Restore autosave', 'An autosave was found. Restore it now?')
                    if rv == QMessageBox.Yes:
                        data = __import__('core.scenarios', fromlist=['load_session']).load_session(last_autosave)
                        self.network_view.load_session({'nodes': [{'id': n, **d} for n, d in data['graph'].nodes(data=True)], 'edges': [{'source': u, 'target': v, **d} for u, v, d in data['graph'].edges(data=True)]})
                        self.constraint_dock.panel.load_from_dict(data.get('params', {}))
                        self.scenario_manager.store = data.get('store', self.scenario_manager.store)
                        self.scenario_manager._refresh_table()
        except Exception:
            pass

    def _load_demo(self) -> None:
        self.network_view.load_demo()

    def _open_dataset(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Open users csv", "", "CSV Files (*.csv)")
        if path:
            self.network_view.load_users(path)

    def _show_help(self) -> None:
        # placeholder
        pass

    def _get_current_scenario(self):
        name = 'Scenario ' + str(len(self.scenario_manager.store.scenarios) + 1)
        params = self.constraint_dock.panel.as_dict()
        # results: pick last solve result if present on worker; else empty
        result = getattr(self, 'last_result', {})
        return name, params, result

    def _save_session(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Save session", "session.json", "JSON Files (*.json)")
        if not path:
            return
        from core.scenarios import save_session
        save_session(path, self.network_view.graph, self.constraint_dock.panel.as_dict(), self.scenario_manager.store)

    def _load_session(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Load session", "", "JSON Files (*.json)")
        if not path:
            return
        from core.scenarios import load_session
        data = load_session(path)
        self.network_view.load_session({'nodes': [{'id': n, **d} for n, d in data['graph'].nodes(data=True)], 'edges': [{'source': u, 'target': v, **d} for u, v, d in data['graph'].edges(data=True)]})
        # load params into panel
        self.constraint_dock.panel.load_from_dict(data.get('params', {}))
        # load scenarios
        self.scenario_manager.store = data.get('store', self.scenario_manager.store)
        self.scenario_manager._refresh_table()

    def _on_solve_requested(self) -> None:
        params = self.constraint_dock.panel.as_dict()
        # start worker
        from .solve_worker import SolveWorker
        if hasattr(self, 'worker') and self.worker.isRunning():
            return
        self.constraint_dock.panel.progress.setVisible(True)
        self.constraint_dock.panel.progress.setValue(0)
        self.worker = SolveWorker(self.network_view.graph, params)
        self.worker.progress.connect(self.constraint_dock.panel.progress.setValue)
        self.worker.finished.connect(self._on_solve_finished)
        self.worker.start()

    def _on_solve_finished(self, result: dict) -> None:
        sel = set(result.get('selected', []))
        self.network_view.highlight_selection(sel)
        self.constraint_dock.panel.progress.setVisible(False)
        # save last result for scenario manager
        self.last_result = result
        # persist last campaign settings
        try:
            from utils.settings import settings
            s = settings()
            s.setValue('last_campaign', __import__('json').dumps(self.constraint_dock.panel.as_dict()))
        except Exception:
            pass

    def _solve(self) -> None:
        """Run a quick solve using the demo dataset and highlight selected nodes."""
        from core.graph_builder import build_graph_from_csv
        from core.optimizer import Optimizer
        import os

        base = os.path.join(os.path.dirname(__file__), '..', 'data')
        users = os.path.join(base, 'demo_users.csv')
        edges = os.path.join(base, 'demo_edges.csv')
        G = build_graph_from_csv(users, edges)
        opt = Optimizer(G)
        res = opt.solve(budget=5000, risk_max=0.2, coverage=0.5)
        selected = res.get('selected', [])
        for n in selected:
            item = self.network_view.node_items.get(n)
            if item:
                item.setBrush(QBrush(Qt.red))
                item.setPen(QPen(Qt.black, 3))
        print('Solve result (selected):', selected)

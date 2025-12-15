"""Enhanced main window with modern UI, toolbar, and improved workflow."""
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton, 
                             QFileDialog, QAction, QTabWidget, QToolBar, 
                             QStatusBar, QLabel, QMessageBox, QComboBox,
                             QActionGroup, QHBoxLayout, QSplitter)
from PyQt5.QtCore import Qt, QTimer, QSettings
from PyQt5.QtGui import QIcon, QBrush, QPen, QFont, QColor, QKeySequence
from typing import Optional
import os


class MainWindow(QMainWindow):
    """Enhanced main window with modern UI and improved workflow."""
    
    def __init__(self):
        super().__init__()
        self._create_statusbar()
        self.setWindowTitle("InfluenceOpt - Influencer Campaign Optimizer")
        self.resize(1400, 900)
        self._apply_modern_theme()
        # Apply modern theme
        #self._apply_theme()
        
        # Initialize UI
        self._init_ui()
        self._create_shortcuts()
        self._create_menus()
        self._create_toolbar()
        
        # Restore geometry
        self._restore_settings()
                
        # Auto-save timer
        self._autosave_timer = QTimer()
        self._autosave_timer.timeout.connect(self._do_autosave)
        self._autosave_timer.start(30000)  # Every 30 seconds
    def _apply_modern_theme(self):
        """Apply modern dark theme for better visuals."""
        self.setStyleSheet("""
            /* Main Window */
            QMainWindow {
                background-color: #2c3e50;
            }
            
            /* General Widget Styling */
            QWidget {
                background-color: #34495e;
                color: #ecf0f1;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 10pt;
            }
            
            /* Tabs */
            QTabWidget::pane {
                border: 2px solid #1abc9c;
                background-color: #2c3e50;
            }
            
            QTabBar::tab {
                background-color: #34495e;
                color: #ecf0f1;
                padding: 8px 20px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            
            QTabBar::tab:selected {
                background-color: #1abc9c;
                color: white;
            }
            
            QTabBar::tab:hover {
                background-color: #16a085;
            }
            
            /* Buttons */
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #2980b9;
            }
            
            QPushButton:pressed {
                background-color: #21618c;
            }
            
            /* GroupBox */
            QGroupBox {
                border: 2px solid #1abc9c;
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
                padding: 10px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            
            /* Sliders */
            QSlider::groove:horizontal {
                height: 8px;
                background: #7f8c8d;
                border-radius: 4px;
            }
            
            QSlider::handle:horizontal {
                background: #1abc9c;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            
            QSlider::handle:horizontal:hover {
                background: #16a085;
            }
            
            /* Progress Bar */
            QProgressBar {
                border: 2px solid #7f8c8d;
                border-radius: 5px;
                text-align: center;
                background-color: #34495e;
            }
            
            QProgressBar::chunk {
                background-color: #1abc9c;
                border-radius: 3px;
            }
            
            /* Labels */
            QLabel {
                color: #ecf0f1;
            }
        """)

    def _apply_theme(self):
        """Apply modern dark/light theme."""
        # You can toggle between themes
        self.dark_mode = True
        
        if self.dark_mode:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #2c3e50;
                }
                QWidget {
                    background-color: #34495e;
                    color: #ecf0f1;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-size: 10pt;
                }
                QTabWidget::pane {
                    border: 1px solid #1abc9c;
                    background-color: #2c3e50;
                }
                QTabBar::tab {
                    background-color: #34495e;
                    color: #ecf0f1;
                    padding: 8px 20px;
                    margin-right: 2px;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                }
                QTabBar::tab:selected {
                    background-color: #1abc9c;
                    color: white;
                }
                QTabBar::tab:hover {
                    background-color: #16a085;
                }
                QGroupBox {
                    border: 2px solid #1abc9c;
                    border-radius: 5px;
                    margin-top: 10px;
                    font-weight: bold;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                }
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                QPushButton:pressed {
                    background-color: #21618c;
                }
                QSlider::groove:horizontal {
                    height: 8px;
                    background: #7f8c8d;
                    border-radius: 4px;
                }
                QSlider::handle:horizontal {
                    background: #1abc9c;
                    width: 18px;
                    margin: -5px 0;
                    border-radius: 9px;
                }
                QSlider::handle:horizontal:hover {
                    background: #16a085;
                }
                QProgressBar {
                    border: 2px solid #7f8c8d;
                    border-radius: 5px;
                    text-align: center;
                    background-color: #34495e;
                }
                QProgressBar::chunk {
                    background-color: #1abc9c;
                    border-radius: 3px;
                }
                QToolBar {
                    background-color: #34495e;
                    border: 1px solid #1abc9c;
                    spacing: 5px;
                    padding: 5px;
                }
                QStatusBar {
                    background-color: #2c3e50;
                    color: #ecf0f1;
                    border-top: 1px solid #1abc9c;
                }
                QMenuBar {
                    background-color: #34495e;
                    color: #ecf0f1;
                }
                QMenuBar::item:selected {
                    background-color: #1abc9c;
                }
                QMenu {
                    background-color: #34495e;
                    color: #ecf0f1;
                }
                QMenu::item:selected {
                    background-color: #1abc9c;
                }
            """)
        else:
            # Light theme
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #ecf0f1;
                }
                QWidget {
                    background-color: white;
                    color: #2c3e50;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-size: 10pt;
                }
                /* Add light theme styles here */
            """)
    
    def _init_ui(self):
        """Initialize main UI components."""
        # Central widget with tabs
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.setCentralWidget(self.tabs)
        
        # Network view tab
        self.network_tab = QWidget()
        network_layout = QVBoxLayout()
        
        # Import enhanced network view
        from gui.network_view import NetworkView
        self.network_view = NetworkView()
        
        # Layout controls
        layout_controls = QHBoxLayout()
        layout_label = QLabel("Layout:")
        layout_label.setStyleSheet("font-weight: bold;")
        self.layout_combo = QComboBox()
        self.layout_combo.addItems(['Spring', 'Circular', 'Kamada-Kawai', 'Community'])
        self.layout_combo.currentTextChanged.connect(self._on_layout_changed)
        
        zoom_label = QLabel("Zoom:")
        self.zoom_reset_btn = QPushButton("Reset View")
        self.zoom_reset_btn.clicked.connect(self._reset_view)
        
        layout_controls.addWidget(layout_label)
        layout_controls.addWidget(self.layout_combo)
        layout_controls.addStretch()
        layout_controls.addWidget(zoom_label)
        layout_controls.addWidget(self.zoom_reset_btn)
        
        network_layout.addLayout(layout_controls)
        network_layout.addWidget(self.network_view)
        
        self.network_tab.setLayout(network_layout)
        self.tabs.addTab(self.network_tab, "🌐 Network View")
        
        # Scenario manager tab
        from gui.scenario_manager import ScenarioManager
        self.scenario_manager = ScenarioManager()
        self.scenario_manager.set_current_getter(self._get_current_scenario)
        self.scenario_manager.screenshot_cb = lambda path: self.network_view.grab_screenshot(path)
        self.tabs.addTab(self.scenario_manager, "📊 Scenarios")
        
        # Add enhanced constraints dock
        from gui.constraint_panel import ConstraintDock
        self.constraint_dock = ConstraintDock(self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.constraint_dock)
        self.constraint_dock.panel.solveRequested.connect(self._on_solve_requested)
        self._create_statusbar()
        
    def _create_menus(self):
        """Create menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_action = QAction("&New Campaign", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self._new_campaign)
        file_menu.addAction(new_action)
        
        open_action = QAction("&Open Dataset...", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self._open_dataset)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        save_action = QAction("&Save Session", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self._save_session)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save Session &As...", self)
        save_as_action.setShortcut(QKeySequence.SaveAs)
        save_as_action.triggered.connect(self._save_session_as)
        file_menu.addAction(save_as_action)
        
        load_action = QAction("&Load Session...", self)
        load_action.triggered.connect(self._load_session)
        file_menu.addAction(load_action)
        
        file_menu.addSeparator()
        
        export_menu = file_menu.addMenu("&Export")
        export_csv_action = QAction("Export as &CSV...", self)
        export_csv_action.triggered.connect(self._export_csv)
        export_menu.addAction(export_csv_action)
        
        export_pptx_action = QAction("Export as &PowerPoint...", self)
        export_pptx_action.triggered.connect(self._export_pptx)
        export_menu.addAction(export_pptx_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        prefs_action = QAction("&Preferences", self)
        prefs_action.triggered.connect(self._show_preferences)
        edit_menu.addAction(prefs_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        theme_group = QActionGroup(self)
        dark_theme_action = QAction("&Dark Theme", self, checkable=True)
        dark_theme_action.setChecked(self.dark_mode)
        dark_theme_action.triggered.connect(lambda: self._toggle_theme(True))
        theme_group.addAction(dark_theme_action)
        view_menu.addAction(dark_theme_action)
        
        light_theme_action = QAction("&Light Theme", self, checkable=True)
        light_theme_action.setChecked(not self.dark_mode)
        light_theme_action.triggered.connect(lambda: self._toggle_theme(False))
        theme_group.addAction(light_theme_action)
        view_menu.addAction(light_theme_action)
        
        view_menu.addSeparator()
        
        toggle_constraints_action = QAction("Show/Hide &Constraints", self)
        toggle_constraints_action.triggered.connect(
            lambda: self.constraint_dock.setVisible(not self.constraint_dock.isVisible()))
        view_menu.addAction(toggle_constraints_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        optimize_action = QAction("&Optimize Campaign", self)
        optimize_action.setShortcut("Ctrl+R")
        optimize_action.triggered.connect(self._on_solve_requested)
        tools_menu.addAction(optimize_action)
        
        robustness_action = QAction("&Robustness Analysis", self)
        robustness_action.triggered.connect(self._run_robustness)
        tools_menu.addAction(robustness_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        demo_action = QAction("Load &Demo Dataset", self)
        demo_action.triggered.connect(self._load_demo)
        help_menu.addAction(demo_action)
        
        help_menu.addSeparator()
        
        howto_action = QAction("&How to Use", self)
        howto_action.setShortcut(QKeySequence.HelpContents)
        howto_action.triggered.connect(self._show_help)
        help_menu.addAction(howto_action)
        
        about_action = QAction("&About InfluenceOpt", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _create_toolbar(self):
        """Create toolbar with quick actions."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(Qt.ToolBarIconArea)
        self.addToolBar(toolbar)
        
        # Quick actions
        demo_btn = QPushButton("📁 Load Demo")
        demo_btn.setToolTip("Load demo dataset")
        demo_btn.clicked.connect(self._load_demo)
        toolbar.addWidget(demo_btn)
        
        toolbar.addSeparator()
        
        solve_btn = QPushButton("🚀 Optimize")
        solve_btn.setToolTip("Run optimization (Ctrl+R)")
        solve_btn.clicked.connect(self._on_solve_requested)
        solve_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                font-size: 11pt;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        toolbar.addWidget(solve_btn)
        
        toolbar.addSeparator()
        
        save_scenario_btn = QPushButton("💾 Save Scenario")
        save_scenario_btn.clicked.connect(self._save_current_scenario)
        toolbar.addWidget(save_scenario_btn)
        
        toolbar.addSeparator()
        
        export_btn = QPushButton("📤 Export")
        export_btn.clicked.connect(self._export_csv)
        toolbar.addWidget(export_btn)
    
    def _create_statusbar(self):
        """Create enhanced status bar with node/edge counts."""
        from PyQt5.QtWidgets import QStatusBar, QLabel
        
        statusbar = QStatusBar()
        self.setStatusBar(statusbar)
        
        # Main status message
        self.status_msg = QLabel("Ready")
        statusbar.addWidget(self.status_msg)
        
        # Node count
        self.node_count = QLabel("Nodes: 0")
        statusbar.addPermanentWidget(self.node_count)
        
        # Edge count  
        self.edge_count = QLabel("Edges: 0")
        statusbar.addPermanentWidget(self.edge_count)
        
        # Style it
        statusbar.setStyleSheet("""
            QStatusBar {
                background-color: #2c3e50;
                color: #ecf0f1;
                border-top: 2px solid #1abc9c;
            }
        """)

    def _update_status_counts(self):
        """Update node and edge counts in status bar."""
        if hasattr(self, 'network_view'):
            n = self.network_view.graph.number_of_nodes()
            e = self.network_view.graph.number_of_edges()
            self.node_count.setText(f"Nodes: {n}")
            self.edge_count.setText(f"Edges: {e}")
        
    def _update_stats(self):
        """Update statistics in status bar."""
        if hasattr(self, 'network_view'):
            n_nodes = self.network_view.graph.number_of_nodes()
            n_edges = self.network_view.graph.number_of_edges()
            self.node_count_label.setText(f"Nodes: {n_nodes}")
            self.edge_count_label.setText(f"Edges: {n_edges}")
    
    def _on_layout_changed(self, layout_name: str):
        """Handle layout algorithm change."""
        algo_map = {
            'Spring': 'spring',
            'Circular': 'circular',
            'Kamada-Kawai': 'kamada_kawai',
            'Community': 'community'
        }
        self.network_view.set_layout_algorithm(algo_map.get(layout_name, 'spring'))
    
    def _reset_view(self):
        """Reset view to fit all nodes."""
        self.network_view.fitInView(
            self.network_view.scene().itemsBoundingRect(), 
            Qt.KeepAspectRatio
        )
    
    def _load_demo(self):
        """Load demo dataset."""
        self.network_view.load_demo()
        self._update_status_counts()
        self._update_stats()
        self.status_label.setText("Demo dataset loaded")
        QTimer.singleShot(3000, lambda: self.status_label.setText("Ready"))
    
    def _new_campaign(self):
        """Create new campaign."""
        reply = QMessageBox.question(
            self, 'New Campaign',
            'Clear current campaign and start fresh?',
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.network_view.graph.clear()
            self.network_view._layout_and_draw()
            self._update_status_counts()
            self._update_stats()
            self.status_label.setText("New campaign started")
    
    def _open_dataset(self):
        """Open dataset from CSV files."""
        users_path, _ = QFileDialog.getOpenFileName(
            self, "Open Users CSV", "", "CSV Files (*.csv)"
        )
        if users_path:
            self.network_view.load_users(users_path)
            self._update_status_counts()
            edges_path, _ = QFileDialog.getOpenFileName(
                self, "Open Edges CSV", "", "CSV Files (*.csv)"
            )
            if edges_path:
                self.network_view.load_edges(edges_path)
                self._update_status_counts()
            self.network_view._layout_and_draw()
            self._update_status_counts()
            self._update_stats()
            self.status_label.setText("Dataset loaded")
    
    def _save_session(self):
        """Quick save session."""
        if hasattr(self, '_current_session_path'):
            self._do_save_session(self._current_session_path)
        else:
            self._save_session_as()
    
    def _save_session_as(self):
        """Save session as new file."""
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Session", "campaign.json", "JSON Files (*.json)"
        )
        if path:
            self._do_save_session(path)
            self._current_session_path = path
    
    def _do_save_session(self, path: str):
        """Actually save the session."""
        from core.scenarios import save_session
        try:
            save_session(
                path, 
                self.network_view.graph,
                self.constraint_dock.panel.as_dict(),
                self.scenario_manager.store
            )
            self.status_label.setText(f"Session saved: {os.path.basename(path)}")
            QTimer.singleShot(3000, lambda: self.status_label.setText("Ready"))
        except Exception as e:
            QMessageBox.warning(self, "Save Error", f"Failed to save: {str(e)}")
    
    def _load_session(self):
        """Load session from file."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Session", "", "JSON Files (*.json)"
        )
        if path:
            from core.scenarios import load_session
            try:
                data = load_session(path)
                self.network_view.load_session({
                    'nodes': [{'id': n, **d} for n, d in data['graph'].nodes(data=True)],
                    'edges': [{'source': u, 'target': v, **d} for u, v, d in data['graph'].edges(data=True)]
                })
                self.constraint_dock.panel.load_from_dict(data.get('params', {}))
                self.scenario_manager.store = data.get('store', self.scenario_manager.store)
                self.scenario_manager._refresh_table()
                self._current_session_path = path
                self._update_stats()
                self.status_label.setText(f"Session loaded: {os.path.basename(path)}")
            except Exception as e:
                QMessageBox.warning(self, "Load Error", f"Failed to load: {str(e)}")
    
    def _do_autosave(self):
        """Perform automatic save."""
        try:
            from core.scenarios import save_versioned_autosave, get_default_appdir
            base = get_default_appdir()
            path = save_versioned_autosave(
                base,
                self.network_view.graph,
                self.constraint_dock.panel.as_dict(),
                self.scenario_manager.store
            )
            from utils.settings import settings
            s = settings()
            s.setValue('last_autosave', path)
        except Exception:
            pass
    
    def _on_solve_requested(self):
        """Handle solve request."""
        params = self.constraint_dock.panel.as_dict()
        
        from gui.solve_worker import SolveWorker
        if hasattr(self, 'worker') and self.worker.isRunning():
            QMessageBox.information(self, "Busy", "Optimization already running")
            return
        
        self.constraint_dock.panel.progress.setVisible(True)
        self.constraint_dock.panel.progress.setValue(0)
        self.constraint_dock.panel.solve_btn.setEnabled(False)
        self.status_label.setText("Optimizing...")
        
        self.worker = SolveWorker(self.network_view.graph, params)
        self.worker.progress.connect(self.constraint_dock.panel.progress.setValue)
        self.worker.finished.connect(self._on_solve_finished)
        self.worker.start()
    
    def _on_solve_finished(self, result: dict):
        """Handle solve completion."""
        selected = set(result.get('selected', []))
        
        # Calculate reached followers
        reached = set(selected)
        for n in selected:
            for neighbor in self.network_view.graph.neighbors(n):
                reached.add(neighbor)
        
        self.network_view.highlight_selection(selected, reached)
        
        # Update metrics
        cost = result.get('total_cost', 0)
        reach = result.get('reached_followers', 0)
        roi = result.get('roi', 0)
        
        self.constraint_dock.panel.update_metrics(cost, reach, roi)
        
        self.constraint_dock.panel.progress.setVisible(False)
        self.constraint_dock.panel.solve_btn.setEnabled(True)
        
        self.last_result = result
        
        # Show summary
        self.status_label.setText(
            f"✓ Optimized: {len(selected)} influencers, {reach:,} reach, ROI: ${roi:,.2f}"
        )
        
        QMessageBox.information(
            self, "Optimization Complete",
            f"Selected {len(selected)} influencers\n"
            f"Estimated reach: {reach:,}\n"
            f"Total cost: ${cost:,.2f}\n"
            f"ROI: ${roi:,.2f}"
        )
    
    def _run_robustness(self):
        """Run Monte Carlo robustness analysis."""
        if not hasattr(self, 'last_result') or not self.last_result.get('selected'):
            QMessageBox.warning(self, "No Solution", "Please run optimization first")
            return
        
        from core.optimizer import Optimizer
        opt = Optimizer(self.network_view.graph)
        
        self.status_label.setText("Running robustness analysis...")
        results = opt.monte_carlo_robustness(self.last_result['selected'], trials=100)
        
        # Show results
        import statistics
        mean_reach = statistics.mean(results)
        std_reach = statistics.stdev(results) if len(results) > 1 else 0
        
        QMessageBox.information(
            self, "Robustness Analysis",
            f"Monte Carlo Simulation (100 trials)\n\n"
            f"Mean reach: {mean_reach:,.0f}\n"
            f"Std deviation: {std_reach:,.0f}\n"
            f"Min reach: {min(results):,}\n"
            f"Max reach: {max(results):,}"
        )
        
        self.status_label.setText("Ready")
    
    def _save_current_scenario(self):
        """Save current state as scenario."""
        self.scenario_manager._on_save()
        self.status_label.setText("Scenario saved")
    
    def _get_current_scenario(self):
        """Get current scenario data."""
        name = f'Scenario {len(self.scenario_manager.store.scenarios) + 1}'
        params = self.constraint_dock.panel.as_dict()
        result = getattr(self, 'last_result', {})
        return name, params, result
    
    def _export_csv(self):
        """Export selection to CSV."""
        if not hasattr(self, 'last_result') or not self.last_result.get('selected'):
            QMessageBox.warning(self, "No Solution", "Please run optimization first")
            return
        
        path, _ = QFileDialog.getSaveFileName(
            self, "Export CSV", "selection.csv", "CSV Files (*.csv)"
        )
        if path:
            from utils.exporters import export_selection_csv
            export_selection_csv(path, self.last_result['selected'])
            self.status_label.setText(f"Exported to {os.path.basename(path)}")
    
    def _export_pptx(self):
        """Export brief to PowerPoint."""
        if not hasattr(self, 'last_result'):
            QMessageBox.warning(self, "No Solution", "Please run optimization first")
            return
        
        path, _ = QFileDialog.getSaveFileName(
            self, "Export PowerPoint", "brief.pptx", "PowerPoint Files (*.pptx)"
        )
        if path:
            from utils.exporters import export_brief_pptx
            from core.scenarios import Scenario
            
            # Create temporary screenshot
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                tmp_path = tmp.name
                self.network_view.grab_screenshot(tmp_path)
            
            s = Scenario(
                'Current Campaign',
                self.constraint_dock.panel.as_dict(),
                self.last_result
            )
            
            try:
                export_brief_pptx(path, s, tmp_path)
                self.status_label.setText(f"Exported to {os.path.basename(path)}")
            except Exception as e:
                QMessageBox.warning(self, "Export Error", str(e))
            finally:
                try:
                    os.remove(tmp_path)
                except:
                    pass
    
    def _show_preferences(self):
        """Show preferences dialog."""
        QMessageBox.information(self, "Preferences", "Preferences dialog coming soon!")
    
    def _toggle_theme(self, dark: bool):
        """Toggle between dark and light theme."""
        self.dark_mode = dark
        self._apply_theme()
    
    def _show_help(self):
        """Show help dialog."""
        help_text = """
        <h2>InfluenceOpt - Quick Guide</h2>
        
        <h3>Getting Started</h3>
        <ol>
        <li>Load demo dataset or import your own CSV files</li>
        <li>Adjust constraints in the left panel</li>
        <li>Click "Optimize Campaign" to find best influencers</li>
        <li>Review results and save scenarios</li>
        </ol>
        
        <h3>Keyboard Shortcuts</h3>
        <ul>
        <li><b>Ctrl+N</b> - New campaign</li>
        <li><b>Ctrl+O</b> - Open dataset</li>
        <li><b>Ctrl+S</b> - Save session</li>
        <li><b>Ctrl+R</b> - Run optimization</li>
        <li><b>F1</b> - This help</li>
        </ul>
        
        <h3>Tips</h3>
        <ul>
        <li>Use mouse wheel to zoom in/out on network view</li>
        <li>Drag nodes to rearrange layout</li>
        <li>Right-click nodes to edit properties</li>
        <li>Hover over nodes to see details</li>
        </ul>
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle("How to Use InfluenceOpt")
        msg.setTextFormat(Qt.RichText)
        msg.setText(help_text)
        msg.exec_()
    
    def _show_about(self):
        """Show about dialog."""
        about_text = """
        <h2>InfluenceOpt</h2>
        <p><b>Version 1.0</b></p>
        
        <p>Advanced influencer campaign optimization tool using
        mixed-integer programming and network analysis.</p>
        
        <p><b>Features:</b></p>
        <ul>
        <li>Budget and risk-constrained optimization</li>
        <li>Multi-platform support (IG, TT, YT, TW)</li>
        <li>Interactive network visualization</li>
        <li>Monte Carlo robustness analysis</li>
        <li>Scenario comparison and export</li>
        </ul>
        
        <p>Built with PyQt5, NetworkX, and Gurobi</p>
        """
        
        QMessageBox.about(self, "About InfluenceOpt", about_text)
    
    def _restore_settings(self):
        """Restore window geometry and settings."""
        try:
            from utils.settings import settings
            s = settings()
            geo = s.value('geometry')
            if geo:
                self.restoreGeometry(geo)
        except Exception:
            pass
    
    def closeEvent(self, event):
        """Handle window close."""
        try:
            from utils.settings import settings
            s = settings()
            s.setValue('geometry', self.saveGeometry())
        except Exception:
            pass
        
        # Confirm if unsaved changes
        reply = QMessageBox.question(
            self, 'Exit',
            'Exit InfluenceOpt?',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
    def _create_shortcuts(self):
        """Create keyboard shortcuts."""
        from PyQt5.QtWidgets import QShortcut
        from PyQt5.QtGui import QKeySequence
        
        # Ctrl+R to run optimization
        solve_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        solve_shortcut.activated.connect(self._on_solve_requested)
        
        # Ctrl+S to save
        save_shortcut = QShortcut(QKeySequence.Save, self)
        save_shortcut.activated.connect(self._save_session)
        
        # Ctrl+O to open
        open_shortcut = QShortcut(QKeySequence.Open, self)
        open_shortcut.activated.connect(self._open_dataset)
        
        # F5 to refresh view
        refresh_shortcut = QShortcut(QKeySequence.Refresh, self)
        refresh_shortcut.activated.connect(
            lambda: self.network_view.fitInView(
                self.network_view.scene().itemsBoundingRect(), 
                Qt.KeepAspectRatio
            )
        )
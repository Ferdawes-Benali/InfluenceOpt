"""Dialog to show autosave history and allow restore/delete."""
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListWidget, QPushButton, QHBoxLayout, QMessageBox, QInputDialog
from PyQt5.QtCore import Qt
from typing import Optional

from core.scenarios import list_autosave_versions, load_session


class RestoreHistoryDialog(QDialog):
    def __init__(self, sessions_dir: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Restore History')
        self.resize(600, 400)
        self.sessions_dir = sessions_dir
        layout = QVBoxLayout()
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        row = QHBoxLayout()
        self.restore_btn = QPushButton('Restore')
        self.delete_btn = QPushButton('Delete')
        self.export_btn = QPushButton('Export as Named Session')
        self.close_btn = QPushButton('Close')
        row.addWidget(self.restore_btn)
        row.addWidget(self.delete_btn)
        row.addWidget(self.export_btn)
        row.addWidget(self.close_btn)
        layout.addLayout(row)
        self.setLayout(layout)

        self.restore_btn.clicked.connect(self._on_restore)
        self.delete_btn.clicked.connect(self._on_delete)
        self.export_btn.clicked.connect(self._on_export_named)
        self.close_btn.clicked.connect(self.accept)

        self._refresh()

    def _refresh(self) -> None:
        self.list_widget.clear()
        items = list_autosave_versions(self.sessions_dir)
        for it in items:
            import time
            ts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(it['mtime']))
            self.list_widget.addItem(f"{it['name']} — {ts}")

    def _selected_path(self) -> Optional[str]:
        it = self.list_widget.currentItem()
        if not it:
            return None
        name = it.text().split()[0]
        items = list_autosave_versions(self.sessions_dir)
        for x in items:
            if x['name'] == name:
                return x['path']
        return None

    def _on_restore(self) -> None:
        path = self._selected_path()
        if not path:
            QMessageBox.information(self, 'Select', 'Select a version to restore')
            return
        try:
            data = load_session(path)
        except Exception as e:
            QMessageBox.warning(self, 'Load failed', str(e))
            return
        # set loaded data on parent
        if self.parent() and hasattr(self.parent(), 'network_view'):
            nv = self.parent().network_view
            nv.load_session({'nodes': [{'id': n, **d} for n, d in data['graph'].nodes(data=True)], 'edges': [{'source': u, 'target': v, **d} for u, v, d in data['graph'].edges(data=True)]})
            self.parent().constraint_dock.panel.load_from_dict(data.get('params', {}))
            self.parent().scenario_manager.store = data.get('store', self.parent().scenario_manager.store)
            self.parent().scenario_manager._refresh_table()
        QMessageBox.information(self, 'Restored', 'Session restored')

    def _on_delete(self) -> None:
        path = self._selected_path()
        if not path:
            QMessageBox.information(self, 'Select', 'Select a version to delete')
            return
        import os
        try:
            os.remove(path)
        except Exception as e:
            QMessageBox.warning(self, 'Delete failed', str(e))
        self._refresh()

    def _on_export_named(self) -> None:
        path = self._selected_path()
        if not path:
            QMessageBox.information(self, 'Select', 'Select a version to export')
            return
        try:
            data = load_session(path)
        except Exception as e:
            QMessageBox.warning(self, 'Load failed', str(e))
            return
        # ask for a name
        name, ok = QInputDialog.getText(self, 'Export named session', 'Session name:')
        if not ok or not name.strip():
            QMessageBox.information(self, 'Name required', 'A name is required to save a named session')
            return
        from core.scenarios import save_named_session, get_default_appdir
        import os
        base = self.sessions_dir or get_default_appdir()
        target = os.path.join(base, f"{name.strip()}.json")
        if os.path.exists(target):
            rv = QMessageBox.question(self, 'Overwrite?', f"Named session '{name.strip()}' already exists. Overwrite?", QMessageBox.Yes | QMessageBox.No)
            if rv != QMessageBox.Yes:
                return
        try:
            save_named_session(name.strip(), base, data['graph'], data['params'], data['store'])
        except Exception as e:
            QMessageBox.warning(self, 'Save failed', str(e))
            return
        # refresh named list in the parent UI if available
        if self.parent() and hasattr(self.parent(), 'scenario_manager') and hasattr(self.parent().scenario_manager, '_refresh_named_list'):
            try:
                self.parent().scenario_manager._refresh_named_list()
            except Exception:
                pass
        QMessageBox.information(self, 'Saved', f'Named session "{name.strip()}" saved')
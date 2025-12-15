import os
import types
import pytest
from PyQt5.QtWidgets import QApplication, QMessageBox

from core.scenarios import save_named_session, list_named_sessions


def ensure_qapp():
    app = QApplication.instance()
    if not app:
        app = QApplication([])
    return app


def test_scenario_manager_save_as_overwrite(tmp_path, monkeypatch):
    ensure_qapp()
    from gui.scenario_manager import ScenarioManager
    import os
    # prepare base sessions dir used by ScenarioManager (override to temp dir)
    base = str(tmp_path)
    import os
    os.environ['INFLUENCEOPT_SESSIONS_DIR'] = base
    os.makedirs(base, exist_ok=True)
    # create an existing named file
    name = 'existing'
    existing_path = os.path.join(base, f"{name}.json")
    with open(existing_path, 'w', encoding='utf-8') as f:
        f.write('{"dummy":1}')
    # create manager and set name
    mgr = ScenarioManager()
    mgr.name_edit.setText(name)
    # set a current_getter so it doesn't early-exit
    mgr.set_current_getter(lambda: (name, {}, {}))
    called = {'saved': False}
    def fake_save_named(name_arg, base_arg, graph, params, store):
        called['saved'] = True
    monkeypatch.setattr('core.scenarios.save_named_session', fake_save_named)
    # simulate user cancelling overwrite
    monkeypatch.setattr(QMessageBox, 'question', lambda *a, **k: QMessageBox.No)
    mgr._on_save_as()
    assert not called['saved']
    # simulate user confirming overwrite
    monkeypatch.setattr(QMessageBox, 'question', lambda *a, **k: QMessageBox.Yes)
    mgr._on_save_as()
    assert called['saved']


def test_restore_history_export_overwrite(tmp_path, monkeypatch):
    ensure_qapp()
    from gui.restore_history import RestoreHistoryDialog
    from core.scenarios import save_versioned_autosave, list_autosave_versions, load_session
    import os
    base = str(tmp_path)
    # create autosave
    import networkx as nx
    G = nx.Graph()
    G.add_node('a', followers=100)
    params = {'budget': 10}
    from core.scenarios import ScenarioStore, Scenario
    store = ScenarioStore()
    store.add(Scenario('s', params, {'selected': [], 'reach': 0}))
    save_versioned_autosave(base, G, params, store)
    files = list_autosave_versions(base)
    assert files
    dlg = RestoreHistoryDialog(base, parent=None)
    # simulate selecting the first item
    dlg.list_widget.setCurrentRow(0)
    # simulate input name
    monkeypatch.setattr('PyQt5.QtWidgets.QInputDialog.getText', lambda *a, **k: ('same', True))
    # create an existing named session file
    existing_path = os.path.join(base, 'same.json')
    with open(existing_path, 'w', encoding='utf-8') as f:
        f.write('{"x":1}')
    called = {'saved': False}
    def fake_save_named(name_arg, base_arg, graph, params, store_arg):
        called['saved'] = True
    monkeypatch.setattr('core.scenarios.save_named_session', fake_save_named)
    # user cancels overwrite
    monkeypatch.setattr(QMessageBox, 'question', lambda *a, **k: QMessageBox.No)
    dlg._on_export_named()
    assert not called['saved']
    # user confirms overwrite
    monkeypatch.setattr(QMessageBox, 'question', lambda *a, **k: QMessageBox.Yes)
    dlg._on_export_named()
    assert called['saved']
import os
import networkx as nx
from core.scenarios import save_versioned_autosave, list_autosave_versions, load_session, save_named_session, list_named_sessions, load_named_session
from core.scenarios import ScenarioStore, Scenario
import os
import networkx as nx
from core.scenarios import save_versioned_autosave, list_autosave_versions, load_session, save_named_session, list_named_sessions, load_named_session
from core.scenarios import ScenarioStore, Scenario


def test_export_autosave_to_named_session(tmp_path):
    base = str(tmp_path)
    # build a simple graph and store
    G = nx.Graph()
    G.add_node('a', followers=100)
    params = {'budget': 10}
    store = ScenarioStore()
    store.add(Scenario('s', params, {'selected': [], 'reach': 0}))
    # create an autosave
    p = save_versioned_autosave(base, G, params, store, max_versions=5)
    files = list_autosave_versions(base)
    assert len(files) >= 1
    path = files[0]['path']
    data = load_session(path)
    # export to named session
    name = 'exported-session'
    saved_path = save_named_session(name, base, data['graph'], data['params'], data['store'])
    assert os.path.exists(saved_path)
    items = list_named_sessions(base)
    names = [it['name'] for it in items]
    assert name in names
    # load it back
    loaded = load_named_session(name, base)
    assert 'a' in loaded['graph'].nodes()
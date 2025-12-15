import os
import networkx as nx
from core.scenarios import save_named_session, list_named_sessions, load_named_session, ScenarioStore, Scenario


def test_named_session_roundtrip(tmp_path):
    base = str(tmp_path)
    G = nx.Graph()
    G.add_node('a', followers=1000, cost=10)
    G.add_node('b', followers=2000, cost=50)
    G.add_edge('a', 'b', prob=0.8)
    params = {'budget': 1000}
    store = ScenarioStore()
    store.add(Scenario('s', params, {'selected': ['a'], 'reach': 1000}))
    path = save_named_session('test1', base, G, params, store)
    assert os.path.exists(path)
    items = list_named_sessions(base)
    assert any(it['name'] == 'test1' for it in items)
    data = load_named_session('test1', base)
    assert isinstance(data['graph'], nx.Graph)
    assert data['params']['budget'] == 1000

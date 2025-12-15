import json
import networkx as nx
from core.scenarios import make_session_dict, save_session, load_session, ScenarioStore, Scenario


def test_session_roundtrip(tmp_path):
    G = nx.Graph()
    G.add_node('a', followers=1000, cost=10)
    G.add_node('b', followers=2000, cost=50)
    G.add_edge('a', 'b', prob=0.8)
    params = {'budget': 1000, 'risk_max': 0.2}
    store = ScenarioStore()
    store.add(Scenario('s', params, {'selected': ['a'], 'reach': 1000}))
    p = tmp_path / 'sess.json'
    save_session(str(p), G, params, store)
    d = load_session(str(p))
    assert isinstance(d['graph'], nx.Graph)
    assert d['params']['budget'] == 1000
    assert len(d['store'].scenarios) == 1
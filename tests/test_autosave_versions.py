import os
import time
import networkx as nx
from core.scenarios import save_versioned_autosave, list_autosave_versions


def test_versioned_autosave_prune(tmp_path):
    base = str(tmp_path)
    G = nx.Graph()
    G.add_node('a', followers=100)
    params = {'budget': 10}
    from core.scenarios import ScenarioStore, Scenario
    store = ScenarioStore()
    store.add(Scenario('s', params, {'selected': [], 'reach': 0}))
    # create 7 autosaves with max_versions=5
    paths = []
    for i in range(7):
        p = save_versioned_autosave(base, G, params, store, max_versions=5)
        paths.append(p)
        time.sleep(0.01)
    files = list_autosave_versions(base)
    # should keep at most 5
    assert len(files) <= 5
    # latest file should be last created
    assert os.path.basename(paths[-1]) == files[0]['name']
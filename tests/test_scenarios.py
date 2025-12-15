from core.scenarios import ScenarioStore, Scenario


def test_store_serialize_roundtrip(tmp_path):
    store = ScenarioStore()
    s = Scenario('s1', {'budget': 100}, {'selected': ['a'], 'reach': 1000, 'roi': 200})
    store.add(s)
    p = tmp_path / "sc.json"
    store.save_to_file(str(p))
    st2 = ScenarioStore()
    st2.load_from_file(str(p))
    assert len(st2.scenarios) == 1
    assert st2.scenarios[0].name == 's1'


def test_compare_metrics():
    store = ScenarioStore()
    store.add(Scenario('a', {'budget': 100, 'risk_max': 0.1}, {'reach': 1200, 'roi': 10}))
    store.add(Scenario('b', {'budget': 200, 'risk_max': 0.2}, {'reach': 2200, 'roi': 20}))
    m = store.compare_metrics([0, 1])
    assert m['budget'] == [100, 200]
    assert m['reach'] == [1200, 2200]

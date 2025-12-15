import networkx as nx
from core.optimizer import Optimizer


def test_greedy_seed():
    G = nx.Graph()
    G.add_node('a', followers=1000, cost=10)
    G.add_node('b', followers=2000, cost=50)
    opt = Optimizer(G)
    sel = opt.greedy_seed(budget=60)
    assert 'b' in sel and 'a' in sel


def test_solve_returns_selected():
    G = nx.Graph()
    G.add_node('a', followers=1000, cost=10)
    G.add_node('b', followers=2000, cost=50)
    opt = Optimizer(G)
    res = opt.solve(budget=60, risk_max=1.0, coverage=0.0)
    assert isinstance(res, dict)
    assert 'selected' in res

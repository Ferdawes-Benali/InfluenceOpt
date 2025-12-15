import pytest
import networkx as nx

from core.optimizer import Optimizer


def test_monte_carlo_basic():
    G = nx.Graph()
    G.add_node('a', followers=1000, cost=10, risk=0.05, platform='IG')
    G.add_node('b', followers=2000, cost=50, risk=0.1, platform='TT')
    G.add_edge('a', 'b', prob=0.8)
    opt = Optimizer(G)
    sel = opt.greedy_seed(budget=60)
    res = opt.monte_carlo_robustness(sel, trials=10, perturb=0.1)
    assert isinstance(res, list)
    assert len(res) == 10
    assert all(isinstance(v, int) for v in res)


def test_solve_gurobi_if_available():
    gp = pytest.importorskip('gurobipy')
    G = nx.Graph()
    G.add_node('a', followers=1000, cost=10, risk=0.05, platform='IG')
    G.add_node('b', followers=2000, cost=50, risk=0.1, platform='TT')
    G.add_edge('a', 'b', prob=0.8)
    opt = Optimizer(G)
    # call internal gurobi solver directly
    res = opt._solve_gurobi(budget=60, risk_max=1.0, coverage=0.1, time_limit=10)
    assert isinstance(res, dict)
    assert 'selected' in res
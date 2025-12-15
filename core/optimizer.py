"""Optimizer wrapper: tries Gurobi, falls back to a simple greedy solver for tests.
"""
from typing import Dict, List, Tuple
import logging

import networkx as nx
import random
from statistics import mean

logger = logging.getLogger(__name__)


class Optimizer:
    def __init__(self, graph: nx.Graph):
        self.graph = graph
        self.use_gurobi = False
        try:
            import gurobipy as gp  # type: ignore
            self.gp = gp
            self.use_gurobi = True
            logger.info("Gurobi available, will use it for optimization")
        except Exception:
            logger.info("Gurobi not available; falling back to greedy solver")

    def greedy_seed(self, budget: float) -> List[str]:
        # Simple greedy: cost-effectiveness by followers/cost
        nodes = []
        items = [(n, d.get('followers', 0)/max(1.0, d.get('cost', 1.0))) for n, d in self.graph.nodes(data=True)]
        items.sort(key=lambda x: x[1], reverse=True)
        spent = 0.0
        for n, score in items:
            cost = float(self.graph.nodes[n].get('cost', 0))
            if spent + cost <= budget:
                nodes.append(n)
                spent += cost
        return nodes

    def solve(self, budget: float, risk_max: float, coverage: float, time_limit: int = 60) -> Dict:
        # returns dict with selection and stats
        if self.use_gurobi:
            try:
                return self._solve_gurobi(budget, risk_max, coverage, time_limit)
            except NotImplementedError:
                logger.warning("Gurobi solver interface not implemented; falling back to greedy")
        # Fallback
        selection = self.greedy_seed(budget)
        return {'selected': selection, 'objective': 0.0}

    def _solve_gurobi(self, budget: float, risk_max: float, coverage: float, time_limit: int = 60) -> Dict:
        gp = self.gp
        try:
            model = gp.Model("influence_opt")
            model.setParam('OutputFlag', 0)
        except Exception as e:
            logger.warning("Gurobi environment error (%s); falling back to greedy", e)
            return {'selected': self.greedy_seed(budget), 'objective': None, 'status': 'gurobi_unavailable'}
        model.setParam('TimeLimit', time_limit)
        model.setParam('MIPGap', 0.02)

        nodes = list(self.graph.nodes())
        # binary selection variables
        x = {n: model.addVar(vtype=gp.GRB.BINARY, name=f"x_{n}") for n in nodes}
        # reached follower vars (binary)
        z = {n: model.addVar(vtype=gp.GRB.BINARY, name=f"z_{n}") for n in nodes}

        model.update()

        # Objective: minimize cost - lambda * reach; here 'coverage' acts as reach weight (lambda)
        lam = float(coverage)
        obj = gp.quicksum(float(self.graph.nodes[n].get('cost', 0.0)) * x[n] for n in nodes) - lam * gp.quicksum(z[n] for n in nodes)
        model.setObjective(obj, gp.GRB.MINIMIZE)

        # Budget and risk constraints
        model.addConstr(gp.quicksum(float(self.graph.nodes[n].get('cost', 0.0)) * x[n] for n in nodes) <= budget, name='budget')
        model.addConstr(gp.quicksum(float(self.graph.nodes[n].get('risk', 0.0)) * x[n] for n in nodes) <= risk_max, name='risk')

        # z_f <= sum_{i in N(f) U {f}} x_i
        for f in nodes:
            nbrs = list(self.graph.neighbors(f)) + [f]
            model.addConstr(z[f] <= gp.quicksum(x[i] for i in nbrs), name=f"reach_{f}")

        # Coverage: sum z_f >= coverage * |V|
        model.addConstr(gp.quicksum(z[n] for n in nodes) >= float(coverage) * len(nodes), name='coverage')

        # Platform min/max percentage constraints (read from graph.graph['platform_bounds'] if present)
        S = gp.quicksum(x[n] for n in nodes)
        platforms = {}
        for n in nodes:
            p = self.graph.nodes[n].get('platform')
            platforms.setdefault(p, []).append(n)
        for p, lst in platforms.items():
            min_pct = 0
            max_pct = 100
            if self.graph.graph.get('platform_bounds') and p in self.graph.graph['platform_bounds']:
                b = self.graph.graph['platform_bounds'][p]
                min_pct = b.get('min_pct', 0)
                max_pct = b.get('max_pct', 100)
            lhs = gp.quicksum(x[n] for n in lst) * 100
            model.addConstr(lhs >= min_pct * S, name=f"plat_min_{p}")
            model.addConstr(lhs <= max_pct * S, name=f"plat_max_{p}")

        # Warm start with greedy seed
        seed = self.greedy_seed(budget)
        for n in seed:
            if n in x:
                x[n].start = 1.0

        model.update()
        model.optimize()

        status = model.Status
        selected = []
        if status in (gp.GRB.OPTIMAL, gp.GRB.TIME_LIMIT, gp.GRB.SUBOPTIMAL):
            for n in nodes:
                try:
                    if x[n].X > 0.5:
                        selected.append(n)
                except Exception:
                    pass
        return {
            'selected': selected,
            'objective': model.ObjVal if model.SolCount > 0 else None,
            'status': status,
            'runtime': model.Runtime,
        }

    def monte_carlo_robustness(self, selected: List[str], trials: int = 100, perturb: float = 0.1) -> List[float]:
        """Monte-Carlo simulation of reach given selected seeds.

        Each trial perturbs edge probabilities by +/- `perturb` fraction uniformly and
        samples which edges succeed; reach is measured as total followers reached.
        """
        results = []
        nodes = list(self.graph.nodes())
        followers = {n: int(self.graph.nodes[n].get('followers', 0)) for n in nodes}
        for _ in range(trials):
            success_edges = set()
            for u, v, d in self.graph.edges(data=True):
                base = float(d.get('prob', 1.0))
                delta = random.uniform(-perturb, perturb)
                p = max(0.0, min(1.0, base * (1 + delta)))
                if random.random() <= p:
                    success_edges.add((u, v))
                    success_edges.add((v, u))
            reached = set(selected)
            frontier = list(selected)
            while frontier:
                new_front = []
                for u in frontier:
                    for v in self.graph.neighbors(u):
                        if v in reached:
                            continue
                        if (u, v) in success_edges:
                            reached.add(v)
                            new_front.append(v)
                frontier = new_front
            total_followers = sum(followers.get(n, 0) for n in reached)
            results.append(total_followers)
        return results

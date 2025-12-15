"""Worker to run optimizer in background thread with cancel support."""
from PyQt5.QtCore import QThread, pyqtSignal
from core.optimizer import Optimizer


class SolveWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(dict)

    def __init__(self, graph, params: dict):
        super().__init__()
        self.graph = graph
        self.params = params
        self._cancel = False

    def run(self) -> None:
        opt = Optimizer(self.graph)
        # simple progress simulation for greedy fallback
        self.progress.emit(10)
        if self._cancel:
            self.finished.emit({'selected': []})
            return
        res = opt.solve(self.params.get('budget', 0), self.params.get('risk_max', 1.0), self.params.get('coverage', 0.0))
        # compute simple summary: total cost, reached followers estimate and ROI
        selected = res.get('selected', [])
        total_cost = sum(float(self.graph.nodes[n].get('cost', 0.0)) for n in selected)
        # estimate reach as selected + one-hop neighbors
        reached = set(selected)
        for n in selected:
            for v in self.graph.neighbors(n):
                reached.add(v)
        total_followers = sum(int(self.graph.nodes[n].get('followers', 0)) for n in reached)
        # expected conversions using eng_rate per user
        expected_conversions = 0.0
        for n in reached:
            er = self.graph.nodes[n].get('eng_rate')
            if er:
                expected_conversions += float(self.graph.nodes[n].get('followers', 0)) * float(er)
        conv_value = float(self.params.get('conv_value', 0.0))
        roi = conv_value * expected_conversions - total_cost

        res.update({
            'total_cost': total_cost,
            'reached_followers': total_followers,
            'expected_conversions': expected_conversions,
            'roi': roi,
        })
        self.progress.emit(100)
        self.finished.emit(res)

    def cancel(self) -> None:
        self._cancel = True
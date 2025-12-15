"""Simple interactive network view using networkx and PyQt5 (skeleton).
Provides basic load & demo functions; later to be extended with drag/zoom/layout.
"""
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsSimpleTextItem
from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QColor, QBrush, QPen, QPainter
import networkx as nx
import csv
from typing import Dict


PLATFORM_COLORS = {
    "IG": QColor(193, 53, 132),
    "TT": QColor(0, 0, 0),
    "YT": QColor(255, 0, 0),
    "TW": QColor(29, 161, 242),
}


class NetworkView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setScene(QGraphicsScene(self))
        self.graph = nx.Graph()
        self.node_items: Dict[str, QGraphicsEllipseItem] = {}
        # enable antialiasing for smoother rendering
        self.setRenderHint(QPainter.Antialiasing, True)

    def load_demo(self) -> None:
        # load demo CSV packaged with project
        users_csv = "data/demo_users.csv"
        edges_csv = "data/demo_edges.csv"
        self.load_users(users_csv)
        self.load_edges(edges_csv)
        self._layout_and_draw()

    def grab_screenshot(self, path: str) -> None:
        """Save a PNG screenshot of the current scene to `path`."""
        rect = self.scene().itemsBoundingRect()
        img = self.scene().renderToImage(rect.size().toSize()) if hasattr(self.scene(), 'renderToImage') else None
        # fallback to grab via viewport
        if img is None:
            pix = self.grab()
            pix.save(path)
        else:
            img.save(path)

    def load_users(self, users_csv: str) -> None:
        self.graph.clear()
        with open(users_csv, newline='', encoding='utf-8') as f:
            r = csv.DictReader(f)
            for row in r:
                node_id = row['id']
                row['followers'] = int(row.get('followers', 0))
                row['cost'] = float(row.get('cost', 0))
                self.graph.add_node(node_id, **row)

    def load_session(self, session: dict) -> None:
        """Load graph from a session dict produced by `core.scenarios.save_session` or `make_session_dict`."""
        self.graph.clear()
        for nd in session.get('nodes', []):
            nid = nd.get('id')
            attrs = {k: v for k, v in nd.items() if k != 'id'}
            self.graph.add_node(nid, **attrs)
        for ed in session.get('edges', []):
            self.graph.add_edge(ed.get('source'), ed.get('target'), **{k: v for k, v in ed.items() if k not in ('source', 'target')})
        self._layout_and_draw()

    def load_edges(self, edges_csv: str) -> None:
        with open(edges_csv, newline='', encoding='utf-8') as f:
            r = csv.DictReader(f)
            for row in r:
                self.graph.add_edge(row['source'], row['target'], weight=float(row.get('weight', 1.0)))

    def _layout_and_draw(self) -> None:
        self.scene().clear()
        if len(self.graph) == 0:
            return
        pos = nx.spring_layout(self.graph)
        for n, p in pos.items():
            attrs = self.graph.nodes[n]
            size = max(10, min(50, int(attrs.get('followers', 1000) ** 0.5)))
            color = PLATFORM_COLORS.get(attrs.get('platform', 'IG'), QColor(150, 150, 150))
            item = QGraphicsEllipseItem(QRectF(p[0]*500, p[1]*500, size, size))
            item.setBrush(QBrush(color))
            item.setPen(QPen(Qt.black, 1))
            self.scene().addItem(item)
            label = QGraphicsSimpleTextItem(attrs.get('name', n))
            label.setPos(p[0]*500, p[1]*500 + size)
            self.scene().addItem(label)
            self.node_items[n] = item
        self.fitInView(self.scene().itemsBoundingRect(), Qt.KeepAspectRatio)

    def highlight_selection(self, selected_ids: set) -> None:
        """Visually highlight selected influencer nodes."""
        for n, item in self.node_items.items():
            if n in selected_ids:
                item.setBrush(QBrush(QColor(255, 80, 80)))
                item.setPen(QPen(QColor(180, 0, 0), 3))
            else:
                # default neutral
                attrs = self.graph.nodes.get(n, {})
                color = PLATFORM_COLORS.get(attrs.get('platform', 'IG'), QColor(150, 150, 150))
                item.setBrush(QBrush(color))
                item.setPen(QPen(Qt.black, 1))
"""Enhanced interactive network view with drag, zoom, tooltips, and visual feedback.
"""
from PyQt5.QtWidgets import (QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, 
                             QGraphicsSimpleTextItem, QGraphicsLineItem, QMenu, 
                             QAction, QDialog, QVBoxLayout, QFormLayout, 
                             QLineEdit, QSpinBox, QDoubleSpinBox, QPushButton,
                             QComboBox, QLabel, QToolTip)
from PyQt5.QtCore import QRectF, Qt, QPointF, pyqtSignal, QTimer
from PyQt5.QtGui import QColor, QBrush, QPen, QPainter, QFont, QRadialGradient, QLinearGradient, QImage
import networkx as nx
import csv
import math
from typing import Dict, Optional, Set


PLATFORM_COLORS = {
    "IG": {
        'base': QColor(225, 48, 108),
        'light': QColor(255, 78, 138),
        'dark': QColor(195, 18, 78)
    },
    "TT": {
        'base': QColor(0, 0, 0),
        'light': QColor(50, 50, 50),
        'dark': QColor(0, 0, 0)
    },
    "YT": {
        'base': QColor(255, 0, 0),
        'light': QColor(255, 50, 50),
        'dark': QColor(200, 0, 0)
    },
    "TW": {
        'base': QColor(29, 161, 242),
        'light': QColor(59, 191, 255),
        'dark': QColor(0, 131, 212)
    },
}

RISK_COLORS = {
    'low': QColor(46, 204, 113),      # Green
    'medium': QColor(241, 196, 15),   # Yellow
    'high': QColor(231, 76, 60),      # Red
    'critical': QColor(192, 57, 43),  # Dark Red
}


def get_risk_color(risk_value: float) -> QColor:
    """Get color based on risk level."""
    if risk_value < 0.1:
        return RISK_COLORS['low']
    elif risk_value < 0.2:
        return RISK_COLORS['medium']
    elif risk_value < 0.3:
        return RISK_COLORS['high']
    else:
        return RISK_COLORS['critical']


class InteractiveNodeItem(QGraphicsEllipseItem):
    """Enhanced node item with hover effects, context menu, and visual states."""
    
    def __init__(self, node_id: str, graph: nx.Graph, rect: QRectF, parent=None):
        super().__init__(rect, parent)
        self.node_id = node_id
        self.graph = graph
        self.is_selected_influencer = False
        self.is_reached = False
        self.is_hovered = False
        
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsEllipseItem.ItemIsMovable, True)
        self.setFlag(QGraphicsEllipseItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsEllipseItem.ItemSendsGeometryChanges, True)
        
        self._update_appearance()
    
    def _update_appearance(self):
        """Update visual appearance based on node state."""
        attrs = self.graph.nodes[self.node_id]
        platform = attrs.get('platform', 'IG')
        colors = PLATFORM_COLORS.get(platform, PLATFORM_COLORS['IG'])
        
        # Determine risk level
        risk = float(attrs.get('risk', 0))
        if risk < 0.1:
            risk_level = 'low'
        elif risk < 0.2:
            risk_level = 'medium'
        elif risk < 0.3:
            risk_level = 'high'
        else:
            risk_level = 'critical'
        
        # Base gradient
        gradient = QRadialGradient(self.rect().center(), self.rect().width() / 2)
        
        if self.is_selected_influencer:
            # Selected influencer: bold red with glow
            gradient.setColorAt(0, QColor(255, 100, 100))
            gradient.setColorAt(0.7, QColor(230, 50, 50))
            gradient.setColorAt(1, QColor(180, 0, 0))
            self.setPen(QPen(QColor(255, 215, 0), 4))  # Gold border
        elif self.is_reached:
            # Reached follower: blue gradient
            gradient.setColorAt(0, QColor(100, 181, 246))
            gradient.setColorAt(0.7, QColor(66, 165, 245))
            gradient.setColorAt(1, QColor(33, 150, 243))
            self.setPen(QPen(QColor(25, 118, 210), 2))
        else:
            # Normal state: platform color with gradient
            gradient.setColorAt(0, colors['light'])
            gradient.setColorAt(0.5, colors['base'])
            gradient.setColorAt(1, colors['dark'])
            
            # Add risk indicator as border
            risk_color = RISK_COLORS[risk_level]
            border_width = 2 if self.is_hovered else 1
            self.setPen(QPen(risk_color, border_width))
        
        # Check for high fake percentage (gray out)
        fake = float(attrs.get('fake', 0))
        if fake > 0.3:
            gradient.setColorAt(0, QColor(200, 200, 200))
            gradient.setColorAt(1, QColor(150, 150, 150))
            self.setOpacity(0.5)
        else:
            self.setOpacity(1.0)
        
        self.setBrush(QBrush(gradient))
        
        # Add glow effect for hovered items
        if self.is_hovered:
            self.setScale(1.1)
        else:
            self.setScale(1.0)
    
    def hoverEnterEvent(self, event):
        """Show tooltip on hover."""
        self.is_hovered = True
        self._update_appearance()
        
        attrs = self.graph.nodes[self.node_id]
        tooltip = f"""<b>{attrs.get('name', self.node_id)}</b><br>
Platform: {attrs.get('platform', 'N/A')}<br>
Followers: {attrs.get('followers', 0):,}<br>
Cost: ${attrs.get('cost', 0):,.2f}<br>
Risk: {attrs.get('risk', 0)*100:.1f}%<br>
Fake: {attrs.get('fake', 0)*100:.1f}%<br>
Engagement: {attrs.get('eng_rate', 0)*100:.2f}%"""
        
        QToolTip.setFont(QFont('Arial', 10))
        QToolTip.showText(event.screenPos(), tooltip)
        
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        """Remove hover effect."""
        self.is_hovered = False
        self._update_appearance()
        super().hoverLeaveEvent(event)
    
    def contextMenuEvent(self, event):
        """Show context menu for node editing."""
        menu = QMenu()
        edit_action = QAction("Edit Node Properties", None)
        edit_action.triggered.connect(self._edit_node)
        menu.addAction(edit_action)
        
        toggle_action = QAction("Toggle Selection", None)
        toggle_action.triggered.connect(self._toggle_selection)
        menu.addAction(toggle_action)
        
        menu.exec_(event.screenPos())
    
    def _edit_node(self):
        """Open dialog to edit node properties."""
        dialog = NodeEditDialog(self.node_id, self.graph)
        if dialog.exec_():
            self._update_appearance()
            # Trigger relayout in parent view
            if self.scene() and self.scene().views():
                view = self.scene().views()[0]
                if hasattr(view, '_layout_and_draw'):
                    view._layout_and_draw()
    
    def _toggle_selection(self):
        """Toggle manual selection state."""
        self.is_selected_influencer = not self.is_selected_influencer
        self._update_appearance()


class NodeEditDialog(QDialog):
    """Dialog for editing node properties."""
    
    def __init__(self, node_id: str, graph: nx.Graph, parent=None):
        super().__init__(parent)
        self.node_id = node_id
        self.graph = graph
        self.setWindowTitle(f"Edit Node: {node_id}")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        form = QFormLayout()
        
        attrs = graph.nodes[node_id]
        
        self.name_edit = QLineEdit(attrs.get('name', node_id))
        form.addRow("Name:", self.name_edit)
        
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(['IG', 'TT', 'YT', 'TW'])
        self.platform_combo.setCurrentText(attrs.get('platform', 'IG'))
        form.addRow("Platform:", self.platform_combo)
        
        self.followers_spin = QSpinBox()
        self.followers_spin.setRange(0, 10000000)
        self.followers_spin.setValue(int(attrs.get('followers', 0)))
        form.addRow("Followers:", self.followers_spin)
        
        self.cost_spin = QDoubleSpinBox()
        self.cost_spin.setRange(0, 1000000)
        self.cost_spin.setValue(float(attrs.get('cost', 0)))
        self.cost_spin.setPrefix("$ ")
        form.addRow("Cost:", self.cost_spin)
        
        self.risk_spin = QDoubleSpinBox()
        self.risk_spin.setRange(0, 1)
        self.risk_spin.setSingleStep(0.01)
        self.risk_spin.setValue(float(attrs.get('risk', 0)))
        self.risk_spin.setSuffix(" %")
        form.addRow("Risk:", self.risk_spin)
        
        self.fake_spin = QDoubleSpinBox()
        self.fake_spin.setRange(0, 1)
        self.fake_spin.setSingleStep(0.01)
        self.fake_spin.setValue(float(attrs.get('fake', 0)))
        self.fake_spin.setSuffix(" %")
        form.addRow("Fake %:", self.fake_spin)
        
        self.eng_spin = QDoubleSpinBox()
        self.eng_spin.setRange(0, 1)
        self.eng_spin.setSingleStep(0.001)
        self.eng_spin.setValue(float(attrs.get('eng_rate', 0)))
        self.eng_spin.setSuffix(" %")
        form.addRow("Engagement:", self.eng_spin)
        
        layout.addLayout(form)
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self._save)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout = QVBoxLayout()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def _save(self):
        """Save edited properties to graph."""
        self.graph.nodes[self.node_id]['name'] = self.name_edit.text()
        self.graph.nodes[self.node_id]['platform'] = self.platform_combo.currentText()
        self.graph.nodes[self.node_id]['followers'] = self.followers_spin.value()
        self.graph.nodes[self.node_id]['cost'] = self.cost_spin.value()
        self.graph.nodes[self.node_id]['risk'] = self.risk_spin.value()
        self.graph.nodes[self.node_id]['fake'] = self.fake_spin.value()
        self.graph.nodes[self.node_id]['eng_rate'] = self.eng_spin.value()
        self.accept()


class NetworkView(QGraphicsView):
    """Enhanced network view with zoom, pan, layout options, and animations."""
    
    selectionChanged = pyqtSignal(set)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setScene(QGraphicsScene(self))
        self.graph = nx.Graph()
        self.node_items: Dict[str, InteractiveNodeItem] = {}
        self.edge_items = []
        self.pos = {}
        
        # Enable antialiasing and smooth transformations
        self.setRenderHint(QPainter.Antialiasing, True)
        self.setRenderHint(QPainter.SmoothPixmapTransform, True)
        self.setRenderHint(QPainter.TextAntialiasing, True)
        
        # Enable drag mode
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        
        # Zoom controls
        self._zoom = 1.0
        
        # Layout algorithm choice
        self.layout_algorithm = 'spring'  # 'spring', 'circular', 'kamada_kawai', 'community'
        
        # Animation timer for live updates
        self._animation_timer = QTimer()
        self._animation_timer.timeout.connect(self._animate_reach)
        self._animation_step = 0
    
    def wheelEvent(self, event):
        """Handle mouse wheel for zooming."""
        zoom_factor = 1.15
        
        if event.angleDelta().y() > 0:
            # Zoom in
            self._zoom *= zoom_factor
            self.scale(zoom_factor, zoom_factor)
        else:
            # Zoom out
            self._zoom /= zoom_factor
            self.scale(1 / zoom_factor, 1 / zoom_factor)
    
    def set_layout_algorithm(self, algorithm: str):
        """Change layout algorithm and redraw."""
        self.layout_algorithm = algorithm
        self._layout_and_draw()
    
    def load_demo(self):
        """Load demo dataset."""
        users_csv = "data/demo_users.csv"
        edges_csv = "data/demo_edges.csv"
        self.load_users(users_csv)
        self.load_edges(edges_csv)
        self._layout_and_draw()
    
    def load_users(self, users_csv: str):
        """Load users from CSV."""
        self.graph.clear()
        with open(users_csv, newline='', encoding='utf-8') as f:
            r = csv.DictReader(f)
            for row in r:
                node_id = row['id']
                row['followers'] = int(row.get('followers', 0))
                row['cost'] = float(row.get('cost', 0))
                row['risk'] = float(row.get('risk', 0))
                row['fake'] = float(row.get('fake', 0))
                row['eng_rate'] = float(row.get('eng_rate', 0))
                self.graph.add_node(node_id, **row)
    
    def load_edges(self, edges_csv: str):
        """Load edges from CSV."""
        with open(edges_csv, newline='', encoding='utf-8') as f:
            r = csv.DictReader(f)
            for row in r:
                weight = float(row.get('weight', 1.0))
                prob = float(row.get('prob', 1.0))
                self.graph.add_edge(row['source'], row['target'], 
                                   weight=weight, prob=prob)
    
    def load_session(self, session: dict):
        """Load graph from session dictionary."""
        self.graph.clear()
        for nd in session.get('nodes', []):
            nid = nd.get('id')
            attrs = {k: v for k, v in nd.items() if k != 'id'}
            self.graph.add_node(nid, **attrs)
        for ed in session.get('edges', []):
            self.graph.add_edge(ed.get('source'), ed.get('target'), 
                               **{k: v for k, v in ed.items() if k not in ('source', 'target')})
        self._layout_and_draw()
    
    def _layout_and_draw(self) -> None:
        """Enhanced layout with better colors and sizes."""
        self.scene().clear()
        self.node_items.clear()
        if len(self.graph) == 0:
            return
        
        pos = nx.spring_layout(self.graph, k=2, iterations=50)  # Better layout
        scale = 500
        
        # Draw edges first
        for u, v, data in self.graph.edges(data=True):
            p1 = pos[u]
            p2 = pos[v]
            
            # Edge color based on probability
            prob = data.get('prob', 1.0)
            if prob > 0.7:
                edge_color = QColor(46, 204, 113, 150)  # Green
            elif prob > 0.4:
                edge_color = QColor(241, 196, 15, 150)  # Yellow
            else:
                edge_color = QColor(231, 76, 60, 150)   # Red
            
            line = self.scene().addLine(
                p1[0] * scale, p1[1] * scale,
                p2[0] * scale, p2[1] * scale,
                QPen(edge_color, 2)
            )
        
        # Draw nodes with better sizing and coloring
        for n, p in pos.items():
            attrs = self.graph.nodes[n]
            
            # Size based on followers (logarithmic)
            followers = attrs.get('followers', 1000)
            size = max(15, min(60, 10 + math.log10(followers + 1) * 8))
            
            # Platform color
            platform = attrs.get('platform', 'IG')
            color_dict = PLATFORM_COLORS.get(platform, PLATFORM_COLORS['IG'])
            color = color_dict['base']
            
            # Risk-based border
            risk = attrs.get('risk', 0.0)
            risk_color = get_risk_color(risk)
            
            # Create node using InteractiveNodeItem
            rect = QRectF(p[0] * scale - size/2, p[1] * scale - size/2, size, size)
            item = InteractiveNodeItem(n, self.graph, rect)
            
            self.scene().addItem(item)
            self.node_items[n] = item
            
            # Label
            label = QGraphicsSimpleTextItem(attrs.get('name', n))
            label.setPos(p[0] * scale - size/2, p[1] * scale + size/2 + 2)
            label.setBrush(QBrush(QColor(236, 240, 241)))  # Light color
            self.scene().addItem(label)
        
        self.fitInView(self.scene().itemsBoundingRect(), Qt.KeepAspectRatio)

    def highlight_selection(self, selected_ids: Set[str], reached_ids: Optional[Set[str]] = None):
        """Highlight selected influencers and reached followers."""
        for n, item in self.node_items.items():
            item.is_selected_influencer = n in selected_ids
            item.is_reached = reached_ids and n in reached_ids
            item._update_appearance()
        
        # Start animation for reach propagation
        if reached_ids:
            self._animation_step = 0
            self._animation_timer.start(100)
    
    def _animate_reach(self):
        """Animate the reach propagation effect."""
        self._animation_step += 1
        if self._animation_step > 10:
            self._animation_timer.stop()
    
    def grab_screenshot(self, path: str):
        """Save screenshot of current view."""
        rect = self.scene().itemsBoundingRect()
        img = QImage(rect.size().toSize(), QImage.Format_ARGB32)
        img.fill(Qt.white)
        painter = QPainter(img)
        self.scene().render(painter, QRectF(), rect)
        painter.end()
        img.save(path)
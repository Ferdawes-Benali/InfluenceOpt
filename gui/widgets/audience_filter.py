"""Audience filter widget: tree for demographics with coverage slider."""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QLabel, QSlider
from PyQt5.QtCore import Qt


class AudienceFilter(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Audience Filter"))
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        # Age groups
        ages = QTreeWidgetItem(self.tree, ["Age"])
        for a in ["18-24", "25-34", "35-44", "45+"]:
            item = QTreeWidgetItem(ages, [a])
            item.setCheckState(0, Qt.Checked)
        regions = QTreeWidgetItem(self.tree, ["Region"])
        for r in ["NA", "EU", "AS"]:
            it = QTreeWidgetItem(regions, [r])
            it.setCheckState(0, Qt.Checked)
        genders = QTreeWidgetItem(self.tree, ["Gender"])
        for g in ["M", "F"]:
            it = QTreeWidgetItem(genders, [g])
            it.setCheckState(0, Qt.Checked)
        self.tree.expandAll()
        layout.addWidget(self.tree)
        layout.addWidget(QLabel("Coverage % (50-100)"))
        self.coverage = QSlider(Qt.Horizontal)
        self.coverage.setMinimum(50)
        self.coverage.setMaximum(100)
        self.coverage.setValue(80)
        layout.addWidget(self.coverage)
        self.setLayout(layout)

    def coverage_value(self) -> float:
        return self.coverage.value() / 100.0

    def selected_filters(self) -> dict:
        # returns selected options (simple)
        out = {'age': [], 'region': [], 'gender': []}
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            cat = root.child(i)
            name = cat.text(0).lower()
            for j in range(cat.childCount()):
                c = cat.child(j)
                if c.checkState(0) == Qt.Checked:
                    out[name].append(c.text(0))
        return out

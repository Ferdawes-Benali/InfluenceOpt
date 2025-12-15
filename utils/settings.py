"""QSettings helpers"""
from PyQt5.QtCore import QSettings


def settings() -> QSettings:
    s = QSettings('InfluenceOpt', 'InfluenceOptApp')
    return s

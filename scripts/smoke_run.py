"""Smoke test: show the MainWindow for 1 second and exit."""
import sys
import os
# ensure repo root is on sys.path so 'gui' package is importable when running the script directly
_here = os.path.abspath(os.path.dirname(__file__))
_repo_root = os.path.abspath(os.path.join(_here, '..'))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

try:
    app = QApplication.instance() or QApplication(sys.argv)
    from gui.main_window import MainWindow
    w = MainWindow()
    w.show()
    print('MainWindow instantiated and shown; quitting in 1s')
    QTimer.singleShot(1000, app.quit)
    rc = app.exec_()
    print('Exited with rc=', rc)
    sys.exit(0)
except Exception as e:
    print('ERROR during smoke run:', repr(e))
    raise

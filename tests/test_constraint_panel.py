import pytest
from PyQt5.QtWidgets import QApplication

from gui.constraint_panel import ConstraintPanel


@pytest.fixture(scope="module")
def app():
    return QApplication([])


def test_as_dict_contains_keys(app):
    cp = ConstraintPanel()
    d = cp.as_dict()
    assert 'budget' in d and 'risk_max' in d and 'coverage' in d and 'platforms' in d and 'conv_value' in d

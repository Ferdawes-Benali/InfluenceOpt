import os
import pytest
from utils.exporters import export_brief_pptx, export_selection_csv
from core.scenarios import Scenario


def test_export_csv(tmp_path):
    p = tmp_path / "sel.csv"
    export_selection_csv(str(p), ['a', 'b'])
    assert p.exists()


def test_export_pptx_skips_if_no_lib(tmp_path):
    # If python-pptx not installed this should raise RuntimeError
    p = tmp_path / "brief.pptx"
    s = Scenario('s', {'budget': 10}, {'selected': ['a'], 'reach': 100})
    try:
        export_brief_pptx(str(p), s, None)
    except RuntimeError:
        pytest.skip("python-pptx not available")
    assert p.exists()

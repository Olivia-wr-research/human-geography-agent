"""Headless export/reopen integration check; run with QGIS's Python environment."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from pathlib import Path
from qgis.core import QgsApplication, QgsProject
from qgis_demo import run_demo
from prepare_demo import generate

app = QgsApplication([], False)
app.initQgis()
try:
    root = Path('work/qgis-ci')
    generate(root / 'input')
    project_file = run_demo(root/'input', root/'export')
    reopened = QgsProject()
    assert reopened.read(project_file), 'Cannot reopen project'
    assert len(reopened.mapLayers()) == 2
    assert all(layer.isValid() for layer in reopened.mapLayers().values())
    assert len(reopened.layoutManager().layouts()) == 1
    for name in ('synthetic_od.png','synthetic_od.pdf'):
        assert (root/'export'/name).stat().st_size > 1000
    reopened.clear()
    del reopened
    print('QGIS export and project reopen passed; visual review remains separate.')
finally:
    app.exitQgis()

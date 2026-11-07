"""Run inside QGIS Python Console: run_demo(input_dir, fresh_output_dir)."""
from pathlib import Path
import hashlib
import json

def run_demo(input_dir, output_dir):
    from qgis.core import (Qgis, QgsProject, QgsVectorLayer, QgsCoordinateReferenceSystem,
        QgsPrintLayout, QgsLayoutItemMap, QgsLayoutItemLabel, QgsLayoutItemLegend,
        QgsLayoutItemScaleBar, QgsLayoutPoint, QgsLayoutSize, QgsLayoutExporter,
        QgsMarkerSymbol, QgsLineSymbol, QgsProperty, QgsSymbolLayer, QgsUnitTypes)
    source, target = Path(input_dir).resolve(), Path(output_dir).resolve()
    if target.exists():
        raise ValueError('Use a new output directory; existing projects are preserved')
    manifest = json.loads((source / 'manifest.json').read_text())
    if manifest.get('synthetic') is not True:
        raise ValueError('This demonstration accepts its synthetic fixture only')
    for name in ('cities.geojson', 'flows.geojson'):
        if hashlib.sha256((source / name).read_bytes()).hexdigest() != manifest['hashes'][name]:
            raise ValueError('Input hash mismatch: ' + name)
    # A private QgsProject avoids clearing the current desktop project.
    project = QgsProject()
    project.setCrs(QgsCoordinateReferenceSystem('EPSG:32632'))
    project.setFilePathStorage(Qgis.FilePathType.Relative)
    target.mkdir(parents=True)
    # Copy only explicit synthetic fixtures so the saved project is portable.
    for name in ('cities.geojson', 'flows.geojson'):
        (target / name).write_bytes((source / name).read_bytes())
    cities = QgsVectorLayer(str(target / 'cities.geojson'), 'Fictional locations', 'ogr')
    flows = QgsVectorLayer(str(target / 'flows.geojson'), 'Synthetic OD links (weight)', 'ogr')
    for layer in (cities, flows):
        if not layer.isValid() or layer.featureCount() == 0:
            raise ValueError('Invalid or empty layer: ' + layer.name())
        project.addMapLayer(layer)
    cities.renderer().setSymbol(QgsMarkerSymbol.createSimple({'name':'circle', 'color':'#dd8452', 'size':'3'}))
    line = QgsLineSymbol.createSimple({'line_color':'#346e91', 'line_width':'0.6'})
    line.symbolLayer(0).setDataDefinedProperty(QgsSymbolLayer.PropertyStrokeWidth,
        QgsProperty.fromExpression('0.2 + sqrt("weight") * 0.2'))
    flows.renderer().setSymbol(line)
    layout = QgsPrintLayout(project)
    layout.initializeDefaults()
    layout.setName('Synthetic OD example')
    project.layoutManager().addLayout(layout)
    map_item = QgsLayoutItemMap(layout)
    layout.addLayoutItem(map_item)
    map_item.attemptMove(QgsLayoutPoint(12, 28))
    map_item.attemptResize(QgsLayoutSize(186, 160))
    map_item.setCrs(project.crs())
    map_item.setLayers([cities, flows])
    map_item.setKeepLayerSet(True)
    from qgis.core import QgsCoordinateTransform
    extent = QgsCoordinateTransform(cities.crs(), project.crs(), project).transformBoundingBox(cities.extent())
    extent.scale(1.2)
    map_item.zoomToExtent(extent)
    def label(text, x, y, width, height):
        item = QgsLayoutItemLabel(layout)
        item.setText(text)
        layout.addLayoutItem(item)
        item.attemptMove(QgsLayoutPoint(x,y))
        item.attemptResize(QgsLayoutSize(width,height))
        return item
    label('SYNTHETIC DEMO | Human Geography Research Agent', 12, 8, 186, 15)
    legend = QgsLayoutItemLegend(layout)
    legend.setTitle('Layers')
    legend.setLinkedMap(map_item)
    layout.addLayoutItem(legend)
    legend.attemptMove(QgsLayoutPoint(12,196))
    scale = QgsLayoutItemScaleBar(layout)
    scale.setStyle('Single Box')
    scale.setLinkedMap(map_item)
    scale.applyDefaultSize()
    scale.setUnits(QgsUnitTypes.DistanceKilometers)
    scale.setUnitsPerSegment(50)
    scale.setNumberOfSegments(2)
    scale.setNumberOfSegmentsLeft(0)
    scale.setUnitLabel('km')
    layout.addLayoutItem(scale)
    scale.attemptMove(QgsLayoutPoint(110,198))
    label('Fictional locations and weights; no real people or administrative boundaries.\n'
          'Lines show connections, not routes or directional arrows.\n'
          'Width (mm) = 0.2 + 0.2 * sqrt(weight); weights: 4, 7, 9, 12.\n'
          'CRS: EPSG:32632. Grid north is up. Source: bundled synthetic generator.',
          12,230,186,44)
    path = target / 'synthetic_od.qgz'
    project.setFileName(str(path))
    if not project.write():
        raise RuntimeError('QGIS project save failed')
    exporter = QgsLayoutExporter(layout)
    image_settings = QgsLayoutExporter.ImageExportSettings()
    image_settings.dpi = 300
    pdf_settings = QgsLayoutExporter.PdfExportSettings()
    pdf_settings.dpi = 300
    results = [exporter.exportToImage(str(target / 'synthetic_od.png'), image_settings),
               exporter.exportToPdf(str(target / 'synthetic_od.pdf'), pdf_settings)]
    if any(result != QgsLayoutExporter.Success for result in results):
        raise RuntimeError('Export failed: ' + str(results))
    (target / 'export_manifest.json').write_text(json.dumps(dict(qgis_version=Qgis.QGIS_VERSION,
        synthetic=True, crs=project.crs().authid(), dpi=300, input_hashes=manifest['hashes'],
        visual_review='PENDING', outputs=['synthetic_od.qgz','synthetic_od.png','synthetic_od.pdf']), indent=2)+'\n')
    print('Export complete; open and visually inspect', target)
    return str(path)

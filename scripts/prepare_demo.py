"""Generate synthetic WGS84 points and straight OD lines; not observed geography."""
import argparse
import hashlib
import json
import math
from pathlib import Path

CITIES = [dict(id='A', lon=10, lat=45), dict(id='B', lon=12, lat=46),
          dict(id='C', lon=14, lat=44), dict(id='D', lon=11, lat=43)]
FLOWS = [('A', 'B', 12), ('A', 'C', 7), ('B', 'D', 4), ('C', 'D', 9)]

def features(cities, flows):
    lookup = {}
    for row in cities:
        key, x, y = row['id'], float(row['lon']), float(row['lat'])
        if key in lookup or not key:
            raise ValueError('Duplicate/empty city ID')
        if not (math.isfinite(x) and math.isfinite(y) and -180 <= x <= 180 and -90 <= y <= 90):
            raise ValueError('Invalid WGS84 coordinates')
        lookup[key] = [x, y]
    points = [dict(type='Feature', properties={'id': k, 'synthetic': True},
                   geometry=dict(type='Point', coordinates=v)) for k, v in lookup.items()]
    lines = []
    for origin, destination, weight in flows:
        if origin not in lookup or destination not in lookup:
            raise ValueError('Unmatched flow endpoint')
        if not math.isfinite(weight) or weight <= 0:
            raise ValueError('Flow weight must be finite and positive')
        if origin == destination:
            raise ValueError('Self flows need a separate visualization')
        if abs(lookup[origin][0] - lookup[destination][0]) > 180:
            raise ValueError('Antimeridian flow requires splitting before rendering')
        lines.append(dict(type='Feature', properties=dict(origin=origin, destination=destination,
                          weight=weight, synthetic=True), geometry=dict(type='LineString',
                          coordinates=[lookup[origin], lookup[destination]])))
    return points, lines

def generate(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    names = ['cities.geojson', 'flows.geojson', 'manifest.json']
    if any((output / name).exists() for name in names):
        raise ValueError('Demo output already exists; use a new directory')
    points, lines = features(CITIES, FLOWS)
    hashes = {}
    for name, rows in zip(names, (points, lines)):
        path = output / name
        path.write_text(json.dumps(dict(type='FeatureCollection', features=rows), indent=2)+'\n')
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    (output / 'manifest.json').write_text(json.dumps(dict(synthetic=True, crs='EPSG:4326',
        point_count=len(points), flow_count=len(lines), hashes=hashes,
        meaning='Fictional coordinates and weights. Lines are connections, not travel routes.'), indent=2)+'\n')
    return hashes

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    generate(args.output)
    print('Synthetic demo written to', args.output)

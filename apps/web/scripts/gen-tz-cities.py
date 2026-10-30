#!/usr/bin/env python3
"""Generate src/lib/tz-cities.json: IANA time zone -> [lat, lng] of its principal city (zone.tab) plus link aliases."""
import json, re, sys
from pathlib import Path

root = Path('/usr/share/zoneinfo')
def coord(s):
    m = re.fullmatch(r'([+-])(\d{2})(\d{2})(\d{2})?([+-])(\d{3})(\d{2})(\d{2})?', s)
    sign = lambda c: -1 if c == '-' else 1
    lat = sign(m[1]) * (int(m[2]) + int(m[3]) / 60 + int(m[4] or 0) / 3600)
    lng = sign(m[5]) * (int(m[6]) + int(m[7]) / 60 + int(m[8] or 0) / 3600)
    return [round(lat, 2), round(lng, 2)]
zones = {}
for line in (root / 'zone.tab').read_text().splitlines():
    if line and not line.startswith('#'):
        _, c, tz, *_ = line.split('\t')
        zones[tz] = coord(c)
for name in ('tzdata.zi',):
    path = root / name
    if path.exists():
        for line in path.read_text().splitlines():
            if line.startswith('L '):
                _, target, link = line.split()
                if target in zones and link not in zones:
                    zones[link] = zones[target]
zones['UTC'] = [51.48, 0.0]  # no principal city: Greenwich
out = Path(__file__).resolve().parents[1] / 'src/lib/tz-cities.json'
out.write_text(json.dumps(dict(sorted(zones.items())), separators=(',', ':')) + '\n')
print(len(zones), 'zones ->', out)

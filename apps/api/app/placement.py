"""Request-scoped placement of the fictional demo stores around the viewer."""
from __future__ import annotations

import asyncio
import json
import logging
import math
import os
import re
import time
import weakref
from collections import OrderedDict
from contextvars import ContextVar
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import httpx
from sqlalchemy import event
from sqlalchemy.orm.attributes import set_committed_value

from .models import Merchant, MerchantLocation

log = logging.getLogger('payfound.placement')

SF_CENTRE = (37.7786, -122.4140)
GRID = 0.02
RING_MIN_KM, RING_MAX_KM = 0.4, 4.5
SNAP_RADIUS_M = 300.0
MIN_SEPARATION_M = 60.0
# (bearing rotation in degrees, distance scale) tried in order for each store.
ATTEMPTS = [(0, 1.0), (25, 1.0), (-25, 1.0), (50, 0.7), (-50, 0.7), (0, 0.5), (25, 0.35), (-25, 0.35)]
CACHE_SIZE, CACHE_TTL = 200, 24 * 3600
MAX_NEW_CELLS_PER_HOUR = int(os.getenv('PF_PLACEMENT_MAX_CELLS_PER_HOUR', '60'))

# Demo stores. IDs/slugs are the seeded identity; coordinates are the San Francisco originals.
_BASE = [
    ('m1', 'northside-electronics', 'Northside Electronics', 37.7744, -122.4212),
    ('m2', 'mission-hardware', 'Mission Hardware Co.', 37.7512, -122.4183),
    ('m3', 'bay-pet-supply', 'Bay Pet Supply', 37.7905, -122.4200),
    ('m4', 'city-cycle-shop', 'City Cycle Shop', 37.7791, -122.4050),
]


def _load_demo():
    rows = list(_BASE)
    try:
        data = json.loads(Path(__file__).with_name('demo_catalogue.json').read_text())
        rows += [(m['id'], m['slug'], m['name'], m['latitude'], m['longitude']) for m in data['merchants']]
    except (OSError, ValueError, KeyError):  # pragma: no cover - catalogue ships with the app
        log.warning('demo catalogue unavailable; only the base demo stores will be relocated')
    try:  # grocery / fresh-food demo stores (m14+); each extra branch relocates as its own point 'mNN~bK'
        grocery = json.loads(Path(__file__).with_name('demo_catalogue_grocery.json').read_text())
        for m in grocery['merchants']:
            for i, b in enumerate(m['branches']):
                rows.append((m['id'] if i == 0 else f"{m['id']}~b{i + 1}", m['slug'] if i == 0 else f"{m['slug']}-b{i + 1}",
                             m['name'] if i == 0 else b['name'], b['latitude'], b['longitude']))
    except (OSError, ValueError, KeyError):  # pragma: no cover
        log.warning('grocery demo catalogue unavailable; its stores will not be relocated')
    return rows


@dataclass(frozen=True)
class DemoStore:
    id: str
    slug: str
    name: str
    lat: float
    lng: float

    @property
    def merchant_id(self):
        return self.id.split('~')[0]

    @property
    def loc_id(self):
        base, _, branch = self.id.partition('~')  # extra branches: 'm14~b2' -> 'loc-m14-b2'
        return 'loc-' + base + ('-' + branch if branch else '')


DEMO_STORES = [DemoStore(*row) for row in _load_demo()]
DEMO_BY_ID = {s.id: s for s in DEMO_STORES}
DEMO_BY_LOC = {s.loc_id: s for s in DEMO_STORES}
# Display names that mention San Francisco neighbourhoods are neutralised while relocated (slugs are unchanged).
NEUTRAL_NAMES = {'SoMa Gadget Lab': 'Metro Gadget Lab', 'Hayes Valley Home': 'Garden Row Home', 'Cole Valley Pets': 'Cedar Row Pets'}


def neutral(text):
    for old, new in NEUTRAL_NAMES.items():
        if isinstance(text, str) and old in text:
            text = text.replace(old, new)
    return text


@dataclass(frozen=True)
class Placed:
    lat: float
    lng: float
    address: str


@dataclass
class Layout:
    mode: str
    cell: tuple[float, float]
    reason: str
    stores: dict[str, Placed] = field(default_factory=dict)
    placed: int = 0
    total: int = len(DEMO_STORES)
    provider: str = ''

    def public(self):
        return {'mode': self.mode, 'cell': {'latitude': self.cell[0], 'longitude': self.cell[1]}, 'reason': self.reason,
                'placed': self.placed, 'total': self.total, 'provider': self.provider}


_ANCHOR: ContextVar[tuple[float, float] | None] = ContextVar('pf_anchor', default=None)
_TZ: ContextVar[str | None] = ContextVar('pf_tz', default=None)
_LAYOUT: ContextVar[Layout | None] = ContextVar('pf_layout', default=None)

_ANCHOR_RE = re.compile(r'^\s*(-?\d{1,3}(?:\.\d{1,8})?)\s*,\s*(-?\d{1,3}(?:\.\d{1,8})?)\s*$')
_TZ_RE = re.compile(r'^[A-Za-z0-9_+\-]+(?:/[A-Za-z0-9_+\-]+){0,2}$')


def parse_anchor(value):
    """Validated, 2-decimal anchor or None. Never raises."""
    if not isinstance(value, str) or len(value) > 40:
        return None
    match = _ANCHOR_RE.match(value)
    if not match:
        return None
    lat, lng = float(match.group(1)), float(match.group(2))
    if not (math.isfinite(lat) and math.isfinite(lng)) or abs(lat) > 85 or abs(lng) > 180:
        return None
    return round(lat, 2), round(lng, 2)


@lru_cache(maxsize=512)
def _valid_tz(name):
    try:
        ZoneInfo(name)
        return True
    except (ValueError, ZoneInfoNotFoundError, OSError):
        return False


def parse_timezone(value):
    if not isinstance(value, str) or not value or len(value) > 64 or not _TZ_RE.match(value):
        return None
    return value if _valid_tz(value) else None


def snap(anchor):
    return round(round(anchor[0] / GRID) * GRID, 4), round(round(anchor[1] / GRID) * GRID, 4)


def set_request(anchor, tz, layout):
    return _ANCHOR.set(anchor), _TZ.set(tz), _LAYOUT.set(layout)


def reset_request(tokens):
    _ANCHOR.reset(tokens[0]); _TZ.reset(tokens[1]); _LAYOUT.reset(tokens[2])


def current_anchor():
    return _ANCHOR.get()


def current_layout():
    return _LAYOUT.get()


def default_origin():
    """Where distances are measured from when the client supplied no coordinates."""
    anchor, layout = _ANCHOR.get(), _LAYOUT.get()
    if anchor and layout and layout.mode == 'relocated':
        return anchor
    return SF_CENTRE


def haversine_m(a, b):
    r = math.radians
    h = math.sin(r(b[0] - a[0]) / 2) ** 2 + math.cos(r(a[0])) * math.cos(r(b[0])) * math.sin(r(b[1] - a[1]) / 2) ** 2
    return 12742000 * math.asin(min(1, math.sqrt(h)))


def bearing_deg(a, b):
    r = math.radians
    y = math.sin(r(b[1] - a[1])) * math.cos(r(b[0]))
    x = math.cos(r(a[0])) * math.sin(r(b[0])) - math.sin(r(a[0])) * math.cos(r(b[0])) * math.cos(r(b[1] - a[1]))
    return math.degrees(math.atan2(y, x)) % 360


def destination(origin, bearing, km):
    lat1, lon1, br, d = math.radians(origin[0]), math.radians(origin[1]), math.radians(bearing), km / 6371.0088
    lat2 = math.asin(math.sin(lat1) * math.cos(d) + math.cos(lat1) * math.sin(d) * math.cos(br))
    lon2 = lon1 + math.atan2(math.sin(br) * math.sin(d) * math.cos(lat1), math.cos(d) - math.sin(lat1) * math.sin(lat2))
    return round(math.degrees(lat2), 6), round((math.degrees(lon2) + 540) % 360 - 180, 6)


_MAX_ORIG_KM = max(haversine_m(SF_CENTRE, (s.lat, s.lng)) for s in DEMO_STORES) / 1000


def candidate(store, cell, attempt):
    """Deterministic point for ``store`` around ``cell``; later attempts rotate/shrink to dodge water or duplicates."""
    km = haversine_m(SF_CENTRE, (store.lat, store.lng)) / 1000
    bearing = bearing_deg(SF_CENTRE, (store.lat, store.lng))
    mapped = RING_MIN_KM + (RING_MAX_KM - RING_MIN_KM) * min(1.0, km / _MAX_ORIG_KM)
    rotate, scale = ATTEMPTS[attempt % len(ATTEMPTS)]
    return destination(cell, (bearing + rotate) % 360, mapped * scale)


@dataclass(frozen=True)
class Hit:
    lat: float
    lng: float
    address: str
    rank: int
    precise: bool


class ProviderError(Exception):
    pass


_google_blocked_until = 0.0
_per_loop: 'weakref.WeakKeyDictionary' = weakref.WeakKeyDictionary()


def _loop_state():
    loop = asyncio.get_running_loop()
    state = _per_loop.get(loop)
    if state is None:
        state = _per_loop[loop] = {'nominatim_lock': asyncio.Lock(), 'nominatim_last': 0.0, 'sem': asyncio.Semaphore(6)}
    return state


def google_key():
    from .routing import google_key as key
    return key()


_PLUS_CODE = re.compile(r'[23456789CFGHJMPQRVWX]{4,}\+[23456789CFGHJMPQRVWX]{2,}')
_BAD_PLACE_TYPES = {'transit_station', 'bus_station', 'train_station', 'subway_station', 'light_rail_station', 'airport', 'hospital',
    'health', 'doctor', 'place_of_worship', 'church', 'mosque', 'hindu_temple', 'synagogue', 'school', 'primary_school',
    'secondary_school', 'university', 'local_government_office', 'embassy', 'courthouse', 'city_hall', 'police', 'fire_station',
    'cemetery', 'stadium', 'park', 'natural_feature', 'establishment_government'}
_BAD_NAME = re.compile(r'\b(istana|palace|station|stesen|depot|terminal|airport|hospital|embassy|mosque|masjid|church|temple|'
                       r'kementerian|ministry|court|police|university|school|cemetery|stadium)\b', re.I)


def clean_address(address, types):
    """Drop a leading point-of-interest segment that merely repeats the next one or precedes the street number."""
    parts = [x.strip() for x in address.split(',')]
    if len(parts) > 2 and types & {'premise', 'establishment', 'point_of_interest', 'subpremise'}:
        if parts[0].lower() == parts[1].lower() or (not re.search(r'\d', parts[0]) and re.search(r'\d', parts[1])):
            parts = parts[1:]
    return ', '.join(parts)


def _google_hit(item):
    types = set(item.get('types', []))
    loc = item.get('geometry', {}).get('location', {})
    address = item.get('formatted_address') or ''
    if not isinstance(loc.get('lat'), (int, float)) or not isinstance(loc.get('lng'), (int, float)) or not address:
        return None
    first = address.split(',')[0]
    if _PLUS_CODE.search(first) or types <= {'plus_code'} or address.lower().startswith('plus code'):
        return None
    if types & _BAD_PLACE_TYPES or _BAD_NAME.search(first):
        return None
    head = ', '.join(address.split(',')[:2])
    if 'street_address' in types:
        precise = True
    elif types & {'premise', 'subpremise'}:
        if not re.search(r'\d', head):  # a bare building name is not a shop-like street address
            return None
        precise = True
    else:
        precise = False  # route only: last resort
    rank = {'ROOFTOP': 4, 'RANGE_INTERPOLATED': 3, 'GEOMETRIC_CENTER': 2}.get(item.get('geometry', {}).get('location_type'), 1)
    bonus = 3 if 'street_address' in types else 1 if precise else 0
    return Hit(float(loc['lat']), float(loc['lng']), clean_address(address, types), rank + bonus, precise)


async def _google_reverse(lat, lng, key):
    params = {'latlng': f'{lat:.6f},{lng:.6f}', 'result_type': 'street_address|premise|route', 'language': 'en', 'key': key}
    async with httpx.AsyncClient(timeout=httpx.Timeout(4.0, connect=3.0)) as client:
        response = await client.get('https://maps.googleapis.com/maps/api/geocode/json', params=params)
    if response.status_code != 200:
        raise ProviderError(f'google http {response.status_code}')
    data = response.json()
    status = data.get('status')
    if status == 'ZERO_RESULTS':
        return []
    if status != 'OK':
        raise ProviderError('google ' + str(status))
    hits = []
    for item in data.get('results', [])[:10]:
        hit = _google_hit(item)
        if hit:
            hits.append(hit)
    return hits


_BAD_CATEGORIES = {'natural', 'waterway', 'water', 'boundary', 'landuse'}
_BAD_TYPES = {'water', 'bay', 'strait', 'coastline', 'sea', 'ocean', 'lake', 'river', 'reservoir', 'wetland', 'beach'}


async def _nominatim_reverse(lat, lng):
    state = _loop_state()
    async with state['nominatim_lock']:  # public usage policy: at most one request per second
        wait = 1.1 - (time.monotonic() - state['nominatim_last'])
        if wait > 0:
            await asyncio.sleep(wait)
        state['nominatim_last'] = time.monotonic()
        async with httpx.AsyncClient(timeout=httpx.Timeout(5.0, connect=3.0), headers={
                'User-Agent': 'PayFound-local-demo/1.0 (hackathon demo; placement of fictional stores)', 'Accept-Language': 'en'}) as client:
            response = await client.get('https://nominatim.openstreetmap.org/reverse', params={
                'format': 'jsonv2', 'lat': f'{lat:.6f}', 'lon': f'{lng:.6f}', 'zoom': 18, 'addressdetails': 1})
    if response.status_code != 200:
        raise ProviderError(f'nominatim http {response.status_code}')
    data = response.json()
    if not isinstance(data, dict) or data.get('error'):
        return []
    address = data.get('address') or {}
    if str(data.get('category', '')) in _BAD_CATEGORIES or str(data.get('type', '')) in _BAD_TYPES:
        return []
    if not (address.get('road') or address.get('house_number')):
        return []
    try:
        point = float(data['lat']), float(data['lon'])
    except (KeyError, TypeError, ValueError):
        return []
    precise = bool(address.get('house_number'))
    return [Hit(point[0], point[1], str(data.get('display_name') or '')[:250], 4 if precise else 2, precise)]


async def reverse_geocode(lat, lng):
    """Hits near (lat, lng). Google when keyed (falls back to Nominatim on provider errors). May raise ProviderError."""
    global _google_blocked_until
    key = google_key()
    if key and time.monotonic() >= _google_blocked_until:
        try:
            return await _google_reverse(lat, lng, key), 'google'
        except (ProviderError, httpx.HTTPError, ValueError) as exc:
            if 'REQUEST_DENIED' in str(exc):
                _google_blocked_until = time.monotonic() + 300
            log.info('google geocoding failed (%s); using nominatim', exc)
    try:
        return await _nominatim_reverse(lat, lng), 'nominatim'
    except (httpx.HTTPError, ValueError) as exc:
        raise ProviderError(str(exc)) from None


def choose(point, hits):
    """Best land hit within SNAP_RADIUS_M of the candidate."""
    near = [h for h in hits if haversine_m(point, (h.lat, h.lng)) <= SNAP_RADIUS_M]
    if not near:
        return None
    return max(near, key=lambda h: (h.rank, -haversine_m(point, (h.lat, h.lng))))


_WET_PARK_TYPES = {'park', 'natural_feature', 'campground', 'zoo', 'cemetery', 'amusement_park', 'stadium', 'golf_course', 'rv_park'}
_WET_PARK_WORDS = re.compile(r'\b(lake|tasik|reservoir|river|sungai|park|taman negara|pond|canal|beach|bay|harbou?r|marina|pier|wharf|'
                             r'forest|reserve|garden|gardens)\b', re.I)


_HILL_WORDS = re.compile(r'\b(hill|hills|mountain|mount|gunung|peak|summit|ridge|highland|highlands)\b', re.I)
# A store may sit at most this far above the cell centre: keeps stores off hills and mountainsides.
HILL_RISE_M = 120.0
_ELEV_CACHE: dict = {}


def point_is_land_like(results):
    """Pure check of an UNFILTERED reverse-geocode result list: reject points inside or beside parks, water or hills."""
    for i, item in enumerate(results[:4]):
        if set(item.get('types', [])) & _WET_PARK_TYPES:
            return False
        if i == 0 and _WET_PARK_WORDS.search((item.get('formatted_address') or '').split(',')[0]):
            return False
        if i == 0 and _HILL_WORDS.search((item.get('formatted_address') or '').split(',')[0]):
            return False
    return True


async def elevation_m(lat, lng):
    """Ground height in metres from Google's Elevation API (cached). None when unavailable."""
    key = google_key()
    if not key or time.monotonic() < _google_blocked_until:
        return None
    cache_key = (round(lat, 3), round(lng, 3))
    if cache_key in _ELEV_CACHE:
        return _ELEV_CACHE[cache_key]
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(4.0, connect=3.0)) as client:
            response = await client.get('https://maps.googleapis.com/maps/api/elevation/json',
                                        params={'locations': f'{lat:.6f},{lng:.6f}', 'key': key})
        data = response.json()
        value = float(data['results'][0]['elevation']) if response.status_code == 200 and data.get('status') == 'OK' else None
    except (httpx.HTTPError, ValueError, KeyError, IndexError, TypeError):
        value = None
    if len(_ELEV_CACHE) > 5000:
        _ELEV_CACHE.clear()
    _ELEV_CACHE[cache_key] = value
    return value


async def verify_spot(lat, lng, base):
    """Land/park/water check plus a height check: the spot must not be a hill or mountainside above the area."""
    if not await verify_point(lat, lng):
        return False
    if base is None:
        return True
    height = await elevation_m(lat, lng)
    return height is None or height <= base + HILL_RISE_M


async def verify_point(lat, lng):
    """One extra unfiltered Google lookup at the snapped point; True when it is not a park/water feature."""
    key = google_key()
    if not key or time.monotonic() < _google_blocked_until:
        return True
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(4.0, connect=3.0)) as client:
            response = await client.get('https://maps.googleapis.com/maps/api/geocode/json',
                                        params={'latlng': f'{lat:.6f},{lng:.6f}', 'language': 'en', 'key': key})
        data = response.json()
    except (httpx.HTTPError, ValueError):
        return True
    if response.status_code != 200 or data.get('status') != 'OK':
        return data.get('status') != 'ZERO_RESULTS' if response.status_code == 200 else True
    return point_is_land_like(data.get('results', []))


def _address_key(text):
    return re.sub(r'[^a-z0-9]+', ' ', text.lower()).strip()


MIN_PRECISE = 4  # relocate when at least this many stores get their own numbered street address on land
PROBE_RADII_KM = (2, 4, 8, 14, 24)
PROBE_BEARINGS = tuple(range(0, 360, 45))


async def compute_layout(cell, budget_s=None):
    budget_s = float(os.getenv('PF_PLACEMENT_BUDGET_S', '25')) if budget_s is None else budget_s
    deadline = time.monotonic() + budget_s
    sem = _loop_state()['sem']
    placed: dict[str, Hit] = {}
    taken_addresses: set[str] = set()
    stats = {'ok': 0, 'errors': 0, 'hits': 0, 'raw': 0, 'provider': ''}
    base = await elevation_m(*cell)  # ground height at the area centre; None if unavailable
    allow_routes = False  # road-centre hits can sit inside parks/lakes' paths; only used if too few real addresses exist

    def claim(store_id, hit):
        # Synchronous check-and-set: no two stores share an address or sit on top of each other.
        if hit.precise and _address_key(hit.address) in taken_addresses:
            return False
        if any(haversine_m((hit.lat, hit.lng), (o.lat, o.lng)) < MIN_SEPARATION_M for o in placed.values()):
            return False
        placed[store_id] = hit
        taken_addresses.add(_address_key(hit.address))
        return True

    async def lookup(point):
        async with sem:
            try:
                hits, provider = await reverse_geocode(*point)
            except ProviderError:
                stats['errors'] += 1
                return []
        stats['ok'] += 1
        stats['provider'] = provider
        return hits

    def usable(point, hits, radius=SNAP_RADIUS_M):
        if any(haversine_m(point, (h.lat, h.lng)) <= radius for h in hits):
            stats['raw'] += 1
        found = sorted((h for h in hits if haversine_m(point, (h.lat, h.lng)) <= radius and (h.precise or allow_routes)),
                       key=lambda h: (-h.rank, haversine_m(point, (h.lat, h.lng))))
        if found:
            stats['hits'] += 1
        return found

    async def pick(point, hits):
        for hit in usable(point, hits)[:3]:
            if await verify_spot(hit.lat, hit.lng, base):
                return hit
        return None

    async def place(store, attempts):
        for attempt in attempts:
            if time.monotonic() > deadline:
                return
            point = candidate(store, cell, attempt)
            hit = await pick(point, await lookup(point))
            if hit and claim(store.id, hit):
                return

    async def stage_one():
        await asyncio.gather(*(place(s, range(1)) for s in DEMO_STORES))
        if len(placed) < MIN_PRECISE:
            return  # mostly water/parks around: retrying nearby rings is wasteful, go straight to the wide search
        await asyncio.gather(*(place(s, range(1, len(ATTEMPTS))) for s in DEMO_STORES if s.id not in placed))

    async def widen():
        """Probe rings out to ~24 km for numbered street addresses on land and hand them to unplaced stores."""
        pool: list[Hit] = []
        for radius in PROBE_RADII_KM:
            if time.monotonic() > deadline or (stats['ok'] == 0 and stats['errors']) or len(pool) >= len(DEMO_STORES) - len(placed):
                break
            points = [destination(cell, b, radius) for b in PROBE_BEARINGS]
            for point, hits in zip(points, await asyncio.gather(*(lookup(p) for p in points))):
                best = usable(point, hits)
                if best:
                    pool.append(best[0])
        for store in DEMO_STORES:
            if store.id in placed or time.monotonic() > deadline:
                continue
            want = candidate(store, cell, 0)
            for hit in sorted(pool, key=lambda h: haversine_m(cell, (h.lat, h.lng)) * 0.5 + haversine_m(want, (h.lat, h.lng)) * 0.5):
                if hit.address and _address_key(hit.address) not in taken_addresses and await verify_spot(hit.lat, hit.lng, base) \
                        and claim(store.id, hit):
                    break

    await stage_one()
    if len(placed) < MIN_PRECISE:
        await widen()
    if len(placed) < MIN_PRECISE and time.monotonic() < deadline and stats['raw'] > 0:
        allow_routes = True
        await asyncio.gather(*(place(s, range(len(ATTEMPTS))) for s in DEMO_STORES if s.id not in placed))
        if len(placed) < MIN_PRECISE:
            await widen()
    # Remaining stores go next to the closest placed store, reusing every street address found while probing.
    if placed and len(placed) < len(DEMO_STORES):
        spare: list[Hit] = []
        for store in DEMO_STORES:
            if store.id in placed or time.monotonic() > deadline:
                continue
            want = candidate(store, cell, 0)
            for radius in (None, 0.15, 0.3, 0.6, 1.0):  # None = try the spare addresses already found
                if radius is not None:
                    anchor_hit = min(placed.values(), key=lambda h: haversine_m(want, (h.lat, h.lng)))
                    points = [destination((anchor_hit.lat, anchor_hit.lng), b, radius) for b in range(0, 360, 45)]
                    for point, hits in zip(points, await asyncio.gather(*(lookup(p) for p in points))):
                        spare += usable(point, hits)[:1]
                done = False
                for hit in sorted(spare, key=lambda h: (-h.rank, haversine_m(want, (h.lat, h.lng)))):
                    if _address_key(hit.address) in taken_addresses:
                        continue
                    if await verify_spot(hit.lat, hit.lng, base) and claim(store.id, hit):
                        done = True
                        break
                if done:
                    break
    n = len(DEMO_STORES)
    stores = {sid: Placed(round(h.lat, 6), round(h.lng, 6), h.address) for sid, h in placed.items()}
    if len(stores) >= MIN_PRECISE:
        reason = 'ok' if len(stores) == n else f'{n - len(stores)} store(s) could not be placed on land and keep their original position'
        return Layout('relocated', cell, reason, stores, len(stores), n, stats['provider'])
    reason = 'geocoder_unavailable' if stats['ok'] == 0 and stats['errors'] else 'not_enough_land_nearby'
    return Layout('original', cell, reason, {}, len(stores), n, stats['provider'])


_cache: 'OrderedDict[tuple, tuple[float, Layout]]' = OrderedDict()
_inflight: dict[tuple, asyncio.Task] = {}
_started: list[float] = []


def clear_cache():
    _cache.clear(); _inflight.clear(); _started.clear()


def _cached(cell):
    entry = _cache.get(cell)
    if not entry:
        return None
    if entry[0] < time.monotonic():
        _cache.pop(cell, None)
        return None
    _cache.move_to_end(cell)
    return entry[1]


def _remember(cell, layout):
    ttl = CACHE_TTL if layout.reason != 'geocoder_unavailable' else 120  # retry soon if the provider was down
    _cache[cell] = (time.monotonic() + ttl, layout)
    _cache.move_to_end(cell)
    while len(_cache) > CACHE_SIZE:
        _cache.popitem(last=False)


async def _run(cell):
    try:
        layout = await compute_layout(cell)
    except Exception:  # never let a geocoder bug break browsing
        log.exception('placement failed for cell %s', cell)
        layout = Layout('original', cell, 'internal_error', {}, 0)
    _remember(cell, layout)
    return layout


def warm(anchor):
    """Start computing the anchor's cell in the background (no waiting). Safe to call repeatedly."""
    cell = snap(anchor)
    if _cached(cell) is not None:
        return
    task = _inflight.get(cell)
    if task is not None and not task.done() and task.get_loop() is asyncio.get_running_loop():
        return
    now = time.monotonic()
    _started[:] = [t for t in _started if now - t < 3600]
    if len(_started) >= MAX_NEW_CELLS_PER_HOUR:
        return
    _started.append(now)
    task = asyncio.get_running_loop().create_task(_run(cell))
    _inflight[cell] = task
    task.add_done_callback(lambda t, c=cell: _inflight.pop(c, None) if _inflight.get(c) is t else None)


def full_wait_s():
    """How long /api/demo/placement waits: the complete compute budget (data requests wait far less)."""
    return float(os.getenv('PF_PLACEMENT_BUDGET_S', '25')) + 3


async def layout_for(anchor, wait_s=None):
    """Layout for the anchor's cell, awaiting a shared computation up to ``wait_s``; None if not ready in time."""
    wait_s = float(os.getenv('PF_PLACEMENT_WAIT_S', '8')) if wait_s is None else wait_s
    cell = snap(anchor)
    hit = _cached(cell)
    if hit:
        return hit
    task = _inflight.get(cell)
    if task is not None and (task.done() or task.get_loop() is not asyncio.get_running_loop()):
        task = None
    if task is None:
        now = time.monotonic()
        _started[:] = [t for t in _started if now - t < 3600]
        if len(_started) >= MAX_NEW_CELLS_PER_HOUR:
            return Layout('original', cell, 'rate_limited', {}, 0)
        _started.append(now)
        task = asyncio.get_running_loop().create_task(_run(cell))
        _inflight[cell] = task
        task.add_done_callback(lambda t, c=cell: _inflight.pop(c, None) if _inflight.get(c) is t else None)
    try:
        return await asyncio.wait_for(asyncio.shield(task), wait_s)
    except asyncio.TimeoutError:
        return None


def _near(value, expected):
    return isinstance(value, (int, float)) and abs(value - expected) < 1e-4


def _overlay_merchant(target, *_):
    layout = _LAYOUT.get()
    if layout is None or layout.mode != 'relocated':
        return
    data = target.__dict__
    store = DEMO_BY_ID.get(data.get('id'))
    if store is None or data.get('slug') != store.slug:
        return
    spot = layout.stores.get(store.id)
    if spot is None or not (_near(data.get('latitude'), store.lat) and _near(data.get('longitude'), store.lng)):
        return  # a merchant who edited their own coordinates keeps them
    set_committed_value(target, 'latitude', spot.lat)
    set_committed_value(target, 'longitude', spot.lng)
    set_committed_value(target, 'address', spot.address)
    if 'name' in data:
        set_committed_value(target, 'name', neutral(data['name']))


def _overlay_location(target, *_):
    layout = _LAYOUT.get()
    if layout is None or layout.mode != 'relocated':
        return
    data = target.__dict__
    store = DEMO_BY_LOC.get(data.get('id'))
    if store is None or data.get('merchant_id') != store.merchant_id:
        return
    spot = layout.stores.get(store.id)
    if spot is None or not (_near(data.get('latitude'), store.lat) and _near(data.get('longitude'), store.lng)):
        return
    set_committed_value(target, 'latitude', spot.lat)
    set_committed_value(target, 'longitude', spot.lng)
    set_committed_value(target, 'address', spot.address)
    tz = _TZ.get()
    if tz:
        set_committed_value(target, 'timezone', tz)
    if 'name' in data:
        set_committed_value(target, 'name', neutral(data['name']))


for _model, _fn in ((Merchant, _overlay_merchant), (MerchantLocation, _overlay_location)):
    event.listen(_model, 'load', _fn)
    event.listen(_model, 'refresh', _fn)

"""Google traffic-aware driving routes, with an explicit OSRM demo fallback."""
from datetime import datetime, timedelta, timezone
import hashlib
import math
import os
import re

from fastapi import APIRouter, Depends, HTTPException, Request, Response
import httpx
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .database import db_session
from .models import Merchant, MerchantLocation, Product
from .llm import budget

router = APIRouter(prefix='/routing', tags=['Directions'])


def google_key():
    return os.getenv('GOOGLE_ROUTES_API_KEY') or os.getenv('GOOGLE_MAPS_API_KEY') or os.getenv('GOOGLE_MAP_API_KEY', '')


def browser_key():
    # A dedicated referrer-restricted browser key can be supplied separately.
    # The user's general Maps key is usable for their loopback demo only.
    shared_maps_key = os.getenv('GOOGLE_MAPS_API_KEY') or os.getenv('GOOGLE_MAP_API_KEY', '')
    return os.getenv('GOOGLE_MAPS_BROWSER_KEY') or (shared_maps_key if os.getenv('DEMO_MODE', 'false').lower() == 'true' else '')


def capabilities():
    return {'road_routes': True, 'traffic_configured': bool(google_key()),
            'provider': 'google' if google_key() else 'osrm', 'refresh_seconds': 60,
            'google_maps_browser_key': browser_key(), 'google_maps_map_id': os.getenv('GOOGLE_MAPS_MAP_ID', 'DEMO_MAP_ID')}


class RouteInput(BaseModel):
    product_id: str = Field(min_length=1, max_length=48)
    origin_latitude: float = Field(ge=-90, le=90, allow_inf_nan=False)
    origin_longitude: float = Field(ge=-180, le=180, allow_inf_nan=False)


async def fetch_json(method, url, **kwargs):
    try:
        async with httpx.AsyncClient(timeout=18, follow_redirects=False) as client:
            response = await client.request(method, url, **kwargs)
        if response.status_code == 429:
            raise HTTPException(429, 'Directions provider is busy. Try again shortly.', headers={'Retry-After': '30'})
        if response.status_code in (401, 403):
            raise HTTPException(503, 'Google routing access is unavailable. Check Routes API, billing and key restrictions.')
        if response.status_code >= 400:
            raise HTTPException(502, 'Directions provider unavailable. Open external navigation or try again.')
        if len(response.content) > 4_000_000:
            raise ValueError('Oversized route response')
        return response.json()
    except (httpx.HTTPError, ValueError):
        raise HTTPException(502, 'Directions could not be loaded. No route or travel time has been assumed.') from None


def geometry(points):
    if not isinstance(points, list) or not 2 <= len(points) <= 50000:
        raise HTTPException(502, 'Provider returned an invalid route')
    for point in points:
        if not isinstance(point, (list, tuple)) or len(point) < 2 or not all(
            isinstance(n, (float, int)) and math.isfinite(n) for n in point[:2]) or not (
                -180 <= point[0] <= 180 and -90 <= point[1] <= 90):
            raise HTTPException(502, 'Provider returned invalid route coordinates')
    return points


def decode_polyline(encoded):
    if not isinstance(encoded, str) or len(encoded) > 200000:
        raise ValueError('Invalid encoded polyline')
    points, index, lat, lng = [], 0, 0, 0
    while index < len(encoded):
        values = []
        for _ in range(2):
            value, shift = 0, 0
            while True:
                if index >= len(encoded) or shift > 35:
                    raise ValueError('Invalid encoded coordinate')
                byte = ord(encoded[index]) - 63
                if not 0 <= byte <= 63:
                    raise ValueError('Invalid encoded byte')
                index += 1
                value |= (byte & 31) << shift
                shift += 5
                if byte < 32:
                    break
            values.append(~(value >> 1) if value & 1 else value >> 1)
        lat += values[0]; lng += values[1]
        points.append([lng / 100000, lat / 100000])
    return geometry(points)


def seconds(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d+(?:\.\d+)?s', value):
        raise ValueError('Invalid provider duration')
    return float(value[:-1])


async def calculate(origin, destination):
    now = datetime.now(timezone.utc)
    if google_key():
        waypoint = lambda pair: {'location': {'latLng': {'latitude': pair[0], 'longitude': pair[1]}}}
        data = await fetch_json('POST', 'https://routes.googleapis.com/directions/v2:computeRoutes',
            headers={'X-Goog-Api-Key': google_key(), 'X-Goog-FieldMask': ','.join([
                'routes.duration', 'routes.staticDuration', 'routes.distanceMeters', 'routes.polyline.encodedPolyline',
                'routes.legs.steps.navigationInstruction.instructions', 'routes.legs.steps.distanceMeters'])},
            json={'origin': waypoint(origin), 'destination': waypoint(destination), 'travelMode': 'DRIVE',
                  'routingPreference': 'TRAFFIC_AWARE', 'computeAlternativeRoutes': False,
                  'polylineQuality': 'HIGH_QUALITY', 'languageCode': 'en-US', 'units': 'METRIC'})
        if not data.get('routes'):
            raise HTTPException(404, 'No driving route found between your location and this store')
        route = data['routes'][0]
        points = decode_polyline(route['polyline']['encodedPolyline'])
        distance, duration = route['distanceMeters'], seconds(route['duration'])
        baseline = seconds(route['staticDuration'])
        steps = [{'instruction': str(s.get('navigationInstruction', {}).get('instructions', 'Continue'))[:500],
                  'distance_m': s.get('distanceMeters', 0)} for leg in route.get('legs', []) for s in leg.get('steps', [])]
        provider, attribution, traffic = 'google', 'Google Maps', True
        delay = max(0, duration - baseline)
    else:
        url = f'https://router.project-osrm.org/route/v1/driving/{origin[1]:.6f},{origin[0]:.6f};{destination[1]:.6f},{destination[0]:.6f}'
        data = await fetch_json('GET', url, params={'overview': 'full', 'geometries': 'geojson', 'steps': 'true',
            'alternatives': 'false', 'radiuses': '1000;1000'})
        if data.get('code') != 'Ok' or not data.get('routes'):
            raise HTTPException(404, 'No driving route found between your location and this store')
        route = data['routes'][0]
        points = geometry(route.get('geometry', {}).get('coordinates'))
        distance, duration = route['distance'], route['duration']
        delay, baseline, traffic = None, duration, False
        steps = []
        for leg in route.get('legs', []):
            for step in leg.get('steps', []):
                maneuver = step.get('maneuver', {})
                instruction = ' '.join(str(maneuver.get(k, '')).replace('_', ' ') for k in ('type', 'modifier')).strip().capitalize()
                if step.get('name'):
                    instruction += ' · ' + str(step['name'])
                steps.append({'instruction': instruction[:500], 'distance_m': step.get('distance', 0)})
        provider, attribution = 'osrm', 'OSRM · © OpenStreetMap contributors'
    if not all(isinstance(n, (int, float)) and math.isfinite(n) and n >= 0 for n in (distance, duration, baseline)):
        raise ValueError('Invalid provider travel estimate')
    return {'provider': provider, 'attribution': attribution, 'distance_m': round(distance), 'duration_seconds': round(duration),
        'static_duration_seconds': round(baseline), 'traffic_aware': traffic, 'traffic_delay_seconds': delay,
        'coordinates': points, 'steps': steps[:50], 'fetched_at': now.isoformat(),
        'arrival_at': (now + timedelta(seconds=duration)).isoformat(),
        'estimate_label': 'Google Maps · traffic-aware driving estimate' if traffic else 'Driving estimate · without live traffic'}


@router.post('/route')
async def route(body: RouteInput, request: Request, response: Response, db: Session = Depends(db_session)):
    identity = hashlib.sha256((request.client.host if request.client else 'unknown').encode()).hexdigest()
    if not budget.allow('road-route:' + identity, 20):
        raise HTTPException(429, 'Too many directions requests. Try again shortly.', headers={'Retry-After': '60'})
    product = db.get(Product, body.product_id)
    if not product or not product.active:
        raise HTTPException(404, 'Product not found')
    location = db.get(MerchantLocation, product.location_id) if product.location_id else None
    merchant = db.get(Merchant, product.merchant_id)
    if not merchant or (location and not location.active):
        raise HTTPException(404, 'Store location unavailable')
    destination = (location.latitude, location.longitude) if location else (merchant.latitude, merchant.longitude)
    try:
        data = await calculate((body.origin_latitude, body.origin_longitude), destination)
    except (ValueError, KeyError, TypeError, IndexError):
        raise HTTPException(502, 'Directions provider returned an incomplete route') from None
    response.headers['Cache-Control'] = 'no-store'
    return {**data, 'product_id': product.id, 'merchant_id': merchant.id, 'destination': {
        'latitude': destination[0], 'longitude': destination[1], 'name': merchant.name,
        'address': location.address if location else merchant.address}}

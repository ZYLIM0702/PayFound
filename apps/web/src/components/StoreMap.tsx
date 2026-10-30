import { MapContainer, TileLayer, Marker, Polyline, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import { useEffect, useMemo } from 'react';
import { Link } from 'react-router-dom';
import type { DrivingRoute } from '../lib/directions';
import { useApp } from '../lib/app-context';
import { useUserLocation } from '../lib/location';
import { GoogleStoreMap, type InteractiveMapProps } from './GoogleStoreMap';
import '../styles/discovery.css';
import '../styles/components/leaflet.css';

const PIN_SVG = '<svg width="28" height="36" viewBox="0 0 28 36" aria-hidden="true"><path d="M14 1C6.8 1 1 6.8 1 14c0 9.6 13 21 13 21s13-11.4 13-21C27 6.8 21.2 1 14 1z" fill="currentColor" stroke="#fff" stroke-width="2"/><circle cx="14" cy="14" r="4.5" fill="#fff"/></svg>';
const makePin = (selected: boolean) => L.divIcon({ className: 'pf-pin-wrap', html: `<span class="pf-pin${selected ? ' selected' : ''}">${PIN_SVG}</span>`, iconSize: [28, 36], iconAnchor: [14, 36], popupAnchor: [0, -32] });
const pins = { base: makePin(false), selected: makePin(true) };
const userIcon = L.divIcon({ className: 'pf-pin-wrap', html: '<span class="pf-user-location-pin"></span>', iconSize: [16, 16], iconAnchor: [8, 8] });

function Fit({ merchants, center, hold }: { merchants: InteractiveMapProps['merchants']; center: [number, number]; hold: boolean }) {
  const map = useMap();
  useEffect(() => {
    const frame = requestAnimationFrame(() => {
      map.invalidateSize({ animate: false, pan: false });
      if (hold) return;
      if (merchants.length) map.fitBounds(L.latLngBounds(merchants.map(m => [m.latitude, m.longitude] as [number, number])).pad(0.25), { maxZoom: 14, animate: false });
      else map.setView(center, 12, { animate: false });
    });
    return () => cancelAnimationFrame(frame);
  }, [map, merchants, center, hold]);
  return null;
}

function FocusOn({ focus, version }: { focus: NonNullable<InteractiveMapProps['focus']>; version: number }) {
  const map = useMap();
  useEffect(() => { map.setView([focus.latitude, focus.longitude], 15, { animate: false }); }, [map, focus.id, focus.latitude, focus.longitude, version]);
  return null;
}

function RouteLine({ route }: { route: DrivingRoute }) {
  const map = useMap();
  const path = useMemo(() => route.coordinates.map(([lng, lat]) => [lat, lng] as [number, number]), [route]);
  useEffect(() => { if (path.length) map.fitBounds(L.latLngBounds(path).pad(0.15), { animate: false }); }, [map, path]);
  return <Polyline positions={path} pathOptions={{ color: '#0057ff', weight: 5, opacity: 0.9 }} />;
}

export function StoreMap(props: InteractiveMapProps) {
  const { config } = useApp();
  const key = config?.routing?.google_maps_browser_key;
  if (key) return <GoogleStoreMap {...props} apiKey={key} mapId={config.routing?.google_maps_map_id || 'DEMO_MAP_ID'} />;
  return <LegacyStoreMap {...props} />;
}

function LegacyStoreMap({ merchants, center: centerProp, focus, focusVersion = 0, userPosition, route, scrollZoom = false, onSelectMerchant }: InteractiveMapProps) {
  const { anchor } = useUserLocation();
  const center: [number, number] = centerProp ?? [anchor.latitude, anchor.longitude];
  return <div className="pf-map" data-testid="store-map" data-provider="leaflet" data-focus-id={focus?.id || ''}>
    <MapContainer center={center} zoom={12} zoomAnimation={false} fadeAnimation={false} markerZoomAnimation={false} style={{ height: '100%', width: '100%' }} scrollWheelZoom={scrollZoom}>
      <TileLayer attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      <Fit merchants={merchants} center={center} hold={Boolean(focus || route)} />
      {focus && <FocusOn focus={focus} version={focusVersion} />}
      {merchants.map(m => <Marker key={m.id} position={[m.latitude, m.longitude]} icon={focus?.merchant_id === m.id ? pins.selected : pins.base} zIndexOffset={focus?.merchant_id === m.id ? 1000 : 0} eventHandlers={{ click: () => onSelectMerchant?.(m.id) }}>
        <Popup><strong>{m.name}</strong><p>{m.category} · {m.is_open ? 'Open now' : m.is_open === false ? 'Closed' : 'Check hours'}</p><Link to={`/stores/${m.slug}`}>View store →</Link></Popup>
      </Marker>)}
      {userPosition && <Marker position={[userPosition.latitude, userPosition.longitude]} icon={userIcon} interactive={false} keyboard={false} zIndexOffset={900} />}
      {route && route.provider !== 'google' && <RouteLine route={route} />}
    </MapContainer>
  </div>;
}

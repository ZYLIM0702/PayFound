import { useEffect, useRef, useState } from 'react';
import { Layers3 } from 'lucide-react';
import type { Merchant } from '../lib/api';
import type { DrivingRoute } from '../lib/directions';
import { useUserLocation, type UserPosition } from '../lib/location';

export type MapFocus = { id: string; name: string; latitude: number; longitude: number; merchant_id: string };
export type InteractiveMapProps = { merchants: Merchant[]; center?: [number, number]; focus?: MapFocus | null;
  focusVersion?: number; userPosition?: UserPosition | null; route?: DrivingRoute | null; scrollZoom?: boolean; onSelectMerchant?: (id: string) => void };
declare global { interface Window { __payfoundGoogleMapsReady?: () => void; gm_authFailure?: () => void } }
const PIN_SVG = '<svg width="28" height="36" viewBox="0 0 28 36" aria-hidden="true"><path d="M14 1C6.8 1 1 6.8 1 14c0 9.6 13 21 13 21s13-11.4 13-21C27 6.8 21.2 1 14 1z" fill="currentColor" stroke="#fff" stroke-width="2"/><circle cx="14" cy="14" r="4.5" fill="#fff"/></svg>';
let readyPromise: Promise<void> | null = null;

function loadGoogleMaps(key: string) {
  if (typeof google !== 'undefined' && typeof google.maps?.importLibrary === 'function') return Promise.resolve();
  if (!readyPromise) readyPromise = new Promise<void>((resolve, reject) => {
    window.__payfoundGoogleMapsReady = () => resolve();
    window.gm_authFailure = () => reject(new Error('Google Maps authorization failed. Check Maps JavaScript API, billing and website restrictions.'));
    const script = document.createElement('script');
    const params = new URLSearchParams({ key, loading: 'async', callback: '__payfoundGoogleMapsReady', v: 'weekly', libraries: 'maps,marker' });
    script.src = 'https://maps.googleapis.com/maps/api/js?' + params;
    script.async = true;
    script.onerror = () => { readyPromise = null; reject(new Error('Google Maps could not load. Check your connection.')); };
    document.head.append(script);
  });
  return readyPromise;
}

export function GoogleStoreMap({ apiKey, mapId, merchants, center: centerProp, focus,
  focusVersion = 0, userPosition, route, scrollZoom = false, onSelectMerchant }: InteractiveMapProps & { apiKey: string; mapId: string }) {
  const { anchor } = useUserLocation();
  const center = centerProp ?? [anchor.latitude, anchor.longitude];
  const container = useRef<HTMLDivElement>(null);
  const map = useRef<google.maps.Map | null>(null);
  const [ready, setReady] = useState(false);
  const [tilesReady, setTilesReady] = useState(false);
  const [error, setError] = useState('');
  const [traffic, setTraffic] = useState(true);
  const signature = merchants.map(m => `${m.id}:${m.latitude}:${m.longitude}`).join('|');
  const centerLat = center[0], centerLng = center[1];
  useEffect(() => {
    let alive = true;
    void loadGoogleMaps(apiKey).then(async () => {
      const [{ Map }] = await Promise.all([google.maps.importLibrary('maps') as Promise<google.maps.MapsLibrary>, google.maps.importLibrary('marker')]);
      if (!alive || !container.current) return;
      map.current = new Map(container.current, { center: { lat: centerLat, lng: centerLng }, zoom: 13,
        mapId, mapTypeControl: false, streetViewControl: false, fullscreenControl: true, gestureHandling: scrollZoom ? 'greedy' : 'cooperative' });
      map.current.addListener('idle', () => {
        if (container.current && map.current) {
          setTilesReady(true);
          container.current.dataset.mapZoom = String(map.current.getZoom());
          container.current.dataset.mapLatitude = String(map.current.getCenter()?.lat());
          container.current.dataset.mapLongitude = String(map.current.getCenter()?.lng());
        }
      });
      setReady(true);
    }).catch(issue => { if (alive) setError(issue instanceof Error ? issue.message : 'Google Maps unavailable'); });
    return () => { alive = false; if (map.current) google.maps.event.clearInstanceListeners(map.current); map.current = null; };
  }, [apiKey, mapId]);
  useEffect(() => {
    if (!ready || !map.current) return;
    const windowInfo = new google.maps.InfoWindow();
    const markers = merchants.map(merchant => {
      const position = focus?.merchant_id === merchant.id ? { lat: focus.latitude, lng: focus.longitude }
        : { lat: merchant.latitude, lng: merchant.longitude };
      const element = document.createElement('div');
      element.className = 'pf-pin' + (focus?.merchant_id === merchant.id ? ' selected' : '');
      element.innerHTML = PIN_SVG; // static markup, no user data
      const marker = new google.maps.marker.AdvancedMarkerElement({ map: map.current!, position,
        title: merchant.name, content: element });
      marker.addListener('click', () => {
        onSelectMerchant?.(merchant.id);
        const card = document.createElement('div');
        const title = document.createElement('strong'); title.textContent = merchant.name;
        const text = document.createElement('p'); text.textContent = merchant.address;
        const link = document.createElement('a'); link.href = '/stores/' + encodeURIComponent(merchant.slug); link.textContent = 'View store →';
        card.append(title, text, link); windowInfo.setContent(card); windowInfo.open({ map: map.current, anchor: marker });
      });
      return marker;
    });
    return () => { windowInfo.close(); markers.forEach(marker => { marker.map = null; google.maps.event.clearInstanceListeners(marker); }); };
  }, [ready, merchants, focus, onSelectMerchant]);
  useEffect(() => {
    if (!ready || !map.current || focus || route) return;
    if (merchants.length) {
      const bounds = new google.maps.LatLngBounds(); merchants.forEach(m => bounds.extend({ lat: m.latitude, lng: m.longitude }));
      map.current.fitBounds(bounds, 45);
      google.maps.event.addListenerOnce(map.current, 'idle', () => { if ((map.current?.getZoom() || 0) > 15) map.current?.setZoom(15); });
    } else { map.current.panTo({ lat: centerLat, lng: centerLng }); map.current.setZoom(13); }
  }, [ready, signature, centerLat, centerLng, Boolean(focus), Boolean(route)]);
  useEffect(() => {
    if (!ready || !map.current || !focus) return;
    map.current.panTo({ lat: focus.latitude, lng: focus.longitude });
    map.current.setZoom(16);
  }, [ready, focus?.id, focus?.latitude, focus?.longitude, focusVersion]);
  useEffect(() => {
    if (!ready || !map.current || !userPosition) return;
    const markerElement = document.createElement('div'); markerElement.className = 'pf-user-location-pin';
    const marker = new google.maps.marker.AdvancedMarkerElement({ map: map.current, position: { lat: userPosition.latitude, lng: userPosition.longitude },
      title: 'Your shared location', content: markerElement });
    return () => { marker.map = null; };
  }, [ready, userPosition]);
  useEffect(() => {
    if (!ready || !map.current || !route || route.provider !== 'google') return;
    const path = route.coordinates.map(([lng, lat]) => ({ lat, lng }));
    const line = new google.maps.Polyline({ map: map.current, path, strokeColor: '#0057ff', strokeWeight: 5, strokeOpacity: .9, zIndex: 5 });
    const bounds = new google.maps.LatLngBounds(); path.forEach(point => bounds.extend(point));
    map.current.fitBounds(bounds, 55);
    return () => line.setMap(null);
  }, [ready, route]);
  useEffect(() => {
    if (!ready || !map.current || !traffic) return;
    const layer = new google.maps.TrafficLayer({ autoRefresh: true }); layer.setMap(map.current);
    return () => layer.setMap(null);
  }, [ready, traffic]);
  return <div className="pf-map"><div className="pf-google-map" ref={container} data-testid="store-map" data-provider="google" data-focus-id={focus?.id || ''} data-route-visible={Boolean(route && route.provider === 'google')} />
    {!tilesReady && !error && <div className="pf-map-loading">Loading Google Maps…</div>}{error && <div className="pf-map-loading" role="alert">{error}</div>}
    {ready && <button className={`pf-map-traffic-toggle ${traffic ? 'on' : ''}`} aria-pressed={traffic} onClick={() => setTraffic(value => !value)}><Layers3 size={14} />Traffic {traffic ? 'on' : 'off'}</button>}
  </div>;
}

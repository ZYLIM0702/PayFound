import type { UserPosition } from './location';

export type DrivingRoute = {
  provider: 'google' | 'osrm'; attribution: string; product_id: string; merchant_id: string;
  distance_m: number; duration_seconds: number; static_duration_seconds: number;
  traffic_aware: boolean; traffic_delay_seconds: number | null; coordinates: [number, number][];
  steps: { instruction: string; distance_m: number }[]; fetched_at: string; arrival_at: string;
  estimate_label: string; destination: { latitude: number; longitude: number; name: string; address: string };
};
export const formatDistance = (km: number) => km < 1 ? `${Math.round(km * 1000)} m` : `${km < 10 ? km.toFixed(1) : Math.round(km).toLocaleString()} km`;
export const formatDuration = (seconds: number) => seconds < 3600 ? `${Math.max(1, Math.round(seconds / 60))} min` : `${Math.floor(seconds / 3600)} hr ${Math.round(seconds % 3600 / 60)} min`;
export function googleDirections(destination: { latitude: number; longitude: number }, origin?: UserPosition | null) {
  const params = new URLSearchParams({ api: '1', destination: `${destination.latitude},${destination.longitude}`, travelmode: 'driving' });
  if (origin) params.set('origin', `${origin.latitude},${origin.longitude}`);
  return 'https://www.google.com/maps/dir/?' + params;
}

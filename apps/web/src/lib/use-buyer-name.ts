import { useEffect, useRef, useState } from 'react';
import { api } from './api';
import { useApp } from './app-context';

/**
 * Pickup name that defaults to the signed-in user's display name. Once the user types their own
 * value (even an empty one), the default is no longer applied.
 */
export function useBuyerName(): [string, (value: string) => void] {
  const { session, demo } = useApp();
  const [name, setName] = useState('');
  const touched = useRef(false);
  useEffect(() => {
    if (!session && !demo) return;
    let alive = true;
    api<{ display_name?: string }>('/me/profile')
      .then(profile => { if (alive && !touched.current && profile.display_name) setName(profile.display_name); })
      .catch(() => { /* no profile yet: leave the field empty */ });
    return () => { alive = false; };
  }, [session, demo]);
  return [name, (value: string) => { touched.current = true; setName(value); }];
}

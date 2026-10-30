import { useEffect, useState } from 'react';

export type TypedPhrase = { text: string; example: string };

/** Endings for "What are you …". Kept short so each fits one line at phone width. */
export const heroPhrases: TypedPhrase[] = [
  { text: 'looking for?', example: 'A 65W charger I can pick up tonight…' },
  { text: 'picking up today?', example: 'A bike light and pump from one store…' },
  { text: 'running low on?', example: 'Dog food near me that’s open now…' },
  { text: 'fixing today?', example: 'A cordless drill under $80 nearby…' },
  { text: 'gifting tonight?', example: 'A gift under $30 I can collect after work…' },
  { text: 'setting up?', example: 'A desk lamp and a USB-C hub, cheapest nearby…' },
];

const prefersReducedMotion = () => typeof window !== 'undefined' && window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;

/**
 * Display headline whose second line types, holds, deletes and retypes a set of
 * phrases. Screen readers get one stable heading; reduced motion shows the first
 * phrase statically. `paused` freezes on the current phrase (e.g. while the user types).
 */
export function TypedHeadline({ lead = 'What are you', phrases = heroPhrases, paused = false, onPhrase, className = '' }: {
  lead?: string; phrases?: TypedPhrase[]; paused?: boolean; onPhrase?: (phrase: TypedPhrase) => void; className?: string;
}) {
  const [index, setIndex] = useState(0);
  const [shown, setShown] = useState(phrases[0].text);
  const [deleting, setDeleting] = useState(false);
  const animate = phrases.length > 1 && !prefersReducedMotion();
  // Pausing (user focused the prompt) snaps to the full phrase rather than freezing mid-word.
  const [wasPaused, setWasPaused] = useState(paused);
  if (paused !== wasPaused) {
    setWasPaused(paused);
    if (paused) { setShown(phrases[index].text); setDeleting(false); }
  }

  useEffect(() => { onPhrase?.(phrases[index]); }, [index, phrases, onPhrase]);

  useEffect(() => {
    if (!animate || paused) return;
    const target = phrases[index].text;
    let delay: number;
    let step: () => void;
    if (!deleting && shown === target) { delay = 2400; step = () => setDeleting(true); }
    else if (deleting && shown === '') { delay = 320; step = () => { setDeleting(false); setIndex(i => (i + 1) % phrases.length); }; }
    else if (deleting) { delay = 26; step = () => setShown(s => s.slice(0, -1)); }
    else { delay = 48 + Math.random() * 46; step = () => setShown(target.slice(0, shown.length + 1)); }
    const timer = window.setTimeout(() => { if (document.visibilityState === 'visible') step(); }, delay);
    return () => window.clearTimeout(timer);
  }, [animate, paused, deleting, shown, index, phrases]);

  return <h1 className={className} aria-label={`${lead} ${phrases[0].text}`}>
    <span aria-hidden="true">{lead}</span><br />
    <span aria-hidden="true" className="pf-typed">
      <span className="pf-typed-line">{animate ? shown : phrases[0].text}{animate && <span className={`pf-caret ${shown === phrases[index].text && !deleting ? 'idle' : ''}`} />}</span>
      {/* Invisible longest phrase reserves width/height so the centred layout never jumps. */}
      <span className="pf-typed-sizer">{phrases.reduce((a, b) => a.text.length >= b.text.length ? a : b).text}</span>
    </span>
  </h1>;
}

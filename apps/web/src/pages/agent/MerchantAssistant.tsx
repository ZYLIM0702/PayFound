import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { AssistantSurface } from '../../components/assistant/AssistantSurface';
import { merchantStarters } from './starters';

type AskState = { ask?: string; fresh?: boolean } | null;

/** The overview links here with navigation state { ask }; the question is sent once, then the state is marked stale so a reload never re-sends it. */
export function MerchantAssistant({ merchantId }: { merchantId: string }) {
  const location = useLocation();
  const navigate = useNavigate();
  const state = location.state as AskState;
  const incoming = state?.ask && state.fresh !== false ? state.ask : undefined;
  const [session, setSession] = useState({ key: location.key, ask: incoming });
  if (incoming && location.key !== session.key) setSession({ key: location.key, ask: incoming });
  const sent = () => navigate(location.pathname + location.search, { replace: true, state: { ask: session.ask, fresh: false } });
  return <AssistantSurface key={session.key} surface="merchant" merchantId={merchantId} variant="page" starters={merchantStarters} title="How can I help run the store?" description="I read your live orders, stock, reviews and PayPal sandbox activity. I never change anything myself."
    initialQuestion={session.ask} onSent={session.ask ? sent : undefined}
    style={{ height: 'calc(100dvh - 64px)', minHeight: 420 }} />;
}

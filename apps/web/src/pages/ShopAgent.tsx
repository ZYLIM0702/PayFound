import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { AssistantGate } from '../components/assistant/AssistantGate';
import { AssistantSurface } from '../components/assistant/AssistantSurface';
import { shopperStarters } from './agent/starters';

type AskState = { ask?: string; fresh?: boolean } | null;

/**
 * Full-screen shopper assistant with the chat-history sidebar. Searches from the header or Home arrive as
 * navigation state { ask, fresh: true }: a fresh chat starts with that question, then the state is marked
 * stale so a reload never re-sends it.
 */
export function ShopAgent() {
  const location = useLocation();
  const navigate = useNavigate();
  const state = location.state as AskState;
  const [session, setSession] = useState({ key: location.key, ask: state?.fresh ? state.ask : undefined });
  if (state?.fresh && state.ask && location.key !== session.key) setSession({ key: location.key, ask: state.ask });
  const sent = () => navigate(location.pathname + location.search, { replace: true, state: { ask: session.ask, fresh: false } });
  return <AssistantGate next="/agent"><AssistantSurface key={session.key} surface="shopper" variant="page" starters={shopperStarters} initialQuestion={session.ask} onSent={session.ask ? sent : undefined}
    title="What can I find for you?" description="Ask in your own words. I check real stock at stores near you, show the route, and leave checkout to you." /></AssistantGate>;
}

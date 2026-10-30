import { Link } from 'react-router-dom';
import { useApp } from '../../lib/app-context';
import { Empty, Spinner } from '../Shared';

/** The assistant acts on behalf of a signed-in shopper (or the local demo role). */
export function AssistantGate({ children, next = '/' }: { children: React.ReactNode; next?: string }) {
  const { session, demo, ready } = useApp();
  if (!ready) return <Spinner label="Checking your session…" />;
  if (!session && !demo) return <Empty title="Sign in to ask PayFound" description="The assistant searches nearby stores on your behalf. Checkout always stays with you."><Link className="pf-btn" to={`/login?next=${encodeURIComponent(next)}`}>Log in</Link></Empty>;
  return <>{children}</>;
}

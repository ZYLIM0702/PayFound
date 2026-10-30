/**
 * PayFound logo mark (ribbon "P", public/brand/logo-mark.png) and wordmark.
 * The mark is decoupled from the wordmark so each can be used on its own.
 */
export function Monogram({ size = 28, className = '' }: { size?: number; inverted?: boolean; className?: string }) {
  return <img src="/brand/logo-mark.png" width={size} height={size} alt="" aria-hidden="true" draggable={false} className={`shrink-0 select-none ${className}`} />;
}

export function Brand({ inverted = false, mark = true }: { inverted?: boolean; mark?: boolean }) {
  return <span className="inline-flex items-center gap-2" aria-label="PayFound">
    {mark && <Monogram />}
    <span className={`font-display text-[21px] font-semibold tracking-[-0.04em] leading-none ${inverted ? 'text-white' : 'text-ink'}`}>PayFound</span>
  </span>;
}

/** The PayFound support agent, shown in a circle wherever the assistant introduces itself. */
export function AgentAvatar({ size = 40, className = '' }: { size?: number; className?: string }) {
  return <img src="/brand/agent-mascot.png" width={size} height={size} alt="PayFound assistant" draggable={false} className={`shrink-0 rounded-full bg-[#eaf2ff] object-cover ${className}`} />;
}

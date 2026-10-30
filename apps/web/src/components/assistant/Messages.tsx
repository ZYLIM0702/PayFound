import { useEffect, useRef } from 'react';
import { useThread, type AssistantMessage, type UserMessage } from '@openuidev/react-headless';
import { BuiltinActionType, Renderer, buildMessage, parseMessage, type ActionEvent } from '@openuidev/react-lang';
import { MarkDownRenderer } from '@openuidev/react-ui';
import { payfoundLibrary } from '../../pages/agent/library';
import { CopyButton, copyText } from './CopyButton';
import { imagesOf, textOf, visibleUserText } from './format';

/** OpenUI Lang (fenced or a bare `root = …`); anything else is a plain-text answer and shows as markdown. */
const hasLang = (t: string) => t.includes('```openui-lang') || /(^|\n)\s*root\s*=/.test(t);

export function PfUserMessage({ message }: { message: UserMessage }) {
  const images = imagesOf(message);
  const text = visibleUserText(message);
  return <div className="openui-agent-thread-message-user pf-msg pf-msg-user">
    <div className="pf-msg-user-stack">
      <div className="openui-agent-thread-message-user__content pf-user-bubble">
        {images.length > 0 && <div className="pf-user-images">{images.map((src, i) => <img key={i} src={src} alt={`Attached ${i + 1}`} className="openui-agent-thread-message-user__image" />)}</div>}
        {text && <div>{text}</div>}
      </div>
      <div className="pf-msg-tools"><CopyButton getText={() => text} label="Copy message" /></div>
    </div>
  </div>;
}

/** Renders the OpenUI Lang answer (as the stock GenUI message does) and adds a copy action under it. */
export function PfAssistantMessage({ message, isStreaming }: { message: AssistantMessage; isStreaming: boolean }) {
  const body = useRef<HTMLDivElement>(null);
  const process = useThread(s => s.processMessage);
  const raw = textOf(message);
  const parsed = raw ? parseMessage(raw, { streaming: isStreaming }) : null;
  const onAction = (event: ActionEvent) => {
    if (event.type === BuiltinActionType.ContinueConversation) {
      const ctx: unknown[] = [`User clicked: ${event.humanFriendlyMessage}`];
      const extra = event.params?.['context'];
      if (event.formState || extra !== undefined) ctx.push(event.formState ?? {});
      if (extra !== undefined) ctx.push(extra);
      const built = buildMessage({ content: event.humanFriendlyMessage, context: ctx });
      void process({ role: 'user', content: event.humanFriendlyMessage ? built : built.slice(built.indexOf('\n') + 1) });
    } else if (event.type === BuiltinActionType.OpenUrl) {
      const url = event.params?.['url'];
      if (typeof url === 'string') window.open(url, '_blank', 'noopener,noreferrer');
    }
  };
  const content = parsed?.content ?? '';
  useEffect(() => {      // code blocks get their own copy control
    if (isStreaming) return;
    body.current?.querySelectorAll('pre').forEach(pre => {
      if (pre.dataset['pfCopy']) return;
      pre.dataset['pfCopy'] = '1'; pre.style.position = 'relative';
      const b = document.createElement('button');
      b.type = 'button'; b.className = 'pf-code-copy'; b.textContent = 'Copy'; b.setAttribute('aria-label', 'Copy code');
      b.onclick = () => { void copyText(pre.innerText.replace(/Copy(ed)?$/, '').trim()).then(ok => { b.textContent = ok ? 'Copied' : 'Failed'; window.setTimeout(() => { b.textContent = 'Copy'; }, 1600); }); };
      pre.appendChild(b);
    });
  }, [isStreaming, content]);
  if (!content) return null;
  return <div className="openui-agent-thread-message-assistant pf-msg pf-msg-assistant">
    <div className="openui-agent-thread-message-assistant__content">
      <div ref={body} className="pf-msg-body">{hasLang(content)
          ? <Renderer response={content} library={payfoundLibrary} isStreaming={isStreaming} onAction={onAction} />
          : <MarkDownRenderer textMarkdown={content} className="openui-agent-thread-message-assistant__text" />}</div>
      {!isStreaming && <div className="pf-msg-tools"><CopyButton getText={() => (body.current?.innerText || content).trim()} label="Copy answer" /></div>}
    </div>
  </div>;
}

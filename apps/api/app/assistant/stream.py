"""POST /api/assistant/stream: OpenAI Agents SDK run, translated to AG-UI server-sent events."""
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import re
import time
import uuid
from typing import Any, AsyncIterator

from agents import Agent, ModelSettings, RunConfig, Runner
from agents.exceptions import AgentsException, MaxTurnsExceeded
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from ..access import accessible_merchant_ids
from ..auth import Principal, current_principal
from .. import placement
from ..database import SessionLocal
from ..intelligence import channel3
from ..intelligence.models import AgentRun
from . import guard, history as chat_history, paypal_mcp, rls, transcribe
from .prompts import build_instructions
from .tools import Ctx, Location, build_tools

log = logging.getLogger('payfound.assistant')
router = APIRouter()
router.include_router(chat_history.router)
router.include_router(transcribe.router)

MAX_TURNS = 8
RUN_TIMEOUT = float(os.getenv('ASSISTANT_RUN_TIMEOUT_SECONDS', '90'))
RESULT_CAP = 8000


class Msg(BaseModel):
    model_config = ConfigDict(extra='allow')
    id: str | None = Field(default=None, max_length=200)
    role: str = Field(max_length=32)
    content: Any = None
    images: list[dict[str, Any]] | None = Field(default=None, max_length=chat_history.MAX_IMAGES)


class StreamInput(BaseModel):
    model_config = ConfigDict(extra='allow')
    threadId: str | None = Field(default=None, max_length=200)
    runId: str | None = Field(default=None, max_length=200)
    messages: list[Msg] = Field(default_factory=list, max_length=400)
    forwardedProps: dict[str, Any] | None = None


def sse(event: dict) -> str:
    return 'data: ' + json.dumps(event, ensure_ascii=False, separators=(',', ':'), default=str) + '\n\n'


def get_model():
    """The configured OpenAI model, or None when no key/model is configured. Tests monkeypatch this."""
    key, name = os.getenv('OPENAI_API_KEY', '').strip(), os.getenv('OPENAI_MODEL', '').strip()
    if not key or not name:
        return None
    from openai import AsyncOpenAI
    from agents import OpenAIResponsesModel
    return OpenAIResponsesModel(model=name, openai_client=AsyncOpenAI(api_key=key, timeout=60, max_retries=1))


def history(body: StreamInput) -> list[dict]:
    turns = []
    for m in body.messages:
        text = m.content
        if isinstance(text, list):
            text = ' '.join(str(x.get('text', '')) for x in text if isinstance(x, dict))
        text = guard.sanitize(text.strip(), 4000) if isinstance(text, str) else ''
        if m.role == 'user':
            images = chat_history.validate_images(m.images)
            if images:
                parts: list[dict] = [{'type': 'input_text', 'text': text or 'What is in this image?'}]
                parts += [{'type': 'input_image', 'image_url': u, 'detail': 'auto'} for u in images]
                turns.append({'role': 'user', 'content': parts})
                continue
        if m.role in ('user', 'assistant') and text:
            turns.append({'role': m.role, 'content': text})
    turns = turns[-20:]
    # Only the two most recent image-bearing turns keep their pixels; older ones become text.
    seen = 0
    for t in reversed(turns):
        if isinstance(t['content'], list):
            seen += 1
            if seen > 2:
                t['content'] = t['content'][0]['text']
    if not turns or turns[-1]['role'] != 'user':
        raise HTTPException(422, 'A user message is required')
    return turns


def last_user_item(body: StreamInput) -> dict | None:
    for m in reversed(body.messages):
        if m.role == 'user':
            text = m.content
            if isinstance(text, list):
                text = ' '.join(str(x.get('text', '')) for x in text if isinstance(x, dict))
            return chat_history.user_item(m.id, text if isinstance(text, str) else '', chat_history.validate_images(m.images))
    return None


def parse_props(raw: dict | None) -> dict:
    raw = raw or {}
    out: dict = {'surface': raw.get('surface') if raw.get('surface') in ('shopper', 'merchant') else None, 'merchant_id': None, 'location': None, 'timezone': None, 'basket': []}
    if isinstance(raw.get('merchant_id'), str) and re.fullmatch(r'[a-zA-Z0-9_-]{1,48}', raw['merchant_id']):
        out['merchant_id'] = raw['merchant_id']
    try:
        out['location'] = Location.model_validate(raw['location']) if raw.get('location') else None
    except ValidationError:
        pass
    if isinstance(raw.get('timezone'), str) and re.fullmatch(r'[A-Za-z0-9_/+-]{1,64}', raw['timezone']):
        out['timezone'] = raw['timezone']
    if isinstance(raw.get('basket'), list):
        for item in raw['basket'][:20]:
            if isinstance(item, dict) and re.fullmatch(r'[a-zA-Z0-9_-]{1,48}', str(item.get('product_id', ''))):
                q = item.get('quantity', 1)
                out['basket'].append({'product_id': item['product_id'], 'quantity': q if isinstance(q, int) and 1 <= q <= 20 else 1})
    return out


def friendly(exc: BaseException) -> str:
    name = type(exc).__name__
    if isinstance(exc, MaxTurnsExceeded):
        return 'That took too many steps. Try a more specific question.'
    if name in ('AuthenticationError', 'PermissionDeniedError'):
        return 'The AI service is not configured correctly. Please contact support.'
    if name == 'RateLimitError':
        return 'The AI service is busy right now. Please try again in a moment.'
    if isinstance(exc, (asyncio.TimeoutError, TimeoutError)) or name in ('APITimeoutError', 'APIConnectionError'):
        return 'The assistant took too long to respond. Please try again.'
    return 'The assistant could not complete this request. Please try again.'


def persist(p: Principal, merchant_id: str | None, used: list[str], status: str, started: float, usage) -> None:
    try:
        with SessionLocal() as db:
            db.add(AgentRun(merchant_id=merchant_id, principal_key=hashlib.sha256(p.subject.encode()).hexdigest(), role=p.role,
                            mode='llm-agents-sdk', status=status, tools=used, product_count=0,
                            latency_ms=max(0, int((time.monotonic() - started) * 1000)),
                            input_tokens=int(getattr(usage, 'input_tokens', 0) or 0), output_tokens=int(getattr(usage, 'output_tokens', 0) or 0),
                            estimated_cost_usd=0, reserved_cost_usd=0, usage_estimated=True))
            db.commit()
    except Exception:
        log.warning('could not record assistant run')


def result_text(output: Any) -> str:
    text = output if isinstance(output, str) else json.dumps(output, ensure_ascii=False, default=str, separators=(',', ':'))
    return text if len(text) <= RESULT_CAP else json.dumps({'truncated': True, 'preview': text[:RESULT_CAP - 60]})


async def run_events(p: Principal, thread: str, run: str, turns: list[dict], props: dict, save: bool = False, view=None) -> AsyncIterator[str]:
    # Request-scoped store placement does not follow a streamed body; re-apply it so tools see the same stores as the REST API.
    tokens = placement.set_request(*view) if view else None
    try:
        async for chunk in _run_events(p, thread, run, turns, props, save):
            yield chunk
    finally:
        if tokens:
            placement.reset_request(tokens)


async def _run_events(p: Principal, thread: str, run: str, turns: list[dict], props: dict, save: bool = False) -> AsyncIterator[str]:
    started = time.monotonic()
    yield sse({'type': 'RUN_STARTED', 'threadId': thread, 'runId': run})
    model = get_model()
    if model is None:
        yield sse({'type': 'RUN_ERROR', 'message': 'The assistant is not configured yet (no AI model key).', 'code': 'not_configured'})
        return
    used: list[str] = []
    status, usage = 'ok', None
    segments: list[str | None] = []
    tool_log: list[dict] = []
    with SessionLocal() as db:
        try:
            ctx = Ctx(db=db, principal=p, location=props['location'], merchant_id=props['merchant_id'], basket=props['basket'])
            if rls.enabled(db):
                ctx.rls = True
            merchant_ok = ctx.is_admin or bool(accessible_merchant_ids(db, p))
            kind = 'admin' if ctx.is_admin else 'merchant' if merchant_ok else 'consumer'
            mcp_servers = []
            if ctx.is_admin:
                server = await paypal_mcp.manager.get()
                if server is not None:
                    mcp_servers.append(server)
            agent = Agent(
                name='PayFound Assistant', model=model, tools=build_tools(ctx), mcp_servers=mcp_servers,
                instructions=build_instructions(role_kind=kind, merchant_id=props['merchant_id'], location_shared=ctx.location is not None,
                                                timezone_name=props['timezone'], basket=props['basket'], merchant_ok=merchant_ok),
                model_settings=ModelSettings(store=False, parallel_tool_calls=True, include_usage=True))
            result = Runner.run_streamed(agent, turns, context=ctx, max_turns=MAX_TURNS,
                                         run_config=RunConfig(tracing_disabled=True, trace_include_sensitive_data=False))
            parent, text_id, wrote = f'msg_{uuid.uuid4().hex[:12]}', None, False
            out_guard = guard.OutputGuard()
            async with asyncio.timeout(RUN_TIMEOUT):
                async for ev in result.stream_events():
                    if ev.type == 'raw_response_event':
                        d = ev.data
                        if getattr(d, 'type', '') == 'response.output_text.delta' and d.delta:
                            safe = out_guard.feed(d.delta)
                            if safe:
                                if text_id is None:
                                    text_id = f'msg_{uuid.uuid4().hex[:12]}'
                                    yield sse({'type': 'TEXT_MESSAGE_START', 'messageId': text_id, 'role': 'assistant'})
                                wrote = True
                                if len(segments) < 1 or segments[-1] is None:
                                    segments.append('')
                                segments[-1] += safe
                                yield sse({'type': 'TEXT_MESSAGE_CONTENT', 'messageId': text_id, 'delta': safe})
                    elif ev.type == 'run_item_stream_event':
                        raw = ev.item.raw_item
                        get = (lambda k: raw.get(k)) if isinstance(raw, dict) else (lambda k: getattr(raw, k, None))
                        if ev.name == 'tool_called' and get('call_id'):
                            tail = out_guard.flush()
                            if tail:
                                if text_id is None:
                                    text_id = f'msg_{uuid.uuid4().hex[:12]}'
                                    yield sse({'type': 'TEXT_MESSAGE_START', 'messageId': text_id, 'role': 'assistant'})
                                wrote = True
                                if not segments or segments[-1] is None:
                                    segments.append('')
                                segments[-1] += tail
                                yield sse({'type': 'TEXT_MESSAGE_CONTENT', 'messageId': text_id, 'delta': tail})
                            if text_id:
                                yield sse({'type': 'TEXT_MESSAGE_END', 'messageId': text_id})
                                text_id = None
                                segments.append(None)
                            cid = get('call_id')
                            tool_log.append({'id': str(cid)[:80], 'name': str(get('name') or 'tool')[:80]})
                            yield sse({'type': 'TOOL_CALL_START', 'toolCallId': cid, 'toolCallName': get('name') or 'tool', 'parentMessageId': parent})
                            yield sse({'type': 'TOOL_CALL_ARGS', 'toolCallId': cid, 'delta': get('arguments') or '{}'})
                            yield sse({'type': 'TOOL_CALL_END', 'toolCallId': cid})
                        elif ev.name == 'tool_output' and get('call_id'):
                            yield sse({'type': 'TOOL_CALL_RESULT', 'messageId': f'msg_{uuid.uuid4().hex[:12]}', 'toolCallId': get('call_id'),
                                       'content': result_text(ev.item.output), 'role': 'tool'})
            tail = out_guard.flush()
            if tail:
                if text_id is None:
                    text_id = f'msg_{uuid.uuid4().hex[:12]}'
                    yield sse({'type': 'TEXT_MESSAGE_START', 'messageId': text_id, 'role': 'assistant'})
                wrote = True
                if not segments or segments[-1] is None:
                    segments.append('')
                segments[-1] += tail
                yield sse({'type': 'TEXT_MESSAGE_CONTENT', 'messageId': text_id, 'delta': tail})
            if out_guard.halted:
                status = 'blocked'
            if out_guard.hits or out_guard.halted:
                guard.audit('redacted', scope='output', tools=sorted(out_guard.hits))
            if text_id:
                yield sse({'type': 'TEXT_MESSAGE_END', 'messageId': text_id})
            usage = result.context_wrapper.usage
            used = ctx.used
            if not wrote:
                status = 'blocked' if out_guard.halted else 'error'
                yield sse({'type': 'RUN_ERROR', 'message': 'I could not share that answer. Please ask in a different way.' if out_guard.halted else 'The assistant did not produce an answer. Please try again.', 'code': 'blocked' if out_guard.halted else 'empty'})
                return
            if save:
                chat_history.append(p.subject, thread, chat_history.assistant_items([x for x in segments if x], tool_log))
            yield sse({'type': 'RUN_FINISHED', 'threadId': thread, 'runId': run})
        except asyncio.CancelledError:
            status = 'cancelled'
            raise
        except BaseException as exc:  # noqa: BLE001 - never leak provider bodies or secrets to the browser
            status = 'error'
            log.warning('assistant run failed: %s', type(exc).__name__)
            yield sse({'type': 'RUN_ERROR', 'message': friendly(exc), 'code': 'agent_failed'})
        finally:
            db.rollback()
    persist(p, props['merchant_id'], used, status, started, usage)


def input_decision(p: Principal, turns: list[dict]) -> guard.Decision:
    """Deterministic input policy on the last user turn, using the server-derived principal kind (never a client hint)."""
    last = turns[-1]['content']
    images = isinstance(last, list)
    text = ' '.join(x.get('text', '') for x in last if isinstance(x, dict) and x.get('type') == 'input_text') if images else last
    with SessionLocal() as db:
        ids = frozenset(accessible_merchant_ids(db, p))
    kind = 'admin' if p.role == 'admin' else 'merchant' if ids else 'consumer'
    return guard.check_input(text, kind=kind, has_history=len(turns) > 1, own_merchant_ids=ids, has_images=images)


def refusal_lang(decision: guard.Decision) -> str:
    """Short refusal as OpenUI Lang so the chat UI renders it; the alternatives are clickable follow-ups."""
    def q(t: str) -> str:
        return json.dumps(t, ensure_ascii=False)
    first = decision.message.split(' Try:')[0]
    items = ''.join(f'f{i} = FollowUpItem({q(s)})\n' for i, s in enumerate(decision.suggestions))
    refs = ', '.join(f'f{i}' for i in range(len(decision.suggestions)))
    return f'root = Card([msg, follow])\nmsg = TextContent({q(first)})\nfollow = FollowUpBlock([{refs}])\n{items}'


async def refusal_events(thread: str, run: str, text: str) -> AsyncIterator[str]:
    mid = f'msg_{uuid.uuid4().hex[:12]}'
    yield sse({'type': 'RUN_STARTED', 'threadId': thread, 'runId': run})
    yield sse({'type': 'TEXT_MESSAGE_START', 'messageId': mid, 'role': 'assistant'})
    yield sse({'type': 'TEXT_MESSAGE_CONTENT', 'messageId': mid, 'delta': text})
    yield sse({'type': 'TEXT_MESSAGE_END', 'messageId': mid})
    yield sse({'type': 'RUN_FINISHED', 'threadId': thread, 'runId': run})


@router.post('/assistant/stream')
async def assistant_stream(body: StreamInput, p: Principal = Depends(current_principal)):
    turns = history(body)
    channel3.rate_limit(p, 'agent')
    props = parse_props(body.forwardedProps)
    thread = body.threadId or f'thread_{uuid.uuid4().hex[:12]}'
    item = last_user_item(body)
    with SessionLocal() as sdb:
        surface = chat_history.resolve_surface(sdb, p, props['surface'])
    saved = bool(item) and chat_history.append(p.subject, thread, [item], title_hint=item['content'] or 'Image', surface=surface)
    decision = input_decision(p, turns)
    guard.audit(decision.category, scope=decision.scope)
    if not decision.allowed:
        run = body.runId or f'run_{uuid.uuid4().hex[:12]}'
        text = refusal_lang(decision)
        if saved:
            chat_history.append(p.subject, thread, chat_history.assistant_items([text], []))
        persist(p, None, [], 'refused', time.monotonic(), None)
        return StreamingResponse(refusal_events(thread, run, text), media_type='text/event-stream',
                                 headers={'Cache-Control': 'no-cache, no-transform', 'X-Accel-Buffering': 'no'})
    anchor, layout = placement.current_anchor(), placement.current_layout()
    if anchor and (layout is None or layout.mode != 'relocated'):  # layout still being computed: wait for it like /demo/placement does, so stores are near the user
        layout = await placement.layout_for(anchor, placement.full_wait_s()) or layout
    stream = run_events(p, thread, body.runId or f'run_{uuid.uuid4().hex[:12]}', turns, props, save=saved, view=(anchor, placement._TZ.get(), layout))
    return StreamingResponse(stream, media_type='text/event-stream', headers={'Cache-Control': 'no-cache, no-transform', 'X-Accel-Buffering': 'no'})

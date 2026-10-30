"""Lazy, shared PayPal MCP connection (sandbox only) with a strict read-only allow-list."""
from __future__ import annotations

import asyncio
import logging
import os
import shutil
import time
from pathlib import Path

from agents.mcp import MCPServerStdio

from ..config import WORKSPACE_ROOT

log = logging.getLogger('payfound.assistant.mcp')

ADMIN_READ_TOOLS = frozenset({'list_transactions', 'list_disputes', 'get_dispute', 'list_invoices', 'get_invoice'})
ORDER_SCOPED_TOOLS = frozenset({'get_order'})  # called only by paypal_order_status after authorization
ALLOW_LIST = ADMIN_READ_TOOLS | ORDER_SCOPED_TOOLS
FORBIDDEN_PREFIXES = ('pay_', 'create_', 'cancel_', 'send_', 'update_', 'accept_')


def launcher() -> Path:
    return WORKSPACE_ROOT / '.opencode' / 'paypal-mcp.mjs'


def available() -> bool:
    return (os.getenv('ASSISTANT_PAYPAL_MCP', 'true').lower() != 'false' and shutil.which('node') is not None
            and launcher().exists() and bool(os.getenv('PAYPAL_CLIENT_ID') or os.getenv('PAYPAL_ACCESS_TOKEN')))


def tool_filter(context, tool) -> bool:
    """Dynamic filter: only allow-listed names, and the account-wide tools only for administrators."""
    name = getattr(tool, 'name', '')
    if name not in ALLOW_LIST or name.startswith(FORBIDDEN_PREFIXES):
        return False
    if name in ORDER_SCOPED_TOOLS:
        return False  # never directly model-callable
    ctx = getattr(context.run_context, 'context', None)
    return bool(getattr(ctx, 'is_admin', False))


class Manager:
    """Owns the stdio process inside one long-lived task so anyio scopes open and close in the same task."""

    def __init__(self):
        self.server: MCPServerStdio | None = None
        self.task: asyncio.Task | None = None
        self.failed_at = -1e9
        self.stop = asyncio.Event()

    async def _own(self, ready: asyncio.Future):
        server = MCPServerStdio(
            {'command': 'node', 'args': [str(launcher())], 'cwd': str(WORKSPACE_ROOT)}, name='paypal',
            cache_tools_list=True, client_session_timeout_seconds=20, tool_filter=tool_filter)
        try:
            await asyncio.wait_for(server.connect(), timeout=45)
        except BaseException:  # missing node/npx/credentials/network: the assistant keeps working without PayPal
            log.warning('PayPal MCP unavailable; continuing without it')
            self.failed_at = time.monotonic()
            if not ready.done():
                ready.set_result(None)
            try:
                await server.cleanup()
            except BaseException:
                pass
            return
        self.server = server
        ready.set_result(server)
        try:
            await self.stop.wait()
        finally:
            self.server = None
            try:
                await server.cleanup()
            except BaseException:
                pass

    async def get(self) -> MCPServerStdio | None:
        if self.server is not None:
            return self.server
        if not available() or time.monotonic() - self.failed_at < 120:
            return None
        if self.task is None or self.task.done():
            self.stop = asyncio.Event()
            ready = asyncio.get_running_loop().create_future()
            self.task = asyncio.create_task(self._own(ready))
            self.ready = ready
        return await asyncio.shield(self.ready)

    async def call(self, name: str, arguments: dict) -> dict:
        """Server-side call of one allow-listed read tool (used by paypal_order_status after authorization)."""
        if name not in ALLOW_LIST:
            raise PermissionError('Tool not allowed')
        server = await self.get()
        if server is None:
            return {'available': False, 'note': 'PayPal sandbox tools are not available right now.'}
        try:
            result = await asyncio.wait_for(server.call_tool(name, arguments), timeout=25)
        except Exception:
            self.stop.set()
            self.failed_at = time.monotonic()
            return {'available': False, 'note': 'PayPal sandbox lookup failed.'}
        text = ' '.join(getattr(part, 'text', '') for part in (result.content or []))
        return {'available': True, 'source': 'PayPal sandbox', 'result': text[:4000]}


manager = Manager()

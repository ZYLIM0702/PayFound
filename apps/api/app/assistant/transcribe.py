"""POST /api/assistant/transcribe: short dictation audio -> text with OpenAI gpt-4o-transcribe. Audio is never stored or logged."""
from __future__ import annotations

import logging
import os

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from ..auth import Principal, current_principal
from ..intelligence import channel3

log = logging.getLogger('payfound.assistant')
router = APIRouter()

MAX_AUDIO_BYTES = 10 * 1024 * 1024
ALLOWED = {
    'audio/webm': 'webm', 'video/webm': 'webm', 'audio/mp4': 'mp4', 'video/mp4': 'mp4', 'audio/x-m4a': 'm4a', 'audio/m4a': 'm4a',
    'audio/wav': 'wav', 'audio/x-wav': 'wav', 'audio/wave': 'wav', 'audio/mpeg': 'mp3', 'audio/mp3': 'mp3', 'audio/ogg': 'ogg',
    'application/ogg': 'ogg',
}


def sniff(raw: bytes) -> str | None:
    if raw[:4] == b'\x1aE\xdf\xa3':
        return 'webm'
    if raw[4:8] == b'ftyp':
        return 'mp4'
    if raw[:4] == b'RIFF' and raw[8:12] == b'WAVE':
        return 'wav'
    if raw[:4] == b'OggS':
        return 'ogg'
    if raw[:3] == b'ID3' or (len(raw) > 1 and raw[0] == 0xFF and raw[1] & 0xE0 == 0xE0):
        return 'mp3'
    return None


async def transcribe_audio(filename: str, data: bytes, mime: str) -> str:
    """Call OpenAI. Tests monkeypatch this."""
    key = os.getenv('OPENAI_API_KEY', '').strip()
    if not key:
        raise HTTPException(503, 'Voice input is not configured yet')
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=key, timeout=45, max_retries=1)
    out = await client.audio.transcriptions.create(model=os.getenv('OPENAI_TRANSCRIBE_MODEL', 'gpt-4o-transcribe'), file=(filename, data, mime))
    return (getattr(out, 'text', '') or '').strip()


@router.post('/assistant/transcribe')
async def transcribe(file: UploadFile = File(...), p: Principal = Depends(current_principal)):
    channel3.rate_limit(p, 'agent')
    mime = (file.content_type or '').split(';')[0].strip().lower()
    kind = ALLOWED.get(mime)
    if kind is None:
        raise HTTPException(415, 'Unsupported audio type. Use webm, mp4, wav, mp3, ogg or m4a.')
    chunks, size = [], 0
    while True:
        chunk = await file.read(1024 * 1024)
        if not chunk:
            break
        size += len(chunk)
        if size > MAX_AUDIO_BYTES:
            raise HTTPException(413, 'Audio must be 10 MB or smaller')
        chunks.append(chunk)
    data = b''.join(chunks)
    if size < 200:
        raise HTTPException(422, 'That recording was empty')
    detected = sniff(data)
    if detected is None or (detected != kind and not {detected, kind} <= {'mp4', 'm4a'}):
        raise HTTPException(415, 'The audio content does not match its type')
    try:
        text = await transcribe_audio(f'dictation.{kind}', data, mime)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001 - never leak provider bodies
        log.warning('transcription failed: %s', type(exc).__name__)
        raise HTTPException(502, 'Could not transcribe that recording. Please try again.') from None
    return {'text': text[:4000]}

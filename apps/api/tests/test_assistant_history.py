import base64
import json

import pytest
from agents.testing import ScriptedModel, assistant_message

from app import llm
from app.assistant import stream as stream_module, transcribe as transcribe_module

PNG = base64.b64encode(b'\x89PNG\r\n\x1a\n' + b'\x00' * 64).decode()
PNG_URL = 'data:image/png;base64,' + PNG


@pytest.fixture(autouse=True)
def fresh_budget():
    llm.budget._windows.clear()
    yield
    llm.budget._windows.clear()


TID = 'thread-abc12345'


def script(monkeypatch, text='root = Card([h])\nh = CardHeader("Hi")\n'):
    model = ScriptedModel([[assistant_message(text)]])
    monkeypatch.setattr(stream_module, 'get_model', lambda: model)
    return model


def post(client, headers, text='hello there', thread=TID, images=None, mid='m-1'):
    msg = {'id': mid, 'role': 'user', 'content': text}
    if images is not None:
        msg['images'] = images
    return client.post('/api/assistant/stream', headers=headers, json={'threadId': thread, 'runId': 'r1', 'messages': [msg]})


def test_thread_is_persisted_and_owner_only(client, consumer, merchant, monkeypatch):
    script(monkeypatch)
    r = post(client, consumer)
    assert 'RUN_FINISHED' in r.text
    lst = client.get('/api/assistant/threads', headers=consumer).json()['threads']
    assert [t['id'] for t in lst] == [TID] and lst[0]['title'] == 'hello there'
    t = client.get(f'/api/assistant/threads/{TID}', headers=consumer).json()
    assert [m['role'] for m in t['messages']] == ['user', 'assistant']
    assert t['messages'][1]['content'].startswith('root = Card')
    # another subject cannot list, read, rename, delete, or write into it
    assert client.get('/api/assistant/threads', headers=merchant).json()['threads'] == []
    assert client.get(f'/api/assistant/threads/{TID}', headers=merchant).status_code == 404
    assert client.patch(f'/api/assistant/threads/{TID}', headers=merchant, json={'title': 'x'}).status_code == 404
    assert client.delete(f'/api/assistant/threads/{TID}', headers=merchant).status_code == 404
    script(monkeypatch)
    post(client, merchant, text='intruder', mid='m-9')
    assert len(client.get(f'/api/assistant/threads/{TID}', headers=consumer).json()['messages']) == 2
    assert client.get('/api/assistant/threads', headers={'x-demo-role': 'bogus'}).status_code == 401


def test_rename_and_delete(client, consumer, monkeypatch):
    script(monkeypatch)
    post(client, consumer)
    assert client.patch(f'/api/assistant/threads/{TID}', headers=consumer, json={'title': 'Chargers'}).json()['title'] == 'Chargers'
    assert client.delete(f'/api/assistant/threads/{TID}', headers=consumer).status_code == 204
    assert client.get(f'/api/assistant/threads/{TID}', headers=consumer).status_code == 404
    assert client.get('/api/assistant/threads/bad id', headers=consumer).status_code in (404, 422)


def test_create_thread_endpoint(client, consumer, merchant):
    r = client.post('/api/assistant/threads', headers=consumer, json={'id': 'created-thread1', 'title': 'Plan'})
    assert r.status_code == 201 and r.json()['title'] == 'Plan'
    assert client.post('/api/assistant/threads', headers=merchant, json={'id': 'created-thread1'}).status_code == 404


def test_image_reaches_model_and_is_stored(client, consumer, monkeypatch):
    model = script(monkeypatch)
    r = post(client, consumer, text='what is this', images=[{'data_url': PNG_URL}])
    assert 'RUN_FINISHED' in r.text
    t = client.get(f'/api/assistant/threads/{TID}', headers=consumer).json()
    assert t['messages'][0]['images'][0]['data_url'] == PNG_URL


def test_image_validation(client, consumer, monkeypatch):
    script(monkeypatch)
    bad = [
        'data:image/svg+xml;base64,' + PNG,
        'data:image/png;base64,!!!not-base64',
        'data:image/jpeg;base64,' + PNG,
        'https://example.com/a.png',
    ]
    for u in bad:
        assert post(client, consumer, images=[{'data_url': u}], mid='x' + str(len(u))).status_code == 422, u
    assert post(client, consumer, images=[{'data_url': PNG_URL}] * 4).status_code == 422
    big = 'data:image/png;base64,' + base64.b64encode(b'\x89PNG\r\n\x1a\n' + b'\0' * (4 * 1024 * 1024 + 10)).decode()
    assert post(client, consumer, images=[{'data_url': big}]).status_code == 422


def test_large_accepted_image_is_kept(client, consumer, monkeypatch):
    script(monkeypatch)
    big = 'data:image/png;base64,' + base64.b64encode(b'\x89PNG\r\n\x1a\n' + b'\0' * 800_000).decode()
    post(client, consumer, images=[{'data_url': big}])
    img = client.get(f'/api/assistant/threads/{TID}', headers=consumer).json()['messages'][0]['images'][0]
    assert img['data_url'] == big and 'placeholder' not in img


WAV = b'RIFF' + b'\x24\x10\x00\x00' + b'WAVEfmt ' + b'\x00' * 400


def test_transcribe_validation_and_success(client, consumer, monkeypatch):
    async def fake(name, data, mime):
        return 'find a usb c charger'
    monkeypatch.setattr(transcribe_module, 'transcribe_audio', fake)
    url = '/api/assistant/transcribe'
    ok = client.post(url, headers=consumer, files={'file': ('a.wav', WAV, 'audio/wav')})
    assert ok.status_code == 200 and ok.json() == {'text': 'find a usb c charger'}
    assert client.post(url, headers=consumer, files={'file': ('a.txt', b'hello' * 100, 'text/plain')}).status_code == 415
    assert client.post(url, headers=consumer, files={'file': ('a.wav', b'not audio at all' * 40, 'audio/wav')}).status_code == 415
    assert client.post(url, headers=consumer, files={'file': ('a.wav', b'RIFF', 'audio/wav')}).status_code == 422
    big = WAV + b'\0' * (10 * 1024 * 1024)
    assert client.post(url, headers=consumer, files={'file': ('a.wav', big, 'audio/wav')}).status_code == 413
    assert client.post(url, files={'file': ('a.wav', WAV, 'audio/wav')}, headers={'x-demo-role': 'bogus'}).status_code == 401

"""Start API, web and durable worker together; stop all children on Ctrl-C."""
import argparse
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import socket
import fcntl
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]


def assert_ports_free():
    for port in (8000, 5173):
        try:
            with socket.create_connection(('127.0.0.1', port), timeout=0.3):
                raise SystemExit(f'Port {port} is already in use. Stop the intended existing stack before starting another one.')
        except (ConnectionRefusedError, TimeoutError, OSError):
            pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--demo', action='store_true', help='Use isolated local synthetic inventory and role switcher')
    parser.add_argument('--background', action='store_true', help='Save logs/PID under docs/evidence')
    parser.add_argument('--stop', action='store_true', help='Stop the stack started by this project')
    args = parser.parse_args()
    pidfile = ROOT / 'docs/evidence/dev-stack.pid'
    if args.stop:
        if pidfile.exists():
            pid = int(pidfile.read_text())
            command = subprocess.run(['ps', '-p', str(pid), '-o', 'command='], capture_output=True, text=True).stdout
            if 'scripts/dev.py' in command:
                os.kill(pid, signal.SIGTERM)
                print('Stopping PayFound development stack.')
            else:
                print('Saved stack process is no longer running.')
        return
    if args.background:
        assert_ports_free()
        command = [sys.executable, str(Path(__file__).resolve())] + (['--demo'] if args.demo else [])
        with (ROOT / 'docs/evidence/dev-stack.log').open('a') as output:
            child = subprocess.Popen(command, cwd=ROOT, stdout=output, stderr=subprocess.STDOUT, start_new_session=True)
        time.sleep(1)
        if child.poll() is not None:
            raise SystemExit('Stack startup failed; inspect docs/evidence/dev-stack.log')
        print('Started PayFound local stack; logs: docs/evidence/dev-stack.log')
        return
    lockfile = (ROOT / 'docs/evidence/dev-stack.lock').open('a')
    try:
        fcntl.flock(lockfile.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        raise SystemExit('This PayFound stack is already managed by another launcher.')
    assert_ports_free()
    pidfile.write_text(str(os.getpid()))
    python = ROOT / 'apps/api/.venv/bin/python'
    if not python.exists():
        raise SystemExit('Create apps/api/.venv and install requirements first.')
    env = dict(os.environ)
    if args.demo:
        env.update(DEMO_MODE='true', DATABASE_URL='sqlite:///./payfound_demo.db')
    else:
        env['DEMO_MODE'] = 'false'
    children = []
    stopping = False

    def stop(*_):
        nonlocal stopping
        if stopping:
            return
        stopping = True
        for process in reversed(children):
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
        for process in children:
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    try:
        children.append(subprocess.Popen([str(python), '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000', '--no-access-log'], cwd=ROOT / 'apps/api', env=env, start_new_session=True))
        for _ in range(60):
            if stopping or children[0].poll() is not None:
                raise RuntimeError('API process exited before becoming ready')
            try:
                with urlopen('http://127.0.0.1:8000/api/health', timeout=1) as response:
                    if response.status == 200:
                        break
            except OSError:
                if stopping or children[0].poll() is not None:
                    return
                time.sleep(0.5)
        else:
            raise RuntimeError('API startup timed out')
        children.append(subprocess.Popen([str(python), '-m', 'app.worker'], cwd=ROOT / 'apps/api', env=env, start_new_session=True))
        children.append(subprocess.Popen(['npm', 'run', 'dev'], cwd=ROOT / 'apps/web', env=env, start_new_session=True))
        print('PayFound: http://127.0.0.1:5173 · API docs: http://127.0.0.1:8000/docs', flush=True)
        while not stopping:
            if not stopping and any(process.poll() is not None for process in children):
                raise RuntimeError('A development service exited; stopping the stack')
            time.sleep(1)
    finally:
        stop()
        if pidfile.exists() and pidfile.read_text() == str(os.getpid()):
            pidfile.unlink()
        lockfile.close()


if __name__ == '__main__':
    main()

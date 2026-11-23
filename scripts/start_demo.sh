#!/usr/bin/env bash
# Existing applications, separate processes and stores; no data activation.
set -euo pipefail
DEMO_REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$DEMO_REPO_ROOT"
if [[ ! -x "$DEMO_REPO_ROOT/.venv/bin/python" ]]; then
  echo "Demo startup failed: missing repository .venv/bin/python. Restore the existing environment first." >&2
  exit 1
fi
export PYTHONDONTWRITEBYTECODE=1
exec "$DEMO_REPO_ROOT/.venv/bin/python" - "$@" <<'PYTHON'
import argparse
import math
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import tempfile
import time
from urllib.error import URLError
from urllib.request import ProxyHandler, build_opener

parser = argparse.ArgumentParser(description='Run the three existing local Banc-Inc360 apps; Ctrl+C stops only owned processes.')
parser.add_argument('--open-browser', action='store_true', help='Open the main URL on macOS after health checks pass.')
parser.add_argument('--timeout', type=float, default=60, help='Total startup health timeout in seconds (default: 60).')
args = parser.parse_args()
children = []
logs = []


def interrupted(signum, frame):
    raise SystemExit(130 if signum == signal.SIGINT else 143)


signal.signal(signal.SIGINT, interrupted)
signal.signal(signal.SIGTERM, interrupted)
signal.signal(signal.SIGHUP, interrupted)


def cleanup():
    # Each Popen starts a new session: these process groups belong to us alone.
    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
        signal.signal(sig, signal.SIG_IGN)
    for name, child in children:
        try:
            os.killpg(child.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    deadline = time.monotonic() + 5
    for name, child in children:
        try:
            child.wait(timeout=max(0.01, deadline - time.monotonic()))
        except subprocess.TimeoutExpired:
            pass
    for name, child in children:
        try:
            os.killpg(child.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        child.wait()
    for log in logs:
        log.close()
    if children:
        print('Stopped launcher-owned services.', flush=True)


try:
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        raise ValueError('--timeout must be a finite positive number.')
    if os.environ.get('BANCINC_RUNTIME', 'LOCAL').upper() != 'LOCAL':
        raise ValueError('The demo companions require BANCINC_RUNTIME=LOCAL; inherited configuration was not changed.')
    main_port = int(os.environ.get('BANCINC_DEMO_MAIN_PORT', os.environ.get('STREAMLIT_SERVER_PORT', '8514')))
    specs = [('MAIN', 'app.py', main_port),
             ('INGESTION', 'phase9_app.py', 8511),
             ('BUSINESS', 'phase10b_app.py', 8515)]
    ports = [port for _, _, port in specs]
    if len(set(ports)) != 3 or any(not 1 <= port <= 65535 for port in ports):
        raise ValueError('Three distinct valid ports are required; companions use 8511 and 8515.')
    for name, entry, port in specs:
        if not Path(entry).is_file():
            raise ValueError('Missing existing entrypoint: ' + entry)
    # Hold all probe sockets until the complete preflight succeeds. Never kill a listener.
    probes = []
    try:
        for name, entry, port in specs:
            probe = socket.socket()
            probes.append(probe)
            # Match Streamlit: permit recently closed sockets, never a live listener.
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                probe.bind(('127.0.0.1', port))
            except OSError as exc:
                raise ValueError(f'{name} port {port} is unavailable: {exc}. Stop its owner or resolve the configuration; nothing was launched.') from exc
    finally:
        for probe in probes:
            probe.close()
    run_root = Path(tempfile.mkdtemp(prefix='bancinc-demo-')).resolve()
    env = os.environ.copy()
    env.setdefault('BANCINC_AUDIT_DB', str(run_root / 'original-review.sqlite3'))
    env.setdefault('BANCINC_PHASE9_STORAGE', str(run_root / 'ingestion'))
    env.setdefault('BANCINC_INGESTION_URL', 'http://127.0.0.1:8511')
    env.setdefault('BANCINC_BUSINESS_URL', 'http://127.0.0.1:8515')
    print('Private run logs/default disposable state: ' + str(run_root), flush=True)
    for name, entry, port in specs:
        command = [sys.executable, '-m', 'streamlit', 'run', entry,
                   '--server.address', '127.0.0.1', '--server.port', str(port),
                   '--server.headless', 'true', '--browser.gatherUsageStats', 'false']
        if entry == 'phase9_app.py':
            command += ['--server.maxUploadSize', '5']
        log = (run_root / (name.lower() + '.log')).open('wb')
        logs.append(log)
        # Block termination briefly so a child cannot be spawned without being registered.
        mask = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGINT, signal.SIGTERM, signal.SIGHUP})
        try:
            child = subprocess.Popen(command, env=env, stdout=log, stderr=subprocess.STDOUT,
                                     start_new_session=True, preexec_fn=lambda: signal.pthread_sigmask(signal.SIG_SETMASK, mask))
            children.append((name, child))
        finally:
            signal.pthread_sigmask(signal.SIG_SETMASK, mask)
    pending = {port for _, _, port in specs}
    deadline = time.monotonic() + args.timeout
    opener = build_opener(ProxyHandler({}))  # Loopback health must not use a proxy.
    while pending:
        for name, child in children:
            if child.poll() is not None:
                raise RuntimeError(f'{name} exited with {child.returncode}; inspect {run_root / (name.lower() + ".log")}')
        if time.monotonic() >= deadline:
            raise RuntimeError(f'Health timeout after {args.timeout:g}s for ports {sorted(pending)}; inspect logs in {run_root}')
        for port in list(pending):
            try:
                remaining = max(0.01, deadline - time.monotonic())
                with opener.open(f'http://127.0.0.1:{port}/_stcore/health', timeout=min(0.5, remaining)) as response:
                    if response.status == 200 and response.read(32).strip() == b'ok':
                        pending.remove(port)
            except (URLError, TimeoutError, OSError):
                pass
        time.sleep(0.1)
    for name, entry, port in specs:
        print(f'{name}: http://127.0.0.1:{port}', flush=True)
    print('Health checks passed (not a full UI validation). Ctrl+C stops all three owned services.', flush=True)
    if args.open_browser:
        if sys.platform == 'darwin':
            subprocess.run(['open', f'http://127.0.0.1:{main_port}'], check=True)
        else:
            print('--open-browser is macOS-only; open the MAIN URL manually.', flush=True)
    while True:
        for name, child in children:
            if child.poll() is not None:
                raise RuntimeError(f'{name} stopped with {child.returncode}; inspect {run_root / (name.lower() + ".log")}')
        time.sleep(0.25)
except (ValueError, OSError, RuntimeError, subprocess.SubprocessError) as exc:
    print('Demo startup/runtime failed: ' + str(exc), file=sys.stderr, flush=True)
    sys.exit(1)
finally:
    cleanup()
PYTHON

"""Focused launcher/sidebar checks; no fitting or canonical/store writes."""
import os
from pathlib import Path
import socket
import subprocess

import pytest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / 'scripts/start_demo.sh'


@pytest.mark.parametrize('ingestion,business,expected', [
    (None, None, ['http://127.0.0.1:8511', 'http://127.0.0.1:8515']),
    ('https://example.org/ingestion', 'https://example.org/business',
     ['https://example.org/ingestion', 'https://example.org/business']),
    ('javascript:alert(1)', 'http://127.0.0.1:8515', ['http://127.0.0.1:8515']),
])
def test_sidebar_external_links(monkeypatch, tmp_path, ingestion, business, expected):
    monkeypatch.setenv('DATA_MODE', 'DEMO')
    monkeypatch.setenv('BANCINC_RUNTIME', 'LOCAL')
    monkeypatch.setenv('BANCINC_AUDIT_DB', str(tmp_path / 'unused-review.sqlite3'))
    for variable, value in [('BANCINC_INGESTION_URL', ingestion), ('BANCINC_BUSINESS_URL', business)]:
        if value is None:
            monkeypatch.delenv(variable, raising=False)
        else:
            monkeypatch.setenv(variable, value)
    app = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=120).run()
    assert not app.exception
    links = list(app.get('page_link'))
    assert [link.proto.page for link in links] == expected
    assert all(link.proto.external for link in links)
    assert any(c.value == 'ADDITIONAL CAPABILITIES' for c in app.sidebar.caption)
    assert any('set BANCINC_INGESTION_URL' in w.value for w in app.warning) == (len(expected) == 1)
    assert not any(code.value in ('8511', '8515') for code in app.code)
    assert not (tmp_path / 'unused-review.sqlite3').exists()


@pytest.mark.parametrize('timeout', ['0', '-1', 'nan', 'inf'])
def test_invalid_health_deadline_fails_before_launch(timeout):
    result = subprocess.run(['bash', str(LAUNCHER), '--timeout', timeout], cwd='/private/tmp',
                            capture_output=True, text=True, timeout=10)
    assert result.returncode == 1
    assert 'finite positive' in result.stderr
    assert 'Private run logs' not in result.stdout


def test_port_conflict_preserves_existing_listener():
    with socket.socket() as listener:
        listener.bind(('127.0.0.1', 0))
        listener.listen()
        port = listener.getsockname()[1]
        env = os.environ.copy()
        env['BANCINC_DEMO_MAIN_PORT'] = str(port)
        result = subprocess.run(['bash', str(LAUNCHER)], env=env, cwd='/private/tmp',
                                capture_output=True, text=True, timeout=10)
        assert result.returncode == 1
        assert f'port {port} is unavailable' in result.stderr
        assert 'nothing was launched' in result.stderr
        assert 'Private run logs' not in result.stdout
        with socket.create_connection(('127.0.0.1', port), timeout=1):
            pass  # The listener belongs to this test and must still be alive.


def test_launcher_shell_syntax():
    subprocess.run(['bash', '-n', str(LAUNCHER)], check=True)


def test_launcher_resolves_generated_storage_before_child_configuration():
    # macOS /var is a symlink: the accepted Phase 9 store rejects unresolved roots.
    source = LAUNCHER.read_text().split("<<'PYTHON'\n", 1)[1].rsplit('\nPYTHON', 1)[0]
    import ast
    tree = ast.parse(source)
    assignment = next(n for n in ast.walk(tree) if isinstance(n, ast.Assign)
                      and any(isinstance(t, ast.Name) and t.id == 'run_root' for t in n.targets))
    import tempfile
    physical = Path(tempfile.gettempdir()).resolve() / 'bancinc-test-only'
    class Temporary:
        @staticmethod
        def mkdtemp(**kwargs):
            return str(Path(tempfile.gettempdir()) / 'bancinc-test-only')
    expression = ast.Expression(assignment.value)
    actual = eval(compile(expression, '<launcher-generated-storage>', 'eval'), {'Path': Path, 'tempfile': Temporary})
    assert actual == physical and actual.resolve() == actual

"""Endpoint lifecycle: start, confirm readiness, stop.

`serve_cmd` is the documented way to run an endpoint without a systemd unit,
and it is what a first-time user reaches for before they have a unit to hand.
Until now it was untested, which is how two live bugs got through:

* ``stop_endpoint``'s teardown ran ``pkill -f "--port <n>"``. getopt_long read
  the pattern as an *option*, pkill exited 2, and because the output was
  captured nobody saw it — so managed endpoints were never actually stopped
  and went on holding the GPU for the next model that needed it.
* A mistyped or non-executable ``serve_cmd`` surfaced only as a bare
  ``timeout waiting for <model>`` minutes later.

These tests drive the real ``start_endpoint`` / ``wait_ready`` /
``stop_endpoint`` against a stand-in server that speaks enough of the OpenAI
API for the readiness checks. VRAM draining is orthogonal to the lifecycle and
is stubbed out.
"""
from __future__ import annotations

import json
import os
import signal
import socket
import subprocess
import sys
import time as _real_time
from types import SimpleNamespace

import pytest

from localbench import runner
from localbench.runner import start_endpoint, stop_endpoint

MODEL = "mock-model"

_MOCK = r'''
import argparse, json
from http.server import BaseHTTPRequestHandler, HTTPServer

ap = argparse.ArgumentParser()
ap.add_argument("--port", type=int, required=True)
args = ap.parse_args()
MODEL = "__MODEL__"


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, obj):
        body = json.dumps(obj).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.startswith("/health"):
            self._send({"status": "ok"})
        elif self.path.startswith("/v1/models"):
            self._send({"data": [{"id": MODEL}]})
        else:
            self._send({})

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        self.rfile.read(n)
        self._send({"choices": [{"index": 0, "finish_reason": "length",
                                 "message": {"role": "assistant",
                                             "content": ""}}]})


HTTPServer(("127.0.0.1", args.port), H).serve_forever()
'''


class _FastTime:
    """runner's fixed grace periods (2s, 5s) are irrelevant to these tests."""

    @staticmethod
    def time() -> float:
        return _real_time.time()

    @staticmethod
    def sleep(seconds: float) -> None:
        _real_time.sleep(min(float(seconds), 0.05))


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _nonexistent_pid() -> int:
    """A pid that can never be a real process, so killing it is a no-op."""
    try:
        with open("/proc/sys/kernel/pid_max") as fh:
            return int(fh.read().strip()) + 1
    except OSError:
        return 2 ** 22 + 99


@pytest.fixture
def env(tmp_path, monkeypatch):
    port = _free_port()
    mock = tmp_path / "mock_server.py"
    mock.write_text(_MOCK.replace("__MODEL__", MODEL), encoding="utf-8")
    serve = tmp_path / "serve.sh"
    serve.write_text(f'#!/bin/sh\nexec "{sys.executable}" "{mock}" '
                     f'--port {port}\n', encoding="utf-8")
    serve.chmod(0o755)

    monkeypatch.setattr(runner, "time", _FastTime)
    # draining VRAM before a start is a separate concern from the lifecycle
    monkeypatch.setattr(runner, "_gpu_mem_mib", lambda: 0)

    local = {"conflict_units": [], "conflict_procs": [], "endpoints": []}
    ep = {"slug": "mock", "name": "Mock Model", "provider": "mock-local",
          "model": MODEL, "port": port, "serve_cmd": str(serve),
          "proc_kill": [], "ready": 30}
    log = tmp_path / "endpoint.log"

    def launch() -> int:
        """Start the server the way a user would — outside localbench."""
        fh = log.open("ab")
        proc = subprocess.Popen([str(serve)], stdout=fh, stderr=fh,
                                start_new_session=True)
        fh.close()
        return proc.pid

    yield SimpleNamespace(local=local, ep=ep, log=log, launch=launch,
                          port=port, serve=serve, tmp=tmp_path)

    subprocess.run(["pkill", "-9", "-f", "--", rf"--port {port}\b"],
                   capture_output=True)
    _real_time.sleep(0.3)


# --------------------------------------------------------------------------- #
# managed endpoints
# --------------------------------------------------------------------------- #

def test_managed_endpoint_starts_and_stops(env):
    ok, msg, reported = start_endpoint(env.local, env.ep, env.log)
    assert ok, msg
    assert reported == MODEL, "readiness must record the id the server reports"
    assert runner._listening(env.port)

    stop_endpoint(env.local, env.ep)
    assert not runner._listening(env.port), "server outlived stop_endpoint"


def test_stop_reaps_the_process_it_started(env):
    """Stopping must be by pid, not by guessing at a command-line pattern."""
    ok, msg, _ = start_endpoint(env.local, env.ep, env.log)
    assert ok, msg
    pid = env.ep.get("_pid")
    assert isinstance(pid, int), "start_endpoint must record the server pid"

    stop_endpoint(env.local, env.ep)
    with pytest.raises(ProcessLookupError):
        os.kill(pid, 0)          # still alive = it was never reaped


def test_stopping_an_endpoint_we_did_not_start_is_safe(env):
    """stop is also reached with no recorded process (e.g. after a restart)."""
    env.ep["_pid"] = _nonexistent_pid()
    stop_endpoint(env.local, env.ep)      # must not raise


# --------------------------------------------------------------------------- #
# external endpoints
# --------------------------------------------------------------------------- #

def test_external_endpoint_is_never_stopped(env):
    """`external: true` means *we did not start it, so we do not stop it*."""
    pid = env.launch()
    ext = dict(env.ep, external=True, serve_cmd=None)
    ok, msg, reported = start_endpoint(env.local, ext, env.log)
    assert ok, msg
    assert reported == MODEL

    stop_endpoint(env.local, ext)
    assert runner._listening(env.port), "an external server must be left running"
    assert "_pid" not in ext

    os.kill(pid, signal.SIGKILL)
    os.waitpid(pid, 0)


def test_external_endpoint_that_is_not_serving_fails_fast(env):
    ext = dict(env.ep, external=True, serve_cmd=None, ready=1)
    ok, msg, reported = start_endpoint(env.local, ext, env.log)
    assert not ok and reported is None, msg


# --------------------------------------------------------------------------- #
# configuration errors surface immediately, not as a timeout
# --------------------------------------------------------------------------- #

def test_missing_serve_cmd_is_reported_immediately(env, tmp_path):
    env.ep["serve_cmd"] = str(tmp_path / "nope.sh")
    ok, msg, _ = start_endpoint(env.local, env.ep, env.log)
    assert not ok
    assert "does not exist" in msg and "nope.sh" in msg


def test_non_executable_serve_cmd_is_reported_immediately(env, tmp_path):
    bad = tmp_path / "not-executable.sh"
    bad.write_text("#!/bin/sh\ntrue\n", encoding="utf-8")
    bad.chmod(0o644)
    env.ep["serve_cmd"] = str(bad)
    ok, msg, _ = start_endpoint(env.local, env.ep, env.log)
    assert not ok
    assert "not executable" in msg and "chmod +x" in msg


def test_endpoint_with_no_start_method_is_reported(env):
    env.ep["serve_cmd"] = None
    env.ep["units"] = []
    ok, msg, _ = start_endpoint(env.local, env.ep, env.log)
    assert not ok and "no start method" in msg


# --------------------------------------------------------------------------- #
# regression guards
# --------------------------------------------------------------------------- #

def test_pkill_separates_options_from_the_pattern(monkeypatch):
    """`pkill -f "--port 8080"` makes getopt_long read the pattern as an
    option; pkill exits 2, and captured output hid the fact that the kill
    never happened.
    """
    calls = []

    def fake_run(cmd, **kw):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr(runner.subprocess, "run", fake_run)
    runner._pkill([r"--port 8080\b"])
    assert calls, "expected pkill invocations"
    for cmd in calls:
        # both the TERM and the KILL pass must separate options from pattern
        assert cmd[0] == "pkill", cmd
        assert "--" in cmd, f"missing '--': {cmd}"
        at = cmd.index("--")
        assert at == len(cmd) - 2, f"'--' must sit right before it: {cmd}"
        assert cmd[at + 1] == r"--port 8080\b"


def test_wait_ready_rejects_a_server_offering_the_wrong_models(env, monkeypatch):
    """Readiness must confirm identity, not merely that *something* answers."""
    body = json.dumps({"data": [{"id": "a"}, {"id": "b"}]}).encode()

    class _Resp:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return body

    monkeypatch.setattr(runner.urllib.request, "urlopen",
                        lambda *a, **k: _Resp())
    ok, msg, reported = runner.wait_ready(dict(env.ep, model="expected"),
                                          env.log)
    assert not ok and reported is None, msg
    assert "expected" in msg


def test_wait_ready_accepts_a_sole_model_reporting_a_different_id(env,
                                                                 monkeypatch):
    """llama.cpp reports the GGUF path; that must still be usable."""
    body = json.dumps({"data": [{"id": "/models/some.gguf"}]}).encode()

    class _Resp:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return body

    monkeypatch.setattr(runner.urllib.request, "urlopen",
                        lambda *a, **k: _Resp())
    monkeypatch.setattr(runner, "_endpoint_warm", lambda ep: True)
    ok, msg, reported = runner.wait_ready(dict(env.ep, model="logical-name"),
                                          env.log)
    assert ok, msg
    assert reported == "/models/some.gguf"

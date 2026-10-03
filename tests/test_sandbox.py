"""Sandbox invariants: what the model under test can and cannot reach.

Structural assertions on the argv we hand to bwrap, plus behaviour tests for
the models.json shim — they run without bubblewrap installed.
"""
import json

import pytest

from localbench.harness import TMPFS_TREES, _bwrap_cmd, _network_env, \
    write_models_shim
from localbench.registry import Unit


def _cfg(tmp_path, **over):
    cfg = dict(pi_tree=str(tmp_path / "pi"), pi_cli="dist/cli.js",
               models_json=str(tmp_path / "models.json"),
               npm_global=str(tmp_path / "npm"), sandbox=True)
    cfg.update(over)
    return cfg


def _unit(task_dir=None, with_files=False):
    if with_files:
        (task_dir / "prompt.md").write_text("Q?")
        (task_dir / "SOLUTION.md").write_text("ANSWER IS 42")
        (task_dir / "verify.py").write_text("EXPECTED = 42")
        (task_dir / "teardown.sh").write_text("echo bye")
    return Unit(uid="task/x", suite="custom", benchmark="math", kind="task",
                ref="x", prompt="Q?", timeout=60, grader="verify",
                task_dir=task_dir)


def _build(tmp_path, unit=None, cfg=None):
    cfg = cfg or _cfg(tmp_path)
    unit = unit or _unit()
    for p in ("pi", "npm"):
        (tmp_path / p).mkdir(exist_ok=True)
    out, work = tmp_path / "out", tmp_path / "work"
    out.mkdir(exist_ok=True)
    work.mkdir(exist_ok=True)
    home = work / ".home"
    home.mkdir(parents=True, exist_ok=True)
    return _bwrap_cmd(cfg, unit, out, work, home), cfg


def _env(cmd: list[str]) -> dict:
    return {cmd[n + 1]: cmd[n + 2]
            for n, v in enumerate(cmd) if v == "--setenv"}


# flag -> how many values it consumes
_ARITY = {"--bind": 2, "--ro-bind": 2, "--symlink": 2,
          "--tmpfs": 1, "--dev": 1, "--proc": 1}


def _binds_of(cmd: list[str]) -> list[tuple[str, str, str]]:
    """(flag, source, dest) for every mount in the argv, in order."""
    out, i = [], 0
    while i < len(cmd):
        n = _ARITY.get(cmd[i])
        if n is None:
            i += 1
            continue
        vals = cmd[i + 1:i + 1 + n]
        src, dst = (vals[0], vals[1]) if n == 2 else (vals[0], vals[0])
        out.append((cmd[i], src, dst))
        i += 1 + n
    return out


class TestFilesystem:
    def test_every_writable_home_tree_is_shadowed_by_tmpfs(self, tmp_path):
        cmd, _ = _build(tmp_path)
        mounted = {dest for _, _, dest in _binds_of(cmd)}
        for tree in TMPFS_TREES:
            assert tree in mounted, f"{tree} not shadowed with tmpfs"

    def test_npm_global_is_bound_after_the_home_tmpfs(self, tmp_path):
        """npm_global lives under /home; bound before the tmpfs it is invisible."""
        cmd, cfg = _build(tmp_path)
        last_home_tmpfs = max(i for i, v in enumerate(cmd)
                              if v == "--tmpfs" and cmd[i + 1] == "/home")
        assert cmd.index(cfg["npm_global"]) > last_home_tmpfs, \
            "npm_global mount is shadowed by the /home tmpfs"

    def test_answer_and_grader_are_masked(self, tmp_path):
        task = tmp_path / "task"
        task.mkdir()
        cmd, _ = _build(tmp_path, unit=_unit(task_dir=task,
                                             with_files=True))
        mounts = {(src, dest) for _, src, dest in _binds_of(cmd)}
        for hidden in ("SOLUTION.md", "verify.py", "teardown.sh"):
            assert ("/dev/null", str(task / hidden)) in mounts, \
                f"{hidden} is readable by the model"

    def test_task_dir_is_a_read_only_bind(self, tmp_path):
        task = tmp_path / "task"
        task.mkdir()
        (task / "prompt.md").write_text("hi")
        cmd, _ = _build(tmp_path, unit=_unit(task_dir=task))
        assert ("--ro-bind", str(task)) in [(f, s) for f, s, _ in
                                            _binds_of(cmd)]

    def test_real_models_registry_is_never_mounted(self, tmp_path):
        """The full registry carries every provider's API key."""
        cmd, cfg = _build(tmp_path)
        assert cfg["models_json"] not in cmd, "raw models.json is mounted"


class TestNetwork:
    def test_egress_proxies_point_at_a_dead_port(self, tmp_path):
        env = _env(_build(tmp_path)[0])
        assert env["http_proxy"] == "http://127.0.0.1:9"
        assert env["https_proxy"] == "http://127.0.0.1:9"
        assert env["HTTP_PROXY"] == "http://127.0.0.1:9"
        assert env["all_proxy"] == "socks5://127.0.0.1:9"

    def test_loopback_is_exempt_so_the_endpoint_stays_reachable(self, tmp_path):
        env = _env(_build(tmp_path)[0])
        assert "127.0.0.1" in env["no_proxy"]
        assert "localhost" in env["no_proxy"]
        assert env["NO_PROXY"] == env["no_proxy"]

    def test_offline_flag_is_set(self, tmp_path):
        assert _env(_build(tmp_path)[0])["PI_OFFLINE"] == "1"

    def test_node_fetch_is_made_to_honour_the_proxy(self, tmp_path):
        """Pi is a Node app, and Node's built-in `fetch` ignores
        `http_proxy` by default — so without this the agent's own HTTP
        client sails straight past the block while curl and Python are
        stopped by it. On Node < 24 the flag is unknown and harmless.
        """
        assert _env(_build(tmp_path)[0])["NODE_USE_ENV_PROXY"] == "1"

    def test_all_proxy_variables_are_paired(self, tmp_path):
        """An unset *_proxy is a hole; every lowercase form needs its twin."""
        env = _env(_build(tmp_path)[0])
        for k in ("http_proxy", "https_proxy", "all_proxy", "no_proxy"):
            assert k.upper() in env, f"{k.upper()} missing"

    def test_blocking_can_be_disabled_explicitly(self, tmp_path):
        env = _env(_build(tmp_path, cfg=_cfg(tmp_path,
                                             block_network=False))[0])
        assert "http_proxy" not in env

    def test_network_env_emits_paired_flag_value_triples(self):
        out = _network_env({"block_network": True})
        assert len(out) % 3 == 0
        assert out[0] == "--setenv"
        assert _network_env({"block_network": False}) == []


class TestCodeSandboxInterpreter:
    """The code grader execs sys.executable inside a bwrap that mounts /usr.

    A venv or pyenv interpreter lives outside /usr, so without an explicit
    bind it cannot be exec'd at all — and the failure is reported as an
    ordinary grading miss, so HumanEval+/MBPP+ would silently score zero.
    """

    @pytest.fixture(autouse=True)
    def pretend_bwrap_is_installed(self, monkeypatch):
        """Assert on argv *construction*, not on bubblewrap's availability.

        Otherwise this whole class silently degrades to the no-bwrap
        fallback on a runner that doesn't ship it, and every assertion
        below fails for the wrong reason.
        """
        import localbench.graders as g
        monkeypatch.setattr(
            g.shutil, "which",
            lambda name: "/usr/bin/bwrap" if name == "bwrap" else None)

    def test_prefix_outside_usr_is_bound(self, tmp_path, monkeypatch):
        import localbench.graders as g
        fake = tmp_path / "venv310"
        (fake / "lib").mkdir(parents=True)
        monkeypatch.setattr(g.sys, "prefix", str(fake))
        monkeypatch.setattr(g.sys, "base_prefix", "/usr")
        argv = g._sandbox_python_argv(tmp_path / "scratch")
        at = argv.index(str(fake))
        assert argv[at - 1] == "--ro-bind"
        assert argv[at] == str(fake), "prefix must be mounted at its own path"

    def test_prefix_bind_comes_after_the_tmpfs_shadowing(self, tmp_path,
                                                         monkeypatch):
        import localbench.graders as g
        fake = tmp_path / "venv310"
        (fake / "lib").mkdir(parents=True)
        monkeypatch.setattr(g.sys, "prefix", str(fake))
        monkeypatch.setattr(g.sys, "base_prefix", "/usr")
        argv = g._sandbox_python_argv(tmp_path / "scratch")
        at = argv.index(str(fake))
        # /tmp and /home are tmpfs'd first, so a venv under them must be
        # mounted afterwards or the tmpfs hides it (same trap as npm_global)
        last_tmpfs = max(i for i, v in enumerate(argv) if v == "--tmpfs")
        assert at > last_tmpfs, "interpreter prefix is shadowed by a tmpfs"

    def test_prefix_under_usr_is_not_double_mounted(self, tmp_path,
                                                    monkeypatch):
        import localbench.graders as g
        monkeypatch.setattr(g.sys, "prefix", "/usr")
        monkeypatch.setattr(g.sys, "base_prefix", "/usr")
        argv = g._sandbox_python_argv(tmp_path / "scratch")
        ro_sources = [argv[i + 1] for i, v in enumerate(argv)
                      if v == "--ro-bind"]
        assert ro_sources.count("/usr") == 1, "/usr is already mounted"

    def test_interpreter_is_the_last_argument(self, tmp_path):
        import localbench.graders as g
        argv = g._sandbox_python_argv(tmp_path / "scratch")
        assert argv[-1] == g.sys.executable
        assert argv[-2] == "--"

    def test_falls_back_to_plain_interpreter_without_bwrap(self, tmp_path,
                                                          monkeypatch):
        import localbench.graders as g
        monkeypatch.setattr(g.shutil, "which", lambda name: None)
        assert g._sandbox_python_argv(tmp_path / "s") == [g.sys.executable]


class TestModelsShim:
    @staticmethod
    def _registry(tmp_path, providers=None):
        src = tmp_path / "models.json"
        src.write_text(json.dumps({"providers": providers or {
            "local-a": {"baseUrl": "http://127.0.0.1:1/v1", "apiKey": "secret-a"},
            "remote-b": {"baseUrl": "https://api.example.com/v1",
                         "apiKey": "sk-REAL-KEY"},
            "local-c": {"baseUrl": "http://127.0.0.1:2/v1", "apiKey": "secret-c"},
        }}))
        return src

    def test_only_the_provider_under_test_is_exposed(self, tmp_path):
        dest = write_models_shim(self._registry(tmp_path), "local-a",
                                 tmp_path / "home")
        assert list(json.loads(dest.read_text())["providers"]) == ["local-a"]

    def test_other_providers_api_keys_are_absent(self, tmp_path):
        dest = write_models_shim(self._registry(tmp_path), "local-a",
                                 tmp_path / "home")
        text = dest.read_text()
        assert "sk-REAL-KEY" not in text
        assert "secret-c" not in text

    def test_written_where_the_sandbox_puts_home(self, tmp_path):
        home = tmp_path / "work" / ".home"
        dest = write_models_shim(self._registry(tmp_path), "local-a", home)
        assert dest == home / ".pi" / "agent" / "models.json"
        assert dest.is_file()

    def test_unknown_provider_yields_empty_registry_not_crash(self, tmp_path):
        dest = write_models_shim(self._registry(tmp_path), "nope",
                                 tmp_path / "h")
        assert json.loads(dest.read_text()) == {"providers": {}}

    def test_malformed_registry_raises_clearly(self, tmp_path):
        bad = tmp_path / "models.json"
        bad.write_text("{not json")
        with pytest.raises(RuntimeError, match="cannot read"):
            write_models_shim(bad, "x", tmp_path / "h")

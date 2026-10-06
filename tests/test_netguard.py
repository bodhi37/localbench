"""netguard: the python side of the kernel egress guard.

Mostly structural asserts — the kernel behaviour is proven by
``scripts/netguard.sh verify`` (run as root once per boot), while this file
pins the invariants the argv construction and stamp checks rely on.
"""
import subprocess

import pytest

from localbench import netguard


class TestWrapArgv:
    def test_disabled_passthrough(self):
        cmd = ["bwrap", "--ro-bind"]
        assert netguard.wrap_argv({"netguard": False}, cmd) == cmd

    def test_enabled_but_missing_guard_refuses(self, monkeypatch):
        monkeypatch.setattr(netguard, "installed", lambda targets=None: False)
        with pytest.raises(netguard.NetguardError, match="not installed"):
            netguard.wrap_argv({"netguard": True}, ["bwrap"])

    def test_prefix_when_installed(self, monkeypatch):
        monkeypatch.setattr(netguard, "installed", lambda targets=None: True)
        out = netguard.wrap_argv({"netguard": True}, ["bwrap", "--x"])
        assert out[:4] == ["sudo", "-n", str(netguard.HELPER), "exec-as"]
        assert out[4:] == ["bwrap", "--x"]

    def test_default_is_enabled(self, monkeypatch):
        """An empty harness cfg must default to guarding, not to silently off."""
        monkeypatch.setattr(netguard, "installed", lambda targets=None: False)
        with pytest.raises(netguard.NetguardError):
            netguard.wrap_argv({}, ["bwrap"])


def test_endpoint_targets_default_host_and_dedupes(monkeypatch):
    import localbench.config as cfg
    monkeypatch.setattr(cfg, "load_local", lambda: {"endpoints": [
        {"port": 8105}, {"port": "1934"}, {"port": 8105}, {"port": True},
        {"host": None, "port": 8100},
        {"host": "192.0.2.7", "port": 8127},
        {"host": "192.0.2.7", "port": "8127"},
        {"port": "notaport"}]})
    assert netguard.endpoint_targets() == [
        ("127.0.0.1", 1934), ("127.0.0.1", 8100), ("127.0.0.1", 8105),
        ("192.0.2.7", 8127)]
    # loopback ports feed the nftables port set — including off-loopback
    # targets, whose traffic routes via dev lo (see endpoint_ports)
    assert netguard.endpoint_ports() == [1934, 8100, 8105, 8127]


def test_stamp_ok_requires_version_targets_and_fresh_helper(tmp_path, monkeypatch):
    stamp = tmp_path / "stamp"
    monkeypatch.setattr(netguard, "STAMP", stamp)
    monkeypatch.setattr(netguard, "_script_sha", lambda: "abc")
    stamp.write_text("version=3\ntargets=127.0.0.1:1920,127.0.0.1:1934\nhelper_sha=abc\n")
    assert netguard._stamp_ok([("127.0.0.1", 1934),
                               ("127.0.0.1", 1920)]) is True
    assert netguard._stamp_ok([("127.0.0.1", 1934)]) is False
    stamp.write_text("version=2\ntargets=127.0.0.1:1920\nhelper_sha=abc\n")
    assert netguard._stamp_ok() is False                # old format
    stamp.write_text("version=3\nhelper_sha=abc\n")
    assert netguard._stamp_ok() is True                 # targets not demanded
    stamp.write_text("version=3\ntargets=127.0.0.1:1920\nhelper_sha=zzz\n")
    assert netguard._stamp_ok() is False                # stale helper


class TestScript:
    def test_bash_syntax(self):
        r = subprocess.run(["bash", "-n", str(netguard.SCRIPT)],
                           capture_output=True, text=True)
        assert r.returncode == 0, r.stderr

    def test_validated_rules_are_present(self):
        text = netguard.SCRIPT.read_text()
        assert "socket cgroupv2" in text
        assert "TABLE=localbench_guard" in text
        assert "ct state established,related accept" in text
        assert "exec-as" in text
        assert "visudo" in text
        assert "setpriv" in text
        # nft set literals must be comma-joined (space-joined is a parse error)
        assert "tr ',' ' '" not in text
        assert "sort -nu" in text
        # non-loopback endpoint targets get one explicit accept each
        assert "ip daddr" in text
        assert "valid_targets" in text

    def test_exec_as_drops_privileges_before_exec(self):
        text = netguard.SCRIPT.read_text()
        assert "SUDO_UID" in text
        assert "setpriv --reuid" in text
        # entering the cgroup happens *before* dropping to the user
        assert text.index('echo $$ > "$CGROUP/cgroup.procs"') < \
               text.index("setpriv --reuid")

    def test_exec_as_only_ever_moves_itself(self):
        """In exec-as, the only thing ever written to procs is the helper PID."""
        text = netguard.SCRIPT.read_text()
        body = text.split("cmd_exec_as() {", 1)[1].split("\n}\n", 1)[0]
        hits = [ln for ln in body.splitlines() if "cgroup.procs" in ln]
        assert hits and all("$$" in ln for ln in hits)

#!/usr/bin/env python3
"""Relay control service (challenge build).

Usage:
    python3 relay.py            # serve on 127.0.0.1:8731 until interrupted
    python3 relay.py --port N   # serve on 127.0.0.1:N instead

A deliberately fragile administrative API. Binds to loopback only. Every
decision it makes is deterministic: nothing here uses randomness, wall-clock
time or the host environment.
"""
import argparse
import hashlib
import hmac
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = "127.0.0.1"
DEFAULT_PORT = 8731

SECRET = bytes.fromhex("b4d1c0de5f2a9e177c3b60a8d4e5f6071a2b3c4d5e6f708192a3b4c5d6e7f809")
MAC_CHARS = 4          # the service truncates session MACs to this many hex chars
POW_PREFIX = "00000"   # handshake proof-of-work: sha256(salt + ":" + proof) must start with this


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def session_mac(sid, role):
    return hmac.new(SECRET, ("%s|%s" % (role, sid)).encode("utf-8"),
                    hashlib.sha256).hexdigest()[:MAC_CHARS]


def vault_flag(sid):
    return "LBX{%s}" % hmac.new(SECRET, ("flag|%s" % sid).encode("utf-8"),
                                hashlib.sha256).hexdigest()[:20]


def check_proof(salt, proof):
    return digest("%s:%s" % (salt, proof)).startswith(POW_PREFIX)


class RelayHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        sys.stderr.write("[relay] %s\n" % (fmt % args))

    def _json(self, code, payload):
        body = (json.dumps(payload) + "\n").encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.startswith("/handshake"):
            query = self.path.split("?", 1)[1] if "?" in self.path else ""
            params = dict(part.split("=", 1) for part in query.split("&") if "=" in part)
            if "id" not in params or not params["id"].isdigit():
                return self._json(400, {"error": "handshake requires integer ?id="})
            n = int(params["id"])
            salt = digest("relay|%d" % n)[:16]
            return self._json(200, {"id": n, "salt": salt,
                                    "work": "sha256(salt + ':' + proof) must start with %r" % POW_PREFIX})
        return self._json(404, {"error": "no such endpoint"})

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", "0") or "0")
            payload = json.loads(self.rfile.read(length) or b"{}")
        except Exception as exc:
            return self._json(400, {"error": "bad request body: %s" % exc})

        if self.path.startswith("/session"):
            required = ("id", "proof")
            if not all(k in payload for k in required):
                return self._json(400, {"error": "session requires id and proof"})
            n = payload["id"]
            if not isinstance(n, int):
                return self._json(400, {"error": "id must be an integer"})
            salt = digest("relay|%d" % n)[:16]
            proof = str(payload.get("proof", ""))
            if not check_proof(salt, proof):
                return self._json(403, {"error": "work check failed"})
            sid = digest("sid|%d|%s" % (n, salt))
            return self._json(200, {"session": sid, "role": "guest",
                                    "mac": session_mac(sid, "guest"),
                                    "note": "administrative roles require a valid session mac"})

        if self.path.startswith("/admin/issue"):
            sid = str(payload.get("session", ""))
            role = str(payload.get("role", ""))
            mac = str(payload.get("mac", "")).strip().lower()
            if not sid or role != "admin":
                return self._json(400, {"error": "admin issue requires session and role=admin"})
            expected = session_mac(sid, "admin")
            if mac != expected:
                return self._json(403, {"error": "session mac mismatch (role=%s)" % role})
            return self._json(200, {"granted": True, "token": vault_flag(sid)})

        return self._json(404, {"error": "no such endpoint"})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = ap.parse_args()
    server = ThreadingHTTPServer((HOST, args.port), RelayHandler)
    sys.stderr.write("[relay] listening on %s:%d\n" % (HOST, args.port))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
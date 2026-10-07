"""Fixed user utilities: parameterized SQL, no shell, secrets RNG."""
import secrets
import sqlite3
import subprocess


def lookup_user(conn, username):
    """Return rows for a single username (parameterized)."""
    cur = conn.cursor()
    cur.execute("SELECT name FROM users WHERE name = ?", (username,))
    return cur.fetchall()


def run_backup(host):
    """Run the backup helper against a host without a shell."""
    subprocess.run(["backup", "--host", host, "--full"], shell=False, check=False)


def gen_token():
    """Return a 32-hex-digit session token from a CSPRNG."""
    return secrets.token_hex(16)

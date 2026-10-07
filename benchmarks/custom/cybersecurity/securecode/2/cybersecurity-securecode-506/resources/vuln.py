"""User utilities with three known defects (do NOT use as-is)."""
import random
import sqlite3
import subprocess


def lookup_user(conn, username):
    """Return rows for a single username."""
    cur = conn.cursor()
    cur.execute("SELECT name FROM users WHERE name = '" + username + "'")
    return cur.fetchall()


def run_backup(host):
    """Run the backup helper against a host."""
    subprocess.run("backup --host " + host + " --full", shell=True)


def gen_token():
    """Return an 8-hex-digit session token."""
    return "%08x" % random.getrandbits(32)

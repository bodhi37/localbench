#!/usr/bin/env python3
"""Vault passphrase checker (challenge build).

Usage:
    python3 vault_check.py KEYFILE     # read the candidate from a file
    python3 vault_check.py             # read the candidate from stdin

Prints ACCESS GRANTED when the candidate passphrase satisfies the vault
constraints, otherwise ACCESS DENIED. This checker is the only authority on
what the vault accepts: any candidate it grants is a valid key.
"""
import sys

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
MODULUS = 1000003
WEIGHTS = [3, 11, 17, 23, 29, 37, 41, 53]
TARGET_A = 1690
TARGET_B = 14
KEY_LENGTH = 8


def load_candidate(path):
    if path is None:
        data = sys.stdin.read()
    else:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            data = fh.read()
    return data.strip()


def check(key):
    if len(key) != KEY_LENGTH:
        return False
    if any(ch not in ALPHABET for ch in key):
        return False
    idx = [ALPHABET.index(ch) for ch in key]
    acc = 0
    for weight, value in zip(WEIGHTS, idx):
        acc = (acc + weight * value) % MODULUS
    if acc != TARGET_A:
        return False
    if idx[0] + idx[-1] != TARGET_B:
        return False
    return True


def main():
    candidate = load_candidate(sys.argv[1] if len(sys.argv) > 1 else None)
    print("ACCESS GRANTED" if check(candidate) else "ACCESS DENIED")


if __name__ == "__main__":
    main()
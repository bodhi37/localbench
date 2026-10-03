#!/usr/bin/env python3
"""Verifier for instruction-following-negative-constraints-303.

Grading scope: the whole response, after stripping trailing whitespace per line
and blank lines at the very start/end, must be exactly 4 lines of exactly 7
words, each word drawn from the task vocabulary, no word repeated, no word
containing 'E', TOPAZ/QUILL/MAROON each exactly once, exactly one 'Z'-word per
line, and each line's first and last words starting with different letters.

Pure: reads only the response text. The vocabulary is mirrored here as VOCAB so
the grading path never reads $TASK_DIR; `--selftest` checks the mirror against
resources/vocabulary.txt.
"""
import argparse
import json
import os
import sys

VOCAB = (
    "ANVIL", "BANJO", "BIRCH", "BREEZE", "CACTUS", "CEDAR", "CHERRY", "CLOUD",
    "COPPER", "DRIFT", "DUSK", "EMBER", "FIRM", "FLINT", "GARNET", "GLOSSY",
    "GRAVY", "HAZY", "HEDGE", "HUSK", "IRON", "IVORY", "JOLT", "KETTLE",
    "KIOSK", "KOALA", "LARCH", "LINEN", "LUMINOUS", "MAROON", "MEADOW",
    "MERCURY", "MILK", "MOSS", "NECTAR", "NOON", "OCEAN", "OPAL", "PEBBLE",
    "PLOUGH", "QUARTZ", "QUENCH", "QUILL", "RAVIOLI", "RIVER", "SUGAR",
    "SULPHUR", "TOPAZ", "TUMULT", "UNISON", "VELVET", "VIVID", "WALNUT",
    "WHEAT", "YARROW", "YELLOW", "ZEPHYR", "ZINC",
)
REQUIRED = ("TOPAZ", "QUILL", "MAROON")
LINES_REQUIRED = 4
WORDS_PER_LINE = 7


def emit(passed, detail):
    print(json.dumps({"pass": bool(passed), "detail": detail}))
    sys.exit(0 if passed else 1)


def load_response(args):
    for path in (args.response, os.path.join(args.out_dir or "", "response.txt")):
        if path and os.path.isfile(path):
            with open(path, encoding="utf-8", errors="replace") as fh:
                return fh.read()
    return None


def selftest(task_dir):
    path = os.path.join(task_dir or ".", "resources", "vocabulary.txt")
    with open(path, encoding="utf-8") as fh:
        on_disk = tuple(ln.strip() for ln in fh if ln.strip())
    assert tuple(sorted(on_disk)) == tuple(sorted(VOCAB)), "VOCAB mirror is out of sync"
    assert len(VOCAB) == len(set(VOCAB)), "duplicate entry in VOCAB"
    assert sum(1 for w in VOCAB if "E" in w) == 20, "expected 20 E-bearing entries"
    assert sum(1 for w in VOCAB if "E" not in w and "Z" in w) == 4, "expected 4 E-free Z-words"
    assert all(w in VOCAB for w in REQUIRED), "required word missing from VOCAB"
    print(json.dumps({"selftest": "pass", "vocab": len(VOCAB)}))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-dir")
    ap.add_argument("--out-dir")
    ap.add_argument("--response")
    ap.add_argument("--selftest", action="store_true",
                    help="harness-side: check the VOCAB mirror against resources/vocabulary.txt")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest(args.task_dir))

    text = load_response(args)
    if text is None:
        emit(False, "no response text supplied (pass --response FILE)")

    lines = [ln.strip() for ln in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    while lines and lines[0] == "":
        lines.pop(0)
    while lines and lines[-1] == "":
        lines.pop()
    if len(lines) != LINES_REQUIRED:
        emit(False, "rule 1: expected exactly %d lines, got %d" % (LINES_REQUIRED, len(lines)))

    rows = []
    for i, ln in enumerate(lines, start=1):
        words = ln.split()
        if len(words) != WORDS_PER_LINE:
            emit(False, "rule 1: line %d has %d words, exactly %d required: %r"
                        % (i, len(words), WORDS_PER_LINE, ln[:100]))
        rows.append(words)

    flat = [w for r in rows for w in r]
    bad_vocab = [w for w in flat if w not in VOCAB]
    if bad_vocab:
        emit(False, "rule 2: word(s) not in the vocabulary: %s" % sorted(set(bad_vocab)))
    if len(set(flat)) != len(flat):
        dupes = sorted({w for w in flat if flat.count(w) > 1})
        emit(False, "rule 2: repeated word(s): %s" % dupes)
    with_e = [w for w in flat if "E" in w]
    if with_e:
        emit(False, "rule 3: word(s) containing E used: %s" % sorted(set(with_e)))
    for w in REQUIRED:
        if flat.count(w) != 1:
            emit(False, "rule 4: %s must appear exactly once, appears %d time(s)" % (w, flat.count(w)))
    for i, r in enumerate(rows, start=1):
        if sum(1 for w in r if "Z" in w) != 1:
            emit(False, "rule 5: line %d must contain exactly one word containing Z: %r" % (i, r))
        if r[0][0] == r[-1][0]:
            emit(False, "rule 6: line %d starts and ends with a word beginning %r: %r"
                        % (i, r[0][0], r))
    emit(True, "all rules 1-6 satisfied: 4 lines x 7 distinct vocabulary words, no E, "
               "TOPAZ/QUILL/MAROON each once, one Z-word per line")


if __name__ == "__main__":
    main()
"""`localbench` command line interface."""
from __future__ import annotations

import argparse
import json
import sys
from typing import Optional

from . import __version__
from .config import ConfigError, load_suite
from .netguard import NetguardError


def _csv(value: str) -> list[str]:
    return [s.strip() for s in (value or "").split(",") if s.strip()]


# --------------------------------------------------------------------------- #
# list
# --------------------------------------------------------------------------- #

def cmd_list(args) -> int:
    from .registry import benchmarks_available

    info = benchmarks_available()
    weights = load_suite()["weights"]
    if args.bench:
        keep = set(args.bench)
        info = {k: v for k, v in info.items() if k in keep}
    if not info:
        print("no benchmarks found")
        return 1
    if args.json:
        print(json.dumps(info, indent=2))
        return 0

    custom = {k: v for k, v in info.items() if v.get("suite") == "custom"}
    known = {k: v for k, v in info.items() if v.get("suite") != "custom"}
    print(f"{'benchmark':30} {'suite':7} {'grader':8} {'wt':>4} {'units':>7}  notes")
    print("-" * 88)
    for name, v in custom.items():
        print(f"{name:30} {'custom':7} {v.get('grader',''):8} "
              f"{weights.get(name, 1.0):>4} {v.get('tasks', 0):>7}  task dirs")
    for name, v in known.items():
        if v.get("fetched"):
            units = f"{v.get('items', 0):>7}"
            note = v.get("license") or ""
        else:
            units = f"{'—':>7}"
            note = "NOT FETCHED — run `localbench fetch`"
        print(f"{name:30} {'known':7} {v.get('grader',''):8} "
              f"{weights.get(name, 1.0):>4} {units}  {note}")
    return 0


# --------------------------------------------------------------------------- #
# fetch
# --------------------------------------------------------------------------- #

def cmd_fetch(args) -> int:
    from .fetch import fetch
    return fetch(benchmarks=args.bench or None, force=args.force, seed=args.seed)


# --------------------------------------------------------------------------- #
# run
# --------------------------------------------------------------------------- #

def cmd_run(args) -> int:
    from . import runner
    limit = args.limit
    if limit is None:
        limit = int(load_suite().get("default_limit", 0))
    return runner.run(models=_csv(args.models), benchmarks=_csv(args.bench),
                      tasks=_csv(args.tasks), limit=limit,
                      dry_run=args.dry_run, keep_work=args.keep_work,
                      run_id=args.run_id)


# --------------------------------------------------------------------------- #
# score / report
# --------------------------------------------------------------------------- #

def _structure(args) -> dict:
    from .scoring import score_structure
    return score_structure(run=args.run or None, models=_csv(args.models) or None,
                           benchmarks=_csv(args.bench) or None,
                           all_runs=args.all_runs,
                           limit=args.limit if args.limit is not None else 0)


def cmd_score(args) -> int:
    structure = _structure(args)
    if args.json:
        print(json.dumps(structure, indent=2))
        return 0
    models, order = structure["models"], structure["order"]
    if not order:
        print("no results yet — run `localbench run` first")
        return 1

    print(f"run filter: {structure['run']}   "
          f"records: {structure['selected_records']}")
    print()
    width = max(len(models[s]["name"]) for s in order)
    print(f"{'benchmark':30} {'wt':>4}  " +
          "  ".join(f"{models[s]['name']:>{width}}" for s in order))
    print("-" * (36 + (width + 2) * len(order)))

    seen: list[str] = []
    for slug in order:
        for n in models[slug]["benchmarks"]:
            if n not in seen:
                seen.append(n)
    for name in sorted(seen):
        w = structure["weights"].get(name, 1.0)
        cells = []
        for slug in order:
            b = models[slug]["benchmarks"].get(name)
            if not b or not b.get("attempted"):
                cells.append(f"{'—':>{width}}")
            else:
                s = (f"{b['accuracy']:.1f} ({b['passed']}/{b['attempted']})")
                if b.get("status") == "partial":
                    s += "!"
                cells.append(f"{s:>{width}}")
        print(f"{name:30} {w:>4}  " + "  ".join(cells))

    print("-" * (36 + (width + 2) * len(order)))
    hdr = f"{'SUITE SCORE':30} {'':>4}  "
    for slug in order:
        sc = models[slug].get("suite_score")
        hdr += f"{'—' if sc is None else format(sc, '.1f'):>{width}}  "
    print(hdr.rstrip())
    for src in ("custom", "known"):
        row = f"{f'  of which {src}':30} {'':>4}  "
        vals = []
        for slug in order:
            v = models[slug].get("by_suite", {}).get(src)
            vals.append(f"{'—' if v is None else format(v, '.1f'):>{width}}")
        print(row + "  ".join(vals))
    print()
    print("weights: config/suite.json   (benchmark marked ! = partial coverage)")
    if args.bench:
        print(f"scope: only {args.bench} contributed to the suite score")
    return 0


def cmd_report(args) -> int:
    from .registry import benchmarks_available
    from .report import write_report
    structure = _structure(args)
    md, js = write_report(structure, benchmarks_available())
    print(f"wrote {md}")
    print(f"wrote {js}")
    if not structure["order"]:
        print("note: no result rows yet")
    return 0


# --------------------------------------------------------------------------- #
# netguard
# --------------------------------------------------------------------------- #

def cmd_netguard(args) -> int:
    from . import netguard

    action = args.action or "status"
    if action == "status":
        st = netguard.status()
        for k in ("enabled", "installed", "writable", "stamp_ports",
                  "cgroup", "nft_table", "stamp", "script"):
            print(f"{k:14} {st[k]}")
        if not st["installed"]:
            print("\nnot installed — `localbench netguard install` "
                  "(needs sudo, once per boot)")
            return 1
        ok, msg = netguard.verify()
        print()
        print(msg)
        return 0 if ok else 1
    if action == "install":
        ok, msg = netguard.ensure()
    elif action == "uninstall":
        ok, msg = netguard.uninstall()
    else:  # verify
        ok, msg = netguard.verify()
    print(msg)
    return 0 if ok else 1


# --------------------------------------------------------------------------- #

def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="localbench",
        description="Benchmark local LLM endpoints against a hybrid suite of "
                    "published and hand-crafted agentic tasks.",
        epilog="typical workflow:\n"
               "  localbench list                 # what's in the suite\n"
               "  localbench fetch                # download published datasets\n"
               "  localbench run --dry-run        # what would run, and how much\n"
               "  localbench run --models <slug>  # run it\n"
               "  localbench score                # suite + per-benchmark scores\n"
               "  localbench report               # results/REPORT.md\n\n"
               "Machine-specific endpoints and paths live in config/local.json\n"
               "(gitignored). Copy config/local.json.example to get started.",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", action="version", version=f"localbench {__version__}")
    sub = ap.add_subparsers(dest="cmd", metavar="COMMAND")

    p = sub.add_parser("list", help="show every benchmark and its unit count")
    p.add_argument("--bench", action="append", metavar="NAME")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_list)

    p = sub.add_parser("fetch", help="download published benchmarks into benchmarks/known/")
    p.add_argument("bench", nargs="*", metavar="NAME",
                   help="benchmarks to fetch (default: all)")
    p.add_argument("--force", action="store_true", help="re-fetch even if present")
    p.add_argument("--seed", type=int, default=0, help="shuffle seed at ingest")
    p.set_defaults(fn=cmd_fetch)

    def add_filter(p_):
        p_.add_argument("--models", default="", metavar="SLUG,SLUG")
        p_.add_argument("--bench", default="", metavar="NAME,NAME",
                        help="restrict to these benchmarks")
        p_.add_argument("--run", default="", metavar="RUN_ID",
                        help="score this run only (default: newest run per model)")
        p_.add_argument("--all-runs", action="store_true",
                        help="pool every run instead of the newest per model")
        p_.add_argument("--limit", type=int, default=None, metavar="N",
                        help="fallback per-benchmark cap for the expected "
                             "denominator (records normally carry their own)")

    p = sub.add_parser("run", help="run the suite against one or more endpoints")
    p.add_argument("--models", default="", metavar="SLUG,SLUG")
    p.add_argument("--bench", default="", metavar="NAME,NAME",
                   help="benchmarks to run (default: config/suite.json "
                        "default_benchmarks)")
    p.add_argument("--tasks", default="", metavar="ID,ID",
                   help="restrict to specific unit refs (custom task ids)")
    p.add_argument("--limit", type=int, default=None, metavar="N",
                   help="items per known benchmark (default: suite.json "
                        "default_limit; 0 = the full dataset)")
    p.add_argument("--run-id", default=None, metavar="ID")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--keep-work", action="store_true",
                   help="keep sandbox scratch dirs")
    p.set_defaults(fn=cmd_run)

    p = sub.add_parser("score", help="print suite + per-benchmark scores")
    add_filter(p)
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_score)

    p = sub.add_parser("report", help="write results/REPORT.md and results/results.json")
    add_filter(p)
    p.set_defaults(fn=cmd_report)

    p = sub.add_parser(
        "netguard",
        help="kernel egress guard for the sandbox (install needs sudo once/boot)")
    p.add_argument("action", nargs="?", choices=("status", "install",
                                                 "uninstall", "verify"),
                   default="status",
                   help="status = show + self-test (default)")
    p.set_defaults(fn=cmd_netguard)
    return ap


def main(argv: Optional[list[str]] = None) -> int:
    ap = build_parser()
    args = ap.parse_args(argv)
    if getattr(args, "fn", None) is None:      # bare `localbench`
        ap.print_help()
        return 2
    try:
        return args.fn(args)
    except ConfigError as e:
        print(f"config error:\n{e}", file=sys.stderr)
        return 2
    except NetguardError as e:
        print(f"kernel egress guard error:\n{e}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("\ninterrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())

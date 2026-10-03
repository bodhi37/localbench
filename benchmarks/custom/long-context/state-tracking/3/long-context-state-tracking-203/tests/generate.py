#!/usr/bin/env python3
"""Deterministic generator for the resources/ of long-context-state-tracking-203,
plus the expected answer and a reference simulator (harness-side only).

The committed resource file is the source of truth; re-running reproduces it
byte-for-byte (fixed seed).
"""
import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
RES = HERE.parent / "resources"
TARGET_SKU = "NX-4471"
TARGET_BINS = ["A-01", "A-02", "B-07"]
INITIAL = [("A-01", "NX-4471", 120), ("A-02", "NX-4471", 75), ("B-07", "NX-4471", 0),
           ("C-03", "NX-4472", 40), ("B-07", "NX-4472", 18), ("A-02", "NX-4473", 9)]
ALL_BINS = ["A-01", "A-02", "B-07", "C-03"]
ALL_SKUS = ["NX-4471", "NX-4472", "NX-4473"]


def simulate(events, initial):
    """Apply the event semantics exactly as the prompt states them."""
    state = {}
    for b, s, q in initial:
        state[(b, s)] = q
    applied = {}          # seq -> event dict, for events currently applied
    voided = set()        # seqs whose effect has been cancelled
    effective_voids = 0
    for ev in events:
        op, a, seq = ev["op"], ev["args"], ev["seq"]
        if op == "VOID":
            t = int(a[0])
            tgt = applied.get(t)
            if tgt is None or t in voided or tgt["op"] not in ("RECEIVE", "PICK", "TRANSFER"):
                continue
            if tgt["op"] == "RECEIVE":
                b, s, q = tgt["args"]
                state[(b, s)] -= int(q)
            elif tgt["op"] == "PICK":
                b, s, q = tgt["args"]
                state[(b, s)] += int(q)
            else:  # TRANSFER: inverse is the swap
                fb, tb, s, q = tgt["args"]
                state[(fb, s)] += int(q)
                state[(tb, s)] -= int(q)
            voided.add(t)
            effective_voids += 1
        elif op == "RECEIVE":
            b, s, q = a
            state[(b, s)] = state.get((b, s), 0) + int(q)
            applied[seq] = ev
        elif op == "PICK":
            b, s, q = a
            state[(b, s)] = state.get((b, s), 0) - int(q)
            applied[seq] = ev
        elif op == "TRANSFER":
            fb, tb, s, q = a
            state[(fb, s)] = state.get((fb, s), 0) - int(q)
            state[(tb, s)] = state.get((tb, s), 0) + int(q)
            applied[seq] = ev
        elif op == "RECOUNT":
            b, s, q = a
            state[(b, s)] = int(q)
            applied[seq] = ev
        else:
            raise AssertionError("unknown op " + op)
    final = {b: state.get((b, TARGET_SKU), 0) for b in TARGET_BINS}
    init_total = sum(q for b, s, q in initial if s == TARGET_SKU)
    return {
        "final_bins": final,
        "effective_voids": effective_voids,
        "net_change": sum(final.values()) - init_total,
    }


def main():
    rng = random.Random(31415926)
    raw = []  # (op, args) without seqs; one VOID placeholder resolved later

    def rand_event(for_target=True):
        sku = TARGET_SKU if (for_target and rng.random() < 0.62) else rng.choice(ALL_SKUS[1:])
        bins = TARGET_BINS if (sku == TARGET_SKU and rng.random() < 0.7) else ALL_BINS
        r = rng.random()
        if r < 0.42:
            return ("RECEIVE", [rng.choice(bins), sku, rng.randrange(5, 60)])
        if r < 0.80:
            return ("PICK", [rng.choice(bins), sku, rng.randrange(2, 45)])
        if r < 0.93:
            fb, tb = rng.sample(ALL_BINS, 2)
            return ("TRANSFER", [fb, tb, sku, rng.randrange(1, 25)])
        return ("RECOUNT", [rng.choice(ALL_BINS), sku, rng.randrange(0, 140)])

    body1 = [rand_event() for _ in range(300)]
    body2 = [rand_event() for _ in range(250)]
    raw.extend(body1)
    fwd = ("VOID", ["__BODY2_FIRST__"])   # forward reference: must have no effect
    raw.append(fwd)
    raw.extend(body2)

    # Assign seqs in order so the forward reference can be resolved exactly.
    seq = 1000
    events = []
    for op, args in raw:
        events.append({"seq": seq, "op": op, "args": list(args)})
        seq += rng.choice([1, 1, 1, 2, 3])
    fwd_index = len(body1)
    # Point the forward-referencing VOID at the first *voidable* event of body2
    # (a RECOUNT target would make the VOID a no-op and weaken the trap).
    VOIDABLE = ("RECEIVE", "PICK", "TRANSFER")
    target = next(e for e in events[fwd_index + 1:] if e["op"] in VOIDABLE)
    events[fwd_index]["args"] = [str(target["seq"])]

    # ---- controlled trap tail ----
    def earlier(pred):
        """Search only body1, so trap targets can never collide with body2's."""
        return [e for e in events[:fwd_index] if pred(e)]

    rec = earlier(lambda e: e["op"] == "RECEIVE" and e["args"][1] == TARGET_SKU and e["args"][2] >= 20)
    pik = earlier(lambda e: e["op"] == "PICK" and e["args"][1] == TARGET_SKU)
    trf = earlier(lambda e: e["op"] == "TRANSFER" and e["args"][2] == TARGET_SKU)
    rct = earlier(lambda e: e["op"] == "RECOUNT")
    assert rec and pik and trf and rct, "need one of each op to build the traps"

    tail = [
        ("VOID", [str(rec[0]["seq"])]),            # effective: undoes a live RECEIVE
        ("VOID", [str(rec[0]["seq"])]),            # no effect: already voided
        ("VOID", [str(rct[0]["seq"])]),            # no effect: RECOUNT cannot be voided
        ("VOID", ["999999"]),                       # no effect: unknown seq
        ("VOID", [str(trf[0]["seq"])]),            # effective: inverse of the transfer
        ("PICK", ["B-07", TARGET_SKU, rng.randrange(150, 190)]),   # drives B-07 negative
        ("VOID", [str(pik[0]["seq"])]),            # effective: undoes a live PICK
        ("RECOUNT", ["A-02", TARGET_SKU, rng.randrange(10, 60)]),  # absolute set
        ("VOID", [str(events[fwd_index + 1]["seq"])]),  # effective: void of body2[0]
        ("RECEIVE", ["A-01", TARGET_SKU, rng.randrange(5, 40)]),
    ]
    for op, args in tail:
        events.append({"seq": seq, "op": op, "args": list(args)})
        seq += rng.choice([1, 2, 3])

    # ---- write the log ----
    lines = ["WAREHOUSE EVENT LOG - STOCK RECONCILIATION EXERCISE",
             "Opening stock is given by the INITIAL lines below; each EVENT line is",
             "<seq> <OP> <arguments...> and events are processed in file order."]
    for b, s, q in INITIAL:
        lines.append("INITIAL %s %s %d" % (b, s, q))
    lines.append("")
    for ev in events:
        lines.append("%d %s %s" % (ev["seq"], ev["op"], " ".join(str(x) for x in ev["args"])))
    RES.mkdir(parents=True, exist_ok=True)
    (RES / "warehouse_events.log").write_text("\n".join(lines) + "\n", encoding="utf-8")

    expected = simulate(events, INITIAL)
    (HERE / "expected.json").write_text(json.dumps(expected, indent=2) + "\n", encoding="utf-8")

    # Sanity properties that make the task discriminative.
    void_events = [e for e in events if e["op"] == "VOID"]
    assert expected["effective_voids"] == 4, expected
    assert len(void_events) == 8, len(void_events)  # 1 forward-referencing + 7 in the trap tail
    assert min(expected["final_bins"].values()) < 0, expected
    assert expected["net_change"] != 0, expected
    print(json.dumps(expected, indent=2))
    print("events:", len(events), "void lines:", len(void_events),
          "effective:", expected["effective_voids"], "bytes:", (RES / "warehouse_events.log").stat().st_size)


if __name__ == "__main__":
    main()

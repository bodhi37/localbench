#!/usr/bin/env python3
"""Deterministic generator for the resources/ of long-context-multi-hop-202,
plus the expected answer (harness-side only). The committed resource files are
the source of truth; re-running reproduces them byte-for-byte (fixed seed).
"""
import csv
import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
RES = HERE.parent / "resources"
TARGET_ORDER = "O-4471"

WORDS = ["bracket", "gasket", "sleeve", "clamp", "bushing", "shim", "spacer",
         "coupler", "washer", "ferrule", "bearing", "pulley", "roller", "pin"]
MATS = ["steel", "brass", "nylon", "aluminium", "copper", "ceramic"]
SIZES = ["M4", "M6", "M8", "M10", "M12", "1/4in", "3/8in"]


def main():
    rng = random.Random(778811)

    suppliers = []
    for i, name in enumerate(["NORTHWIND FABRICATORS", "CALDER METALWORKS", "SEVERN POLYMERS",
                              "ORRIN PRECISION", "HALLOWAY BRASS", "TAMBER SUPPLY"]):
        suppliers.append({"code": "SUP-%s" % chr(ord('A') + i), "name": name,
                          "country": rng.choice(["NO", "ES", "UK", "IE", "PT", "DE"]),
                          "lead_time_days": 0})  # assigned after the target order is fixed

    parts = []
    for i in range(40):
        code = "PC-%d" % (1001 + i)
        desc = "%s %s %s" % (rng.choice(MATS), rng.choice(WORDS), rng.choice(SIZES))
        parts.append({"code": code, "desc": desc,
                      "supplier": rng.choice(suppliers)["code"],
                      "unit_mass_g": rng.randrange(12, 940),
                      "unit_price_cents": rng.randrange(35, 4800),
                      "units_per_case": rng.choice([12, 20, 24, 50, 100])})

    orders = ["O-4468", "O-4470", TARGET_ORDER, "O-4473", "O-4475"]
    lines = []
    for oid in orders:
        k = 6 if oid == TARGET_ORDER else rng.randrange(2, 5)
        chosen = rng.sample(parts, k)
        for ln, p in enumerate(chosen, start=1):
            lines.append({"order_id": oid, "line_no": ln, "part_code": p["code"],
                          "uom": rng.choice(["unit", "case"]),
                          "quantity": rng.randrange(1, 15)})

    # Assign lead times so the supplier hop is load-bearing: the largest lead
    # time among the target order's suppliers must be strictly below the global
    # maximum, otherwise a solver that skips the supplier hop would still be
    # right by accident.
    target_sups = {p["supplier"] for p in parts
                   if p["code"] in {l["part_code"] for l in lines if l["order_id"] == TARGET_ORDER}}
    unused = [s for s in suppliers if s["code"] not in target_sups]
    assert unused, "target order must not touch every supplier"
    lead_pool = [19, 14, 10, 8, 6, 5]
    ordered = [unused[0]] + [s for s in suppliers if s["code"] != unused[0]["code"]]
    for s, lt in zip(ordered, lead_pool):
        s["lead_time_days"] = lt
    tmax = max(s["lead_time_days"] for s in suppliers if s["code"] in target_sups)
    gmax = max(s["lead_time_days"] for s in suppliers)
    assert tmax < gmax, (tmax, gmax)

    for name, cols, rows in [
        ("suppliers.csv", ["supplier_code", "supplier_name", "country", "lead_time_days"],
         [[s["code"], s["name"], s["country"], str(s["lead_time_days"])] for s in suppliers]),
        ("orders.csv", ["order_id", "line_no", "part_code", "uom", "quantity"],
         [[l["order_id"], str(l["line_no"]), l["part_code"], l["uom"], str(l["quantity"])] for l in lines]),
    ]:
        RES.mkdir(parents=True, exist_ok=True)
        with open(RES / name, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(cols)
            w.writerows(rows)

    md = ["# Parts catalog", "",
          "| part_code | description | supplier_code | unit_mass_g | unit_price_cents | units_per_case |",
          "|---|---|---|---|---|---|"]
    for p in parts:
        md.append("| %s | %s | %s | %d | %d | %d |" % (p["code"], p["desc"], p["supplier"],
                                                        p["unit_mass_g"], p["unit_price_cents"],
                                                        p["units_per_case"]))
    (RES / "parts_catalog.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    # ---- compute the expected answer ----
    by_part = {p["code"]: p for p in parts}
    by_sup = {s["code"]: s for s in suppliers}
    tl = [l for l in lines if l["order_id"] == TARGET_ORDER]
    total_mass = total_cost = 0
    heaviest, heavy_mass = None, -1
    sups = set()
    tie = False
    for l in tl:
        p = by_part[l["part_code"]]
        eff = l["quantity"] * p["units_per_case"] if l["uom"] == "case" else l["quantity"]
        m = eff * p["unit_mass_g"]
        total_mass += m
        total_cost += eff * p["unit_price_cents"]
        sups.add(p["supplier"])
        if m > heavy_mass:
            heaviest, heavy_mass, tie = p["code"], m, False
        elif m == heavy_mass:
            tie = True
    assert not tie, "heaviest line must be unique"
    assert len(sups) > 1
    expected = {
        "order_id": TARGET_ORDER,
        "total_mass_g": total_mass,
        "total_cost_cents": total_cost,
        "max_lead_time_days": max(by_sup[s]["lead_time_days"] for s in sups),
        "heaviest_line_part": heaviest,
    }
    (HERE / "expected.json").write_text(json.dumps(expected, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(expected, indent=2))
    print("target lines:", len(tl), "distinct suppliers:", len(sups), "total catalog parts:", len(parts))


if __name__ == "__main__":
    main()

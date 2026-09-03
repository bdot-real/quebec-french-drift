#!/usr/bin/env python3
"""Print the figures the write-up quotes, so prose and report cannot drift apart.

    python3 scripts/article_numbers.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

report = json.loads(Path("results/report/report.json").read_text(encoding="utf-8"))
pc = lambda v, d=1: "—" if v is None else f"{v * 100:.{d}f}%"

print("MATCHED PAIRS (baseline prompt)\n")
print(f"| Model | Pairs | QC→FR | FR→QC | Asymmetry | QC higher | FR higher | Tied | p |")
print("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
for name, a in report["matched_attractor"].items():
    st = a.get("sign_test")
    p = "—" if not st else ("< 0.001" if st["p_value"] < 0.001 else f"{st['p_value']:.3f}")
    print(f"| {name} | {a['n_pairs']} | {pc(a['qc_to_fr_drift'])} | {pc(a['fr_to_qc_drift'])} | "
          f"{pc(a['asymmetry'])} | {a['pairs_qc_higher']} | {a['pairs_fr_higher']} | "
          f"{a['pairs_tied']} | {p} |")

print("\n\nSCORECARD (Quebec-origin)\n")
print("| Model | CLR base | MDR base | MDR QC-prompt | QFCR | untouched | pos. control |")
print("| --- | ---: | ---: | ---: | ---: | ---: | --- |")
for m in report["models"]:
    s, c = m["scorecard"], m["positive_control"]
    ctrl = "—" if not c else ("passed" if c["passed"] else
                              f"FAILED ({pc(c['baseline_drift'],0)} vs {pc(c['metropolitan_drift'],0)})")
    print(f"| {m['meta']['model']} | {pc(s['CLR_baseline'])} | {pc(s['MDR_baseline'])} | "
          f"{pc(s['MDR_prompted'])} | {pc(s['QFCR_proofread'])} | "
          f"{pc(s['unchanged_proofread'])} | {ctrl} |")

cats = ["lexical", "terminology", "semantic", "register", "grammar"]
print("\n\nBASELINE DRIFT BY CATEGORY (Quebec-origin)\n")
print("| Model | " + " | ".join(cats) + " |")
print("| --- |" + " ---: |" * len(cats))
for m in report["models"]:
    cells = [pc(m["by_category"][c]["cross_substitution"], 0) if c in m["by_category"] else "—"
             for c in cats]
    print(f"| {m['meta']['model']} | " + " | ".join(cells) + " |")

print("\n\nCONDITION MEANS (Quebec-origin drift)\n")
conds = ["baseline", "canadian", "metropolitan", "proofread"]
print("| Model | " + " | ".join(conds) + " |")
print("| --- |" + " ---: |" * len(conds))
for m in report["models"]:
    cells = [pc(m["by_condition"][c]["qc"]["cross_substitution"], 0)
             if c in m["by_condition"] else "—" for c in conds]
    print(f"| {m['meta']['model']} | " + " | ".join(cells) + " |")

print("\n\nNOTABLE FALSE CORRECTIONS (proofread condition)\n")
for m in report["models"]:
    subs = [(f["test_id"], s["from"], s["to"], f["input"], f["output"])
            for f in m["failures"] if f["condition"] == "proofread"
            for s in f["substitutions"]]
    print(f"-- {m['meta']['model']} ({len(subs)} substitutions)")
    for tid, a, b, src, out in subs[:8]:
        print(f"   {tid}: {a} -> {b}")

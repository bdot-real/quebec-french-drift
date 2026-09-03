"""Scorecard construction and rendering.

The components stay visible. A single composite number can hide exactly the
failure the experiment is trying to surface, so the report leads with the
per-condition breakdown and the worst individual failures, not an average.
"""

from collections import defaultdict
from math import comb
from statistics import mean

CONDITION_ORDER = ["baseline", "canadian", "metropolitan", "proofread"]
CATEGORY_ORDER = ["lexical", "terminology", "semantic", "register", "grammar"]


def _mean(values):
    vals = [v for v in values if v is not None]
    return mean(vals) if vals else None


def _pct(value, width=6):
    return f"{value*100:>{width}.1f}%" if value is not None else " " * (width - 1) + "-"


def _agg(rows):
    ok = [r for r in rows if r.get("compliant", True)]
    return {
        "n": len(rows),
        "n_compliant": len(ok),
        "noncompliant": _mean(float(not r.get("compliant", True)) for r in rows),
        "source_retention": _mean(r["source_retention"] for r in rows),
        "cross_substitution": _mean(r["cross_substitution_rate"] for r in rows),
        "protected_loss": _mean(r["protected_term_loss"] for r in rows),
        "unchanged": _mean(float(r["unchanged"]) for r in rows),
        # Same numbers with void cells (the model answered instead of rewriting)
        # removed. Reported alongside, never silently substituted.
        "cross_substitution_compliant": _mean(r["cross_substitution_rate"] for r in ok),
        "source_retention_compliant": _mean(r["source_retention"] for r in ok),
    }


def _judge_agg(rows):
    judged = [r["judge"] for r in rows if isinstance(r.get("judge"), dict)
              and "judge_error" not in r["judge"]]
    if not judged:
        return None
    keys = ("meaning_preserved", "target_naturalness", "regional_usage_preserved",
            "variety_shift", "unnecessary_correction")
    return {"n": len(judged), **{k: _mean(j.get(k) for j in judged) for k in keys}}


def build_report(runs, tests=None):
    report = {"models": [], "attractor": {}, "matched_attractor": {}}
    tests = tests or {}
    for run in runs:
        rows = run["results"]
        qc = [r for r in rows if r["variety"] == "qc"]
        fr = [r for r in rows if r["variety"] == "fr"]

        by_condition = {}
        for cond in CONDITION_ORDER:
            c_qc = [r for r in qc if r["condition"] == cond]
            c_fr = [r for r in fr if r["condition"] == cond]
            if not c_qc and not c_fr:
                continue
            by_condition[cond] = {
                "qc": _agg(c_qc), "fr": _agg(c_fr),
                "judge_qc": _judge_agg(c_qc),
            }

        by_category = {}
        for cat in CATEGORY_ORDER:
            c_rows = [r for r in qc if r["category"] == cat and r["condition"] == "baseline"]
            if c_rows:
                by_category[cat] = _agg(c_rows)

        # Worst failures: valid Quebec forms the proofreader "corrected", then
        # the largest baseline drift. These examples are more useful than any
        # aggregate.
        failures = []
        for r in qc:
            if r["condition"] == "proofread" and (r["protected_term_loss"] or 0) > 0:
                failures.append({**_slim(r), "kind": "false_correction"})
        for r in qc:
            if r["condition"] == "baseline" and (r["cross_substitution_rate"] or 0) > 0:
                failures.append({**_slim(r), "kind": "baseline_drift"})
        failures.sort(key=lambda f: (-(f["protected_term_loss"] or 0),
                                     -(f["cross_substitution_rate"] or 0)))

        leaks = sum(1 for r in rows if r.get("suspect_reasoning_leak"))
        report["models"].append({
            "meta": run["meta"],
            "by_condition": by_condition,
            "by_category": by_category,
            "failures": failures,
            "n_results": len(rows),
            "suspect_reasoning_leaks": leaks,
            "scorecard": _scorecard(by_condition),
            "positive_control": _positive_control(by_condition),
        })
        if tests:
            matched = _matched_attractor(run, tests)
            if matched:
                report["matched_attractor"][run["meta"]["model"]] = matched

    report["attractor"] = _attractor(report["models"])
    return report


def _slim(r):
    return {k: r[k] for k in ("test_id", "category", "condition", "input", "output",
                              "substitutions", "protected_term_loss",
                              "cross_substitution_rate")}


def _scorecard(by_condition):
    """Headline numbers, all mechanical, all traceable to a single condition."""
    base = by_condition.get("baseline", {}).get("qc") or {}
    ca = by_condition.get("canadian", {}).get("qc") or {}
    pf = by_condition.get("proofread", {}).get("qc") or {}
    return {
        "CLR_baseline": base.get("source_retention"),
        "MDR_baseline": base.get("cross_substitution"),
        "CLR_prompted": ca.get("source_retention"),
        "MDR_prompted": ca.get("cross_substitution"),
        "QFCR_proofread": pf.get("protected_loss"),
        "unchanged_proofread": pf.get("unchanged"),
        "prompt_recovery": (
            None if base.get("cross_substitution") is None or ca.get("cross_substitution") is None
            else base["cross_substitution"] - ca["cross_substitution"]),
    }


def _sign_test(n_qc_higher, n_fr_higher):
    """Two-sided exact binomial test on discordant pairs (McNemar, exact form).

    The null hypothesis is that a pair is equally likely to drift more on its
    Quebec side as on its France side. Concordant pairs -- both drifted the same
    amount, including both zero -- carry no directional information and are
    excluded, which is what makes this McNemar rather than a plain binomial on
    all pairs.
    """
    n = n_qc_higher + n_fr_higher
    if n == 0:
        return None
    k = min(n_qc_higher, n_fr_higher)
    tail = sum(comb(n, i) for i in range(k + 1)) / (2 ** n)
    return {"n_discordant": n, "p_value": min(1.0, 2 * tail)}


def _matched_attractor(run, tests):
    """The §23 experiment on matched content.

    The all-items asymmetry compares 44 Quebec items against 14 France items --
    two different sets. Each control item names its Quebec counterpart, so the
    same measure can be run on 14 sentence pairs that differ only in variety.
    That is what turns "Quebec drifts more" into a claim about the same content.
    """
    pairs = [(t["counterpart"], t["id"]) for t in tests.values() if t.get("counterpart")]
    by_key = {(r["test_id"], r["condition"]): r for r in run["results"]}
    qc_rates, fr_rates, n_void = [], [], 0
    for qc_id, fr_id in pairs:
        qc_row, fr_row = by_key.get((qc_id, "baseline")), by_key.get((fr_id, "baseline"))
        if not qc_row or not fr_row:
            continue
        if not (qc_row.get("compliant", True) and fr_row.get("compliant", True)):
            n_void += 1
            continue
        if qc_row["cross_substitution_rate"] is None or fr_row["cross_substitution_rate"] is None:
            continue
        qc_rates.append(qc_row["cross_substitution_rate"])
        fr_rates.append(fr_row["cross_substitution_rate"])
    if not qc_rates:
        return None
    qc_mean, fr_mean = mean(qc_rates), mean(fr_rates)
    qc_higher = sum(q > f for q, f in zip(qc_rates, fr_rates))
    fr_higher = sum(f > q for q, f in zip(qc_rates, fr_rates))
    return {"n_pairs": len(qc_rates), "n_void_pairs": n_void,
            "qc_to_fr_drift": qc_mean, "fr_to_qc_drift": fr_mean,
            "asymmetry": qc_mean - fr_mean,
            "pairs_qc_higher": qc_higher, "pairs_fr_higher": fr_higher,
            "pairs_tied": len(qc_rates) - qc_higher - fr_higher,
            "sign_test": _sign_test(qc_higher, fr_higher)}


def _positive_control(by_condition):
    """The France-targeted prompt should maximize Quebec->France drift.

    When it does not, the model's numbers are either instruction-following
    noise or already at their drift ceiling under the baseline -- and a reader
    cannot tell which without being told the control failed.
    """
    base = (by_condition.get("baseline") or {}).get("qc") or {}
    metro = (by_condition.get("metropolitan") or {}).get("qc") or {}
    b, m = base.get("cross_substitution"), metro.get("cross_substitution")
    if b is None or m is None:
        return None
    return {"baseline_drift": b, "metropolitan_drift": m, "margin": m - b, "passed": m > b}


def _attractor(models):
    """The central question: under a prompt that names no variety, do BOTH
    varieties move toward Metropolitan French, or only the Quebec one?

    Symmetric drift means the model is simply rewriting. Asymmetric drift --
    Quebec inputs moving and France inputs staying put -- means "generic
    French" is not generic.
    """
    out = {}
    for m in models:
        base = m["by_condition"].get("baseline")
        if not base:
            continue
        qc_drift = base["qc"]["cross_substitution"]
        fr_drift = base["fr"]["cross_substitution"]
        out[m["meta"]["model"]] = {
            "qc_to_fr_drift": qc_drift,
            "fr_to_qc_drift": fr_drift,
            "asymmetry": None if qc_drift is None or fr_drift is None else qc_drift - fr_drift,
            "qc_retention": base["qc"]["source_retention"],
            "fr_retention": base["fr"]["source_retention"],
        }
    return out


def render_markdown(report):
    lines = ["# Quebec French Dialect Drift Report", ""]

    for m in report["models"]:
        meta, card = m["meta"], m["scorecard"]
        lines += [
            f"## {meta['model']}", "",
            f"- run: `{meta['run_id']}`  ·  dataset `{meta['dataset_version']}`  "
            f"·  prompts `{meta['prompt_version']}`",
            "- " + ", ".join(
                f"{k} {v}" for k, v in meta["model_config"].items()
                if k not in ("model",)),
            f"- {m['n_results']} results  ·  judge: {meta.get('judge_model') or 'none'}",
        ]
        if m["suspect_reasoning_leaks"]:
            lines.append(f"- ⚠️  {m['suspect_reasoning_leaks']} outputs look like leaked "
                         f"reasoning — treat this model's scores as unreliable")
        lines += ["", "### Scorecard (Quebec-origin items)", "",
                  "| Metric | Value |", "| --- | ---: |",
                  f"| Canadian lexical retention — baseline (CLR) | {_pct(card['CLR_baseline'])} |",
                  f"| Metropolitan drift — baseline (MDR) | {_pct(card['MDR_baseline'])} |",
                  f"| Canadian lexical retention — Quebec prompt | {_pct(card['CLR_prompted'])} |",
                  f"| Metropolitan drift — Quebec prompt | {_pct(card['MDR_prompted'])} |",
                  f"| Quebec false correction — proofread (QFCR) | {_pct(card['QFCR_proofread'])} |",
                  f"| — of which the model left the text untouched | {_pct(card['unchanged_proofread'])} |",
                  f"| Drift recovered by prompting | {_pct(card['prompt_recovery'])} |",
                  "",
                  "QFCR and *untouched* are entangled: a model that declines to edit "
                  "anything scores a perfect false-correction rate. Read them together.",
                  ""]

        pc = m["positive_control"]
        if pc is not None:
            verdict = ("**passed**" if pc["passed"] else "**FAILED**")
            lines += [f"### Positive control: {verdict}", "",
                      f"The France-targeted prompt should drive more Quebec→France drift "
                      f"than saying nothing. Baseline {_pct(pc['baseline_drift'],0)}, "
                      f"France-targeted {_pct(pc['metropolitan_drift'],0)} "
                      f"(margin {pc['margin']*100:+.1f} pts).", ""]
            if not pc["passed"]:
                lines += ["> Naming France as the audience bought nothing over naming no "
                          "audience at all. That is either an instruction-following "
                          "failure — in which case this model's conditions are not "
                          "cleanly separated — or baseline drift is already at the "
                          "model's ceiling because its default French *is* France "
                          "French. This run cannot distinguish the two.", ""]

        lines += ["### By condition", "",
                  "| Condition | QC retention | QC drift | QC drift (valid cells) | "
                  "QC protected loss | FR retention | FR drift | unchanged | void cells |",
                  "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
        for cond, agg in m["by_condition"].items():
            lines.append(
                f"| {cond} | {_pct(agg['qc']['source_retention'])} | "
                f"{_pct(agg['qc']['cross_substitution'])} | "
                f"{_pct(agg['qc']['cross_substitution_compliant'])} | "
                f"{_pct(agg['qc']['protected_loss'])} | "
                f"{_pct(agg['fr']['source_retention'])} | "
                f"{_pct(agg['fr']['cross_substitution'])} | "
                f"{_pct(agg['qc']['unchanged'])} | "
                f"{_pct(agg['qc']['noncompliant'])} |")
        lines += ["",
                  "*Void cells* are outputs where the model did not perform the rewrite "
                  "at all — it answered the sentence, or replied at a wildly different "
                  "length. Those score as total drift for the wrong reason, so the "
                  "*valid cells* column repeats the drift measure with them removed. "
                  "They are excluded, never silently dropped.", ""]

        if m["by_category"]:
            lines += ["### Baseline drift by category (Quebec-origin)", "",
                      "| Category | n | Retention | Drift |", "| --- | ---: | ---: | ---: |"]
            for cat, agg in sorted(m["by_category"].items(),
                                   key=lambda kv: -(kv[1]["cross_substitution"] or 0)):
                lines.append(f"| {cat} | {agg['n']} | {_pct(agg['source_retention'])} | "
                             f"{_pct(agg['cross_substitution'])} |")
            lines.append("")

        judged = [(c, a["judge_qc"]) for c, a in m["by_condition"].items() if a["judge_qc"]]
        if judged:
            lines += ["### Judge scores — illustrative only", "",
                      "A local 8-30B model is a weak authority on Quebec French, and the "
                      "sample below is small and uneven across models. These numbers "
                      "illustrate the failure modes; they do not rank the models. The "
                      "mechanical metrics above are the headline.", "",
                      "| Condition | n | meaning | QC naturalness | regional usage | "
                      "variety shift | unnecessary correction |",
                      "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
            for cond, j in judged:
                fmt = lambda v: f"{v:.2f}" if v is not None else "-"
                lines.append(f"| {cond} | {j['n']} | {fmt(j['meaning_preserved'])} | "
                             f"{fmt(j['target_naturalness'])} | "
                             f"{fmt(j['regional_usage_preserved'])} | "
                             f"{fmt(j['variety_shift'])} | "
                             f"{fmt(j['unnecessary_correction'])} |")
            lines.append("")

        if m["failures"]:
            lines += ["### Worst failures", ""]
            for f in m["failures"][:10]:
                subs = ", ".join(f"{s['from']} → {s['to']}" for s in f["substitutions"])
                lines += [f"**{f['test_id']}** ({f['category']}, {f['condition']}, {f['kind']})"
                          f"{' — ' + subs if subs else ''}", "",
                          f"> in:  {f['input']}", ">",
                          f"> out: {f['output']}", ""]

    if report["attractor"]:
        lines += ["## Is \"generic French\" actually generic?", "",
                  "Under the baseline prompt, which names no variety. Symmetric drift means "
                  "the model is just rewriting; asymmetric drift means its default French has "
                  "a centre of gravity.", "",
                  "| Model | QC→FR drift | FR→QC drift | asymmetry |",
                  "| --- | ---: | ---: | ---: |"]
        for name, a in report["attractor"].items():
            lines.append(f"| {name} | {_pct(a['qc_to_fr_drift'])} | "
                         f"{_pct(a['fr_to_qc_drift'])} | {_pct(a['asymmetry'])} |")
        lines.append("")

    if report.get("matched_attractor"):
        lines += ["### Matched pairs", "",
                  "The table above compares 44 Quebec items against 14 France items — "
                  "two different sets. Each control item names its Quebec counterpart, so "
                  "the same measure runs on sentence pairs that differ only in variety. "
                  "Void cells are excluded from both arms of a pair.", "",
                  "| Model | pairs | QC→FR drift | FR→QC drift | asymmetry | "
                  "QC higher | FR higher | tied | p (McNemar) |",
                  "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
        for name, a in report["matched_attractor"].items():
            st = a.get("sign_test")
            p_txt = "-" if st is None else (
                "< 0.001" if st["p_value"] < 0.001 else f"{st['p_value']:.3f}")
            lines.append(f"| {name} | {a['n_pairs']} | {_pct(a['qc_to_fr_drift'])} | "
                         f"{_pct(a['fr_to_qc_drift'])} | {_pct(a['asymmetry'])} | "
                         f"{a['pairs_qc_higher']} | {a['pairs_fr_higher']} | "
                         f"{a['pairs_tied']} | {p_txt} |")
        lines += ["",
                  "*p* is a two-sided exact McNemar (sign) test on the discordant pairs — "
                  "those where one side drifted more than the other. Tied pairs, including "
                  "pairs where neither side drifted, carry no directional information and "
                  "are excluded from the test but shown for context.", ""]
    return "\n".join(lines)

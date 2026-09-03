#!/usr/bin/env python3
"""Quebec-French dialect drift harness.

Usage:
    python3 run_experiment.py run   --models llama3.1:8b qwen2.5:14b-instruct
    python3 run_experiment.py judge --judge qwen2.5:14b-instruct
    python3 run_experiment.py report
    python3 run_experiment.py human --sample 120
"""

import argparse
import csv
import json
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from src.dataset import load_dataset, load_prompts
from src.judge import judge_output
from src.metrics import score_output
from src.models import build_model
from src.report import build_report, render_markdown

DATASET_VERSION = "0.2.0"
PROMPT_VERSION = "1.0"
RAW_DIR = Path("results/raw")


def _safe(name):
    return name.replace(":", "_").replace("/", "_")


def run_model(model, tests, prompts, resume=True, progress=True,
              on_cell=None, should_stop=None):
    """Run every (test x condition) cell for one model, resuming if interrupted."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / f"{_safe(model.name)}.json"

    by_id = {t["id"]: t for t in tests}
    done, results = set(), []
    if resume and path.exists():
        previous = json.loads(path.read_text(encoding="utf-8"))
        # A cached cell is only valid if it was produced from the *current* input.
        # Editing a test case must invalidate its outputs, or the resume path
        # silently serves answers to a question that is no longer being asked.
        stale = 0
        for r in previous.get("results", []):
            test = by_id.get(r["test_id"])
            if test is not None and r.get("input") != test["input"]:
                stale += 1
                continue
            results.append(r)
        done = {(r["test_id"], r["condition"]) for r in results}
        if stale:
            print(f"  discarded {stale} cells whose test case changed", file=sys.stderr)
        if done:
            print(f"  resuming: {len(done)} cells already recorded", file=sys.stderr)

    run_meta = {
        "run_id": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "model": model.name,
        "model_config": model.config,
        "dataset_version": DATASET_VERSION,
        "prompt_version": PROMPT_VERSION,
        "n_tests": len(tests),
        "conditions": list(prompts),
    }

    total = len(tests) * len(prompts)
    started = time.time()
    n = 0
    for test in tests:
        for condition, prompt in prompts.items():
            n += 1
            if should_stop is not None and should_stop():
                print("  stopped by request", file=sys.stderr)
                return {"meta": run_meta, "results": results, "stopped": True}
            if (test["id"], condition) in done:
                if on_cell:
                    on_cell(model.name, n, total, None)
                continue
            user = prompt["user"].format(text=test["input"])
            response = model.generate(prompt["system"], user)
            record = {
                "test_id": test["id"],
                "category": test["category"],
                "variety": test["variety"],
                "condition": condition,
                "model": model.name,
                "input": test["input"],
                "output": response.output,
                "raw_output": response.raw,
                "reasoning_stripped": response.reasoning_stripped,
                "suspect_reasoning_leak": response.suspect_reasoning_leak,
                "latency_s": response.latency_s,
                **score_output(test, response.output),
            }
            results.append(record)

            path.write_text(json.dumps({"meta": run_meta, "results": results},
                                       ensure_ascii=False, indent=2), encoding="utf-8")
            if on_cell:
                on_cell(model.name, n, total, record)
            if progress:
                rate = (time.time() - started) / max(len(results) - len(done), 1)
                left = (total - n) * rate
                print(f"  [{n}/{total}] {test['id']}/{condition} "
                      f"{response.latency_s:>5.1f}s  eta {left/60:.0f}m", file=sys.stderr)
    return {"meta": run_meta, "results": results}


def cmd_run(args):
    tests = load_dataset(args.data, ids=args.ids, categories=args.categories,
                         varieties=args.varieties)
    prompts = load_prompts(Path(args.data) / "prompts.json")
    if args.conditions:
        prompts = {k: v for k, v in prompts.items() if k in set(args.conditions)}
    print(f"{len(tests)} tests x {len(prompts)} conditions x {len(args.models)} models "
          f"= {len(tests)*len(prompts)*len(args.models)} calls", file=sys.stderr)

    # Model-outer, test-inner: concurrent requests across models thrash Ollama's
    # model swapping, so each model is loaded once and drained completely.
    for spec in args.models:
        print(f"\n=== {spec} ===", file=sys.stderr)
        model = build_model(spec, temperature=args.temperature, seed=args.seed,
                            num_ctx=args.num_ctx)
        run_model(model, tests, prompts, resume=not args.no_resume)
    cmd_report(args)


def cmd_judge(args):
    """Score existing outputs with a blind judge, in a single pass.

    Kept separate from generation on purpose: interleaving two models makes
    Ollama unload and reload weights on every call.
    """
    raws = sorted(RAW_DIR.glob("*.json"))
    if not raws:
        sys.exit("no results in results/raw -- run the experiment first")
    tests = {t["id"]: t for t in load_dataset(args.data)}
    judge = build_model(args.judge, num_ctx=args.num_ctx)

    for path in raws:
        run = json.loads(path.read_text(encoding="utf-8"))
        if run["meta"]["model"] == judge.name:
            print(f"WARNING: judging {judge.name} with itself measures its own "
                  f"linguistic preferences, not drift.", file=sys.stderr)
        run["meta"]["judge_model"] = judge.name
        rows = run["results"]
        todo = [r for r in rows if not isinstance(r.get("judge"), dict)]
        if args.conditions:
            todo = [r for r in todo if r["condition"] in set(args.conditions)]
        if args.sample:
            # Stratified by condition so no condition is judged more heavily
            # than another, and seeded so the sample is reproducible.
            rng = random.Random(args.seed)
            buckets = {}
            for r in todo:
                buckets.setdefault(r["condition"], []).append(r)
            per = max(1, args.sample // max(len(buckets), 1))
            todo = [r for rs in buckets.values()
                    for r in rng.sample(rs, min(per, len(rs)))]
        print(f"{path.name}: judging {len(todo)}/{len(rows)}", file=sys.stderr)
        for n, row in enumerate(todo, 1):
            row["judge"] = judge_output(judge, tests[row["test_id"]], row["output"])
            path.write_text(json.dumps(run, ensure_ascii=False, indent=2),
                            encoding="utf-8")
            if n % 10 == 0:
                print(f"  [{n}/{len(todo)}]", file=sys.stderr)
    cmd_report(args)


def cmd_report(args):
    raws = sorted(RAW_DIR.glob("*.json"))
    if not raws:
        sys.exit("no results in results/raw -- run the experiment first")
    runs = [json.loads(p.read_text(encoding="utf-8")) for p in raws]

    # Metrics are recomputed from the stored outputs on every report, so
    # fixing a matching bug never requires re-running the models.
    tests = {t["id"]: t for t in load_dataset(args.data)}
    for run in runs:
        for row in run["results"]:
            row.update(score_output(tests[row["test_id"]], row["output"]))

    report = build_report(runs, tests)

    out = Path("results/report")
    out.mkdir(parents=True, exist_ok=True)
    (out / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    markdown = render_markdown(report)
    (out / "report.md").write_text(markdown, encoding="utf-8")

    metrics_dir = Path("results/metrics")
    metrics_dir.mkdir(parents=True, exist_ok=True)
    for run in runs:
        rows = run["results"]
        path = metrics_dir / f"{_safe(run['meta']['model'])}.csv"
        cols = ["test_id", "category", "variety", "condition", "model", "input",
                "output", "source_retention", "cross_substitution_rate",
                "protected_term_loss", "unchanged", "suspect_reasoning_leak"]
        with path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
    print(markdown)
    print(f"\nwrote {out/'report.md'}, {out/'report.json'}, {metrics_dir}/*.csv",
          file=sys.stderr)


def cmd_human(args):
    """Emit a blind, shuffled CSV for a Quebec-French human panel.

    Condition and model are withheld from the rater and kept in a separate key
    file, so the panel rates the language rather than their expectations.
    """
    raws = sorted(RAW_DIR.glob("*.json"))
    if not raws:
        sys.exit("no results in results/raw -- run the experiment first")
    rows = [r for p in raws for r in json.loads(p.read_text(encoding="utf-8"))["results"]]

    rng = random.Random(args.seed)
    rng.shuffle(rows)
    rows = rows[: args.sample]

    out = Path("results/human")
    out.mkdir(parents=True, exist_ok=True)
    rated = ["meaning_preserved", "naturalness_qc", "regional_usage",
             "sounds_translated_from_france", "unnecessary_correction", "comments"]
    with (out / "human_eval.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["item", "context_variety", "input", "output"] + rated)
        for i, row in enumerate(rows, 1):
            writer.writerow([f"H{i:04d}", row["variety"], row["input"], row["output"]]
                            + [""] * len(rated))
    with (out / "human_eval_key.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["item", "test_id", "model", "condition"])
        for i, row in enumerate(rows, 1):
            writer.writerow([f"H{i:04d}", row["test_id"], row["model"], row["condition"]])
    print(f"wrote {out/'human_eval.csv'} ({len(rows)} rows) and the blinding key")


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data", default="data")
    sub = parser.add_subparsers(dest="cmd", required=True)

    run_p = sub.add_parser("run", help="run the experiment")
    run_p.add_argument("--models", nargs="+", required=True)
    run_p.add_argument("--conditions", nargs="*", default=None)
    run_p.add_argument("--categories", nargs="*", default=None)
    run_p.add_argument("--varieties", nargs="*", default=None)
    run_p.add_argument("--ids", nargs="*", default=None)
    run_p.add_argument("--temperature", type=float, default=0.0)
    run_p.add_argument("--seed", type=int, default=42)
    run_p.add_argument("--num-ctx", dest="num_ctx", type=int, default=8192)
    run_p.add_argument("--no-resume", action="store_true")
    run_p.set_defaults(func=cmd_run)

    jud_p = sub.add_parser("judge", help="blind-judge existing outputs in a separate pass")
    jud_p.add_argument("--judge", required=True, help="model spec for the blind judge")
    jud_p.add_argument("--num-ctx", dest="num_ctx", type=int, default=8192)
    jud_p.add_argument("--conditions", nargs="*", default=None)
    jud_p.add_argument("--sample", type=int, default=None,
                       help="judge at most N rows per model, stratified by condition")
    jud_p.add_argument("--seed", type=int, default=7)
    jud_p.set_defaults(func=cmd_judge)

    rep_p = sub.add_parser("report", help="rebuild the report from results/raw")
    rep_p.set_defaults(func=cmd_report)

    hum_p = sub.add_parser("human", help="emit a blind CSV for human raters")
    hum_p.add_argument("--sample", type=int, default=150)
    hum_p.add_argument("--seed", type=int, default=7)
    hum_p.set_defaults(func=cmd_human)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

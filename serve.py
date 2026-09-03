#!/usr/bin/env python3
"""Local control panel for the Quebec-French drift harness.

    python3 serve.py            # then open http://127.0.0.1:8765

Runs on the stdlib. It has to be local: the harness talks to a model server on
127.0.0.1, which a page hosted anywhere else cannot reach.

A full run is hundreds of model calls, so `POST /api/run` starts a background
thread and returns immediately; the UI polls `/api/status`. Because the runner
writes every cell to disk as it completes, closing the page or restarting the
server loses nothing -- the next run resumes from what is already recorded.
"""

import json
import random
import threading
import traceback
import urllib.error
from collections import deque
from datetime import datetime, timezone
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import run_experiment as harness
from src.dataset import load_dataset, load_prompts
from src.judge import judge_output
from src.metrics import score_output
from src.models import build_model, list_ollama_models, list_openai_models
from src.report import build_report, render_markdown

ROOT = Path(__file__).resolve().parent
WEB = ROOT / "web"

STATE = {
    "running": False,
    "phase": "idle",
    "models": [],
    "current_model": None,
    "done": 0,
    "total": 0,
    "started_at": None,
    "finished_at": None,
    "error": None,
    "stop_requested": False,
    "log": deque(maxlen=250),
}
LOCK = threading.Lock()


def log(message):
    with LOCK:
        STATE["log"].append({
            "t": datetime.now(timezone.utc).strftime("%H:%M:%S"),
            "message": message,
        })


def snapshot():
    with LOCK:
        return {**{k: v for k, v in STATE.items() if k != "log"},
                "log": list(STATE["log"])}


def _stop_requested():
    with LOCK:
        return STATE["stop_requested"]


def _run_job(cfg):
    """Generate, optionally judge, then always rebuild the report."""
    try:
        tests = load_dataset("data", categories=cfg.get("categories") or None,
                             varieties=cfg.get("varieties") or None)
        prompts = load_prompts("data/prompts.json")
        if cfg.get("conditions"):
            prompts = {k: v for k, v in prompts.items() if k in set(cfg["conditions"])}
        if not tests or not prompts:
            raise ValueError("that filter combination selects no work")

        specs = cfg["models"]
        per_model = len(tests) * len(prompts)
        with LOCK:
            STATE.update(models=specs, total=per_model * len(specs), done=0,
                         phase="generating")
        log(f"{len(tests)} tests x {len(prompts)} conditions x {len(specs)} models "
            f"= {per_model * len(specs)} cells")

        offset = 0

        def on_cell(model_name, n, total, record):
            with LOCK:
                STATE["done"] = offset + n
                STATE["current_model"] = model_name

        # Model-outer: interleaving models makes a local server unload and
        # reload weights on every call.
        for spec in specs:
            if _stop_requested():
                break
            log(f"running {spec}")
            model = build_model(spec, temperature=cfg.get("temperature", 0.0),
                                seed=cfg.get("seed", 42),
                                num_ctx=cfg.get("num_ctx", 8192),
                                base_url=cfg.get("base_url"),
                                api_key=cfg.get("api_key"))
            try:
                harness.run_model(model, tests, prompts, resume=cfg.get("resume", True),
                                  progress=False, on_cell=on_cell,
                                  should_stop=_stop_requested)
            finally:
                if hasattr(model, "unload"):
                    model.unload()
            offset += per_model

        judge_spec = cfg.get("judge")
        if judge_spec and not _stop_requested():
            with LOCK:
                STATE["phase"] = "judging"
            log(f"judging with {judge_spec}")
            _judge_pass(judge_spec, cfg, tests)

        with LOCK:
            STATE["phase"] = "reporting"
        _rebuild_report()
        log("stopped early" if _stop_requested() else "done")
    except Exception as exc:  # surfaced in the UI rather than only the console
        log(f"ERROR: {exc}")
        traceback.print_exc()
        with LOCK:
            STATE["error"] = str(exc)
    finally:
        with LOCK:
            STATE.update(running=False, phase="idle", current_model=None,
                         stop_requested=False,
                         finished_at=datetime.now(timezone.utc).isoformat(timespec="seconds"))


def _judge_pass(judge_spec, cfg, tests):
    judge = build_model(judge_spec, num_ctx=cfg.get("num_ctx", 8192),
                        base_url=cfg.get("base_url"), api_key=cfg.get("api_key"))
    unload_after = getattr(judge, "unload", None)
    by_id = {t["id"]: t for t in tests}
    limit = cfg.get("judge_sample") or 0
    for path in sorted(harness.RAW_DIR.glob("*.json")):
        if _stop_requested():
            return
        run = json.loads(path.read_text(encoding="utf-8"))
        if run["meta"]["model"] == judge.name:
            log(f"WARNING: {judge.name} is judging its own output")
        run["meta"]["judge_model"] = judge.name
        todo = [r for r in run["results"]
                if r["test_id"] in by_id and not isinstance(r.get("judge"), dict)]
        if limit:
            # Stratified by condition and seeded, matching the CLI: judging the
            # first N rows would judge one condition and call it a sample.
            rng = random.Random(cfg.get("seed", 7))
            buckets = {}
            for r in todo:
                buckets.setdefault(r["condition"], []).append(r)
            per = max(1, limit // max(len(buckets), 1))
            todo = [r for rows in buckets.values()
                    for r in rng.sample(rows, min(per, len(rows)))]
        log(f"{path.name}: judging {len(todo)} rows")
        for row in todo:
            if _stop_requested():
                return
            row["judge"] = judge_output(judge, by_id[row["test_id"]], row["output"])
            path.write_text(json.dumps(run, ensure_ascii=False, indent=2),
                            encoding="utf-8")
    if unload_after:
        unload_after()


def _rebuild_report():
    raws = sorted(harness.RAW_DIR.glob("*.json"))
    if not raws:
        return None
    runs = [json.loads(p.read_text(encoding="utf-8")) for p in raws]
    tests = {t["id"]: t for t in load_dataset("data")}
    for run in runs:
        # Rows for test cases that no longer exist are kept on disk but not
        # scored, so a removed test case cannot poison the aggregates.
        run["results"] = [r for r in run["results"] if r["test_id"] in tests]
        for row in run["results"]:
            row.update(score_output(tests[row["test_id"]], row["output"]))
    report = build_report(runs, tests)
    out = ROOT / "results" / "report"
    out.mkdir(parents=True, exist_ok=True)
    (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2),
                                     encoding="utf-8")
    (out / "report.md").write_text(render_markdown(report), encoding="utf-8")
    return report


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB), **kwargs)

    def log_message(self, fmt, *args):
        pass

    def _send(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        length = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(length) or b"{}")

    def do_GET(self):
        route = self.path.split("?", 1)[0]
        try:
            if route == "/api/dataset":
                return self._send(self._dataset())
            if route == "/api/models":
                return self._send(self._models())
            if route == "/api/status":
                return self._send(snapshot())
            if route == "/api/report":
                path = ROOT / "results" / "report" / "report.json"
                if not path.exists():
                    return self._send({"models": [], "attractor": {},
                                       "matched_attractor": {}})
                return self._send(json.loads(path.read_text(encoding="utf-8")))
        except Exception as exc:
            return self._send({"error": str(exc)}, 500)
        return super().do_GET()

    def do_POST(self):
        route = self.path.split("?", 1)[0]
        try:
            if route == "/api/run":
                return self._send(self._start(self._body()))
            if route == "/api/stop":
                with LOCK:
                    STATE["stop_requested"] = True
                log("stop requested")
                return self._send(snapshot())
            if route == "/api/report":
                return self._send(_rebuild_report() or {})
        except Exception as exc:
            return self._send({"error": str(exc)}, 500)
        self._send({"error": "not found"}, 404)

    # -- handlers ---------------------------------------------------------
    def _dataset(self):
        tests = load_dataset("data")
        prompts = load_prompts("data/prompts.json")
        categories = {}
        for t in tests:
            entry = categories.setdefault(t["category"], {"qc": 0, "fr": 0})
            entry[t["variety"]] += 1
        return {
            "n_tests": len(tests),
            "n_pairs": sum(1 for t in tests if t.get("counterpart")),
            "categories": categories,
            "conditions": {k: {"label": v.get("label", k), "system": v["system"]}
                           for k, v in prompts.items()},
        }

    def _models(self):
        from urllib.parse import parse_qs, urlparse
        q = parse_qs(urlparse(self.path).query)
        backend = (q.get("backend") or ["ollama"])[0]
        try:
            if backend == "ollama":
                host = (q.get("host") or ["http://127.0.0.1:11434"])[0]
                names = [n for n in list_ollama_models(host)
                         if not any(tag in n for tag in ("embed", "bge-"))]
                return {"backend": backend, "models": sorted(names)}
            base_url = (q.get("base_url") or ["http://127.0.0.1:8080/v1"])[0]
            api_key = (q.get("api_key") or [None])[0]
            names = list_openai_models(base_url, api_key)
            return {"backend": backend,
                    "models": sorted(f"openai:{n}" for n in names)}
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            return {"backend": backend, "models": [],
                    "error": f"could not reach the {backend} backend: {exc}"}

    def _start(self, cfg):
        with LOCK:
            if STATE["running"]:
                return {"error": "a run is already in progress", **snapshot()}
            if not cfg.get("models"):
                return {"error": "select at least one model"}
            STATE.update(running=True, phase="starting", error=None, done=0, total=0,
                         stop_requested=False, current_model=None, finished_at=None,
                         started_at=datetime.now(timezone.utc).isoformat(timespec="seconds"))
            STATE["log"].clear()
        threading.Thread(target=_run_job, args=(cfg,), daemon=True).start()
        return snapshot()


def main():
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--host", default="127.0.0.1")
    args = ap.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Quebec-French drift console -> http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nbye")


if __name__ == "__main__":
    main()

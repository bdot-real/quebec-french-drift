#!/usr/bin/env python3
"""Minimal OpenAI-compatible server for a local HuggingFace causal LM.

    .venv/bin/python scripts/serve_hf.py --model <path-or-repo> --name qc-croissant

Exists so a merged LoRA can be benchmarked without a GGUF conversion, through
the harness's existing `openai:` adapter:

    python3 run_experiment.py run --models openai:qc-croissant

Implements only what the harness calls: GET /v1/models and POST
/v1/chat/completions, non-streaming. Deliberately single-threaded — one model on
one machine, and concurrent generate() calls would just contend for the same
weights.
"""

import argparse
import json
import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.models import chat_stop_ids  # noqa: E402  shared with TransformersModel

STATE = {}


def build_prompt(tokenizer, messages):
    """Prefer the model's own chat template; fall back to a plain transcript."""
    if getattr(tokenizer, "chat_template", None):
        return tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True)
    parts = [f"{m['role']}: {m['content']}" for m in messages]
    return "\n".join(parts) + "\nassistant:"


def generate(messages, temperature, max_new_tokens, seed):
    tokenizer, model = STATE["tokenizer"], STATE["model"]
    prompt = build_prompt(tokenizer, messages)
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    if seed is not None:
        torch.manual_seed(seed)
    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=temperature > 0,
            temperature=temperature if temperature > 0 else None,
            top_p=0.95 if temperature > 0 else None,
            pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id,
            eos_token_id=STATE["stop_ids"],
        )
    # Only the continuation: echoing the prompt back would be scored as output.
    text = tokenizer.decode(out[0][inputs["input_ids"].shape[1]:],
                            skip_special_tokens=True)
    return text.strip()


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass

    def _send(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.rstrip("/").endswith("/models"):
            return self._send({"object": "list", "data": [
                {"id": STATE["name"], "object": "model", "owned_by": "local"}]})
        self._send({"error": "not found"}, 404)

    def do_POST(self):
        if not self.path.rstrip("/").endswith("/chat/completions"):
            return self._send({"error": "not found"}, 404)
        length = int(self.headers.get("Content-Length") or 0)
        req = json.loads(self.rfile.read(length) or b"{}")
        try:
            text = generate(
                req.get("messages", []),
                float(req.get("temperature", 0.0) or 0.0),
                int(req.get("max_tokens") or STATE["max_new_tokens"]),
                req.get("seed"),
            )
        except Exception as exc:  # surfaced as a normal error response
            return self._send({"error": {"message": str(exc)}}, 500)
        self._send({
            "id": f"chatcmpl-{int(time.time()*1000)}",
            "object": "chat.completion",
            "model": STATE["name"],
            "choices": [{"index": 0, "finish_reason": "stop",
                         "message": {"role": "assistant", "content": text}}],
        })


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--device", default="mps" if torch.backends.mps.is_available() else "cpu")
    ap.add_argument("--dtype", default="float16")
    ap.add_argument("--max-new-tokens", dest="max_new_tokens", type=int, default=256)
    args = ap.parse_args()

    print(f"loading {args.model} on {args.device}...", flush=True)
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(
        args.model, dtype=getattr(torch, args.dtype), low_cpu_mem_usage=True)
    model.to(args.device).eval()
    STATE.update(tokenizer=tokenizer, model=model, name=args.name,
                 max_new_tokens=args.max_new_tokens,
                 stop_ids=chat_stop_ids(tokenizer, model.generation_config))
    print(f"stop ids: {STATE['stop_ids']}", flush=True)
    print(f"chat template: {'yes' if getattr(tokenizer, 'chat_template', None) else 'NO (plain transcript fallback)'}",
          flush=True)
    print(f"serving '{args.name}' at http://127.0.0.1:{args.port}/v1", flush=True)
    HTTPServer(("127.0.0.1", args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Merge a PEFT/LoRA adapter into its base model and save the result.

    .venv/bin/python scripts/merge_lora.py <adapter-repo> <out-dir> [--base REPO]

The adapter's own `base_model_name_or_path` is used unless --base overrides it
(useful when the named base is gated and an identical ungated mirror exists --
which is a licensing decision, not a technical one).

Refuses to merge when the adapter ships its own tokenizer whose vocabulary
differs from the base: continued pre-training sometimes extends the tokenizer,
and loading the wrong one silently mistokenizes accented French, which would
look like a model quality result rather than a setup error.
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

import torch
from huggingface_hub import snapshot_download
from peft import PeftConfig, PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("adapter")
    ap.add_argument("out")
    ap.add_argument("--base", default=None)
    ap.add_argument("--dtype", default="float16")
    args = ap.parse_args()

    cfg = PeftConfig.from_pretrained(args.adapter)
    named_base = cfg.base_model_name_or_path
    base = args.base or named_base
    print(f"adapter    : {args.adapter}")
    print(f"named base : {named_base}")
    print(f"using base : {base}" + ("  (override)" if args.base else ""))

    adapter_dir = Path(snapshot_download(args.adapter))
    tok_file = adapter_dir / "tokenizer_config.json"

    dtype = getattr(torch, args.dtype)
    tokenizer = AutoTokenizer.from_pretrained(base)

    if tok_file.exists():
        # The adapter carries a tokenizer; only trust it if it really differs.
        adapter_tok = AutoTokenizer.from_pretrained(str(adapter_dir))
        if len(adapter_tok) != len(tokenizer):
            print(f"adapter tokenizer has {len(adapter_tok)} tokens, base has "
                  f"{len(tokenizer)} -- using the adapter's and resizing embeddings")
            tokenizer = adapter_tok
        else:
            print("adapter tokenizer matches the base vocabulary; using the base's")

    print("loading base weights...")
    model = AutoModelForCausalLM.from_pretrained(
        base, dtype=dtype, low_cpu_mem_usage=True, device_map="cpu")

    if model.get_input_embeddings().weight.shape[0] != len(tokenizer):
        print(f"resizing embeddings {model.get_input_embeddings().weight.shape[0]}"
              f" -> {len(tokenizer)}")
        model.resize_token_embeddings(len(tokenizer))

    print("applying adapter...")
    model = PeftModel.from_pretrained(model, args.adapter, dtype=dtype)

    # Sanity: a full-coverage LoRA must actually change the weights. A no-op
    # merge would produce a model identical to the base and a meaningless
    # "the adapter does nothing" result.
    probe = next(p for n, p in model.named_parameters() if "q_proj" in n and "lora" not in n)
    before = probe.detach().clone()

    print("merging...")
    model = model.merge_and_unload()

    after = next(p for n, p in model.named_parameters() if "q_proj" in n)
    delta = (after.detach().float() - before.float()).abs().max().item()
    print(f"max weight delta on a probed q_proj: {delta:.6f}")
    if delta == 0.0:
        sys.exit("merge changed nothing -- adapter did not apply; refusing to save")

    out = Path(args.out)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    print(f"saving to {out}...")
    model.save_pretrained(out, safe_serialization=True)
    tokenizer.save_pretrained(out)
    (out / "MERGE_INFO.json").write_text(json.dumps({
        "adapter": args.adapter, "named_base": named_base, "base_used": base,
        "dtype": args.dtype, "max_probe_delta": delta,
    }, indent=2))
    print("done")


if __name__ == "__main__":
    main()

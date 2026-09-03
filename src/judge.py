"""Blind LLM judge for the questions lexical matching cannot reach.

Mechanical metrics cannot see "this is technically correct, but nobody in
Quebec would write it this way". The judge can -- but a local 8-30B model is a
weak Quebec-French authority, so judge scores are reported as provisional and
the mechanical metrics stay the headline.

Two safeguards from the design doc are enforced here: the judge never sees the
model name or the prompt condition, and the judge should not be the model under
test (the runner warns when it is).
"""

import json
import re

JUDGE_SYSTEM = (
    "You are a careful evaluator of French-language text. "
    "You answer only with a single JSON object and no other text."
)

# Braces in the JSON skeleton are doubled so that .format() leaves them alone.
JUDGE_TEMPLATE = """You are evaluating a rewritten French text.

The target variety is {target_label}.

Do NOT judge whether one variety of French is better than another.
Judge only whether the CANDIDATE appropriately preserves the variety, meaning
and register of the ORIGINAL.

ORIGINAL:
{original}

CANDIDATE:
{candidate}

Return JSON only, in exactly this shape:

{{
  "meaning_preserved": 1,
  "target_naturalness": 1,
  "regional_usage_preserved": 1,
  "variety_shift": 1,
  "unnecessary_correction": 1,
  "reason": "one short sentence"
}}

Scales (integers 1-5):
meaning_preserved:        1 = meaning substantially changed, 5 = fully preserved
target_naturalness:       1 = clearly unnatural for the target variety, 5 = fully natural
regional_usage_preserved: 1 = regional usage largely removed, 5 = appropriately preserved
variety_shift:            1 = no shift toward the other variety, 5 = strongly shifted
unnecessary_correction:   1 = no unnecessary change, 5 = extensively rewrote valid usage
"""

FIELDS = ("meaning_preserved", "target_naturalness", "regional_usage_preserved",
          "variety_shift", "unnecessary_correction")

TARGET_LABEL = {"qc": "Quebec French", "fr": "Metropolitan (France) French"}


def build_judge_prompt(test, candidate):
    return JUDGE_TEMPLATE.format(
        target_label=TARGET_LABEL[test["variety"]],
        original=test["input"],
        candidate=candidate,
    )


_JSON_OBJ = re.compile(r"\{.*\}", re.DOTALL)


def parse_judge(text):
    """Best-effort JSON extraction; returns None rather than guessing."""
    match = _JSON_OBJ.search(text or "")
    if not match:
        return None
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
    out = {}
    for field in FIELDS:
        value = data.get(field)
        if isinstance(value, (int, float)) and 1 <= value <= 5:
            out[field] = int(value)
        else:
            out[field] = None
    out["reason"] = str(data.get("reason", ""))[:300]
    return out


def judge_output(judge_model, test, candidate):
    prompt = build_judge_prompt(test, candidate)
    response = judge_model.generate(JUDGE_SYSTEM, prompt)
    scores = parse_judge(response.output) or parse_judge(response.raw)
    if scores is None:
        return {"judge_error": "unparseable", "judge_raw": response.raw[:400]}
    scores["judge_model"] = judge_model.name
    return scores

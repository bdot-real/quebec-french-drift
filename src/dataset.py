"""Dataset loading and validation.

Test cases are data, not code: adding a category means adding a JSONL file.
"""

import json
from pathlib import Path

REQUIRED = ("id", "category", "variety", "input")
VALID_VARIETIES = ("qc", "fr")
VALID_RELATIONS = ("equivalent", "preference", "semantic_diff")


def load_jsonl(path):
    path = Path(path)
    out = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{lineno}: {exc}") from exc
    return out


def validate(test, source=""):
    for key in REQUIRED:
        if key not in test:
            raise ValueError(f"{source}: test {test.get('id', '?')} missing '{key}'")
    if test["variety"] not in VALID_VARIETIES:
        raise ValueError(f"{source}: {test['id']} has variety={test['variety']!r}")
    for pair in test.get("pairs", []):
        if "qc" not in pair or "fr" not in pair:
            raise ValueError(f"{source}: {test['id']} has a pair missing 'qc' or 'fr'")
        if pair.get("relation", "preference") not in VALID_RELATIONS:
            raise ValueError(f"{source}: {test['id']} bad relation {pair.get('relation')!r}")
    return test


def load_dataset(directory="data", ids=None, categories=None, varieties=None):
    directory = Path(directory)
    tests, seen = [], set()
    for path in sorted(directory.glob("*.jsonl")):
        for test in load_jsonl(path):
            validate(test, source=path.name)
            if test["id"] in seen:
                raise ValueError(f"duplicate test id {test['id']} in {path.name}")
            seen.add(test["id"])
            test.setdefault("source_file", path.name)
            tests.append(test)

    if ids:
        tests = [t for t in tests if t["id"] in set(ids)]
    if categories:
        tests = [t for t in tests if t["category"] in set(categories)]
    if varieties:
        tests = [t for t in tests if t["variety"] in set(varieties)]
    return tests


def load_prompts(path="data/prompts.json"):
    return json.loads(Path(path).read_text(encoding="utf-8"))

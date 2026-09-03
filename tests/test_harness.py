"""Self-tests. Run: python3 tests/test_harness.py"""
import sys, unicodedata
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.textnorm import contains_term, contains_any
from src.metrics import score_output
from src.dataset import load_dataset, load_prompts
from src.judge import build_judge_prompt, parse_judge
from src.models import strip_reasoning, looks_like_untagged_reasoning, _strip_wrappers

def check(cond, label):
    if not cond:
        raise AssertionError(label)

# --- matching -------------------------------------------------------------
MATCH = [
    (unicodedata.normalize("NFD", "Le déjeuner est prêt."), "déjeuner", True),   # NFD input
    ("l’édifice est fermé", "l'édifice", True),                                  # curly apostrophe
    ("derrière l’édifice", "édifice", True),                                     # elision boundary
    ("Nous dînerons tard.", "dîner", False),                                     # not inside a word
    ("Envoyez un e-mail.", "mail", False),                                       # hyphen is a boundary
    ("Envoyez un mail.", "mail", True),
    ("des téléphones intelligents", "téléphone intelligent", True),              # plural tolerance
    ("faire vos magasinages", "magasinage", True),
    ("supprimez les courriels indésirables", "pourriel", False),
]
for text, term, expected in MATCH:
    check(contains_term(text, term) is expected, f"match {term!r} in {text!r}")

# --- metrics are direction-aware -----------------------------------------
qc = {"id": "T1", "category": "lexical", "variety": "qc",
      "input": "Envoyez-nous un courriel.",
      "pairs": [{"qc": "courriel", "fr": ["e-mail", "email"], "relation": "preference"}],
      "protected": ["courriel"]}
kept = score_output(qc, "Envoyez-nous un courriel.")
check(kept["source_retention"] == 1.0 and kept["cross_substitution_rate"] == 0.0, "qc kept")
check(kept["protected_term_loss"] == 0.0 and kept["unchanged"], "qc unchanged")

drifted = score_output(qc, "Envoyez-nous un e-mail.")
check(drifted["source_retention"] == 0.0, "qc retention on drift")
check(drifted["cross_substitution_rate"] == 1.0, "qc drift detected")
check(drifted["substitutions"][0]["to"] == "e-mail", "substitution recorded")

# Dropping a term without substituting is absence, not drift.
dropped = score_output(qc, "Écrivez-nous.")
check(dropped["cross_substitution_rate"] == 0.0, "absence is not substitution")

fr = dict(qc, id="T2", variety="fr", input="Envoyez-nous un e-mail.", protected=["e-mail"])
mirror = score_output(fr, "Envoyez-nous un courriel.")
check(mirror["cross_substitution_rate"] == 1.0, "fr->qc mirror drift detected")
check(score_output(fr, "Envoyez-nous un e-mail.")["cross_substitution_rate"] == 0.0, "fr kept")

# --- judge prompt survives .format() on literal JSON braces ---------------
prompt = build_judge_prompt({"variety": "qc", "input": "A"}, "B")
check("Quebec French" in prompt and '"meaning_preserved": 1' in prompt, "judge prompt")
parsed = parse_judge('noise {"meaning_preserved":5,"target_naturalness":4,'
                     '"regional_usage_preserved":3,"variety_shift":2,'
                     '"unnecessary_correction":1,"reason":"ok"} tail')
check(parsed["meaning_preserved"] == 5 and parsed["variety_shift"] == 2, "judge parse")
check(parse_judge("not json at all") is None, "judge parse failure is explicit")

# --- reasoning and wrapper handling --------------------------------------
clean, was = strip_reasoning("<think>weighing courriel vs e-mail</think>\nLe courriel.")
check(clean == "Le courriel." and was, "tagged reasoning stripped")
check(strip_reasoning("Le courriel.") == ("Le courriel.", False), "clean text untouched")
check(looks_like_untagged_reasoning("Okay, the user wants me to rewrite"), "leak flagged")
check(not looks_like_untagged_reasoning("Le stationnement est ouvert."), "no false leak flag")
check(_strip_wrappers("Voici le texte réécrit :\nLe courriel.") == "Le courriel.", "lead-in")
check(_strip_wrappers("```\nLe courriel.\n```") == "Le courriel.", "code fence")

# --- dataset integrity ----------------------------------------------------
tests = load_dataset("data")
check(len(tests) >= 50, "dataset loaded")
check({t["variety"] for t in tests} == {"qc", "fr"}, "both varieties present")
for t in tests:
    for term in t.get("protected", []):
        check(contains_any(t["input"], term),
              f"{t['id']}: protected term {term!r} is not in its own input")
    for pair in t.get("pairs", []):
        src = pair[t["variety"]]
        check(any(contains_term(t["input"], v) for v in ([src] if isinstance(src, str) else src)),
              f"{t['id']}: source-variety form {src!r} is not in its own input")
# Every Quebec item must have exactly one France counterpart: the matched-pair
# arm is the load-bearing comparison, and a silently unpaired item weakens it.
qc_ids = {t["id"] for t in tests if t["variety"] == "qc"}
counterparts = [t["counterpart"] for t in tests if t.get("counterpart")]
check(len(counterparts) == len(set(counterparts)), "a Quebec item is claimed twice")
missing = qc_ids - set(counterparts)
check(not missing, f"Quebec items with no France counterpart: {sorted(missing)}")
dangling = set(counterparts) - qc_ids
check(not dangling, f"counterparts naming no Quebec item: {sorted(dangling)}")

prompts = load_prompts("data/prompts.json")
for name, p in prompts.items():
    check("{text}" in p["user"], f"prompt {name} has no {{text}} slot")

print(f"all self-tests passed ({len(tests)} test cases, {len(counterparts)} matched pairs, {len(prompts)} conditions)")

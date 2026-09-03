"""Mechanical drift metrics.

These are deliberately dumb. An LLM judge that decides "parking" and
"stationnement" are equivalent would hide exactly the substitution we are
trying to count, so substitutions are detected mechanically first and only
then handed to a judge for the harder questions.

Every metric is direction-aware. A test case declares its source `variety`
("qc" or "fr"); the metric reports whether the *source* variety survived and
whether it was replaced by the *other* variety. Running the identical measure
on Quebec-origin and France-origin inputs under the same prompt is what makes
the "which French is the default?" question answerable.
"""

from .textnorm import as_variants, contains_any, contains_term


def _sides(test):
    """Return (source_key, other_key) for a test case."""
    return ("qc", "fr") if test["variety"] == "qc" else ("fr", "qc")


def source_retention(test, output):
    """Fraction of the input's own-variety forms still present in the output.

    Named Canadian Lexical Retention (CLR) for qc-origin items.
    Returns None when the item declares no pairs (nothing to measure).
    """
    src, _ = _sides(test)
    pairs = test.get("pairs", [])
    if not pairs:
        return None
    kept = sum(contains_any(output, p[src]) for p in pairs)
    return kept / len(pairs)


def cross_substitution(test, output):
    """Own-variety form gone AND other-variety form present.

    For qc-origin items this is the Metropolitan Drift Rate (MDR).
    For fr-origin items it is the mirror-image quebecisation rate.
    """
    src, other = _sides(test)
    pairs = test.get("pairs", [])
    subs = []
    for pair in pairs:
        src_forms, other_forms = as_variants(pair[src]), as_variants(pair[other])
        if not contains_any(output, src_forms) and contains_any(output, other_forms):
            hit = next(f for f in other_forms if contains_term(output, f))
            subs.append({
                "from": src_forms[0],
                "to": hit,
                "relation": pair.get("relation", "preference"),
            })
    return {"rate": len(subs) / len(pairs) if pairs else None, "substitutions": subs}


def protected_term_loss(test, output):
    """Fraction of explicitly protected forms that disappeared from the output.

    `protected` holds forms that should survive any faithful rewrite, whatever
    else changes. Under the `proofread` condition this is the Quebec False
    Correction Rate (QFCR): valid regional forms a proofreader "corrected".

    An entry may be a list of accepted surface variants, for terms whose
    faithful rewrite legitimately changes inflection ("souperons" -> "souper").
    Counting a conjugation change as a lost regional form would fill the
    false-correction rate with grammatical noise.
    """
    protected = test.get("protected", [])
    if not protected:
        return None
    lost = sum(not contains_any(output, entry) for entry in protected)
    return lost / len(protected)


def unchanged(test, output):
    """True when the model returned the input essentially verbatim.

    Useful context: a high retention score means little if the model simply
    echoed the prompt instead of rewriting it.
    """
    from .textnorm import normalize
    return normalize(output) == normalize(test["input"])


def score_output(test, output):
    sub = cross_substitution(test, output)
    compliance = task_compliance(test, output)
    return {
        "compliant": compliance["compliant"],
        "noncompliance_reason": compliance["reason"],
        "source_retention": source_retention(test, output),
        "cross_substitution_rate": sub["rate"],
        "substitutions": sub["substitutions"],
        "protected_term_loss": protected_term_loss(test, output),
        "unchanged": unchanged(test, output),
    }


# Words too common to signal that the model actually engaged with the input.
_STOP = {
    "vous", "nous", "avec", "pour", "dans", "votre", "notre", "leur", "leurs",
    "est", "sont", "être", "avoir", "cette", "celui", "celle", "plus", "tout",
    "tous", "toute", "toutes", "elle", "elles", "ils", "mais", "donc", "que",
    "qui", "les", "des", "une", "aux", "par", "sur", "sans", "chez",
}


def task_compliance(test, output):
    """Did the model perform the requested rewrite at all?

    Some cells are not drift measurements but void cells: informal spoken-register
    items read as conversational prompts, and a model that *answers* the question
    instead of rewriting it scores as total drift for the wrong reason. Two cheap
    signals catch it: a wildly different length, or no substantive word in common
    with the input.
    """
    from .textnorm import normalize
    src, out = normalize(test["input"]), normalize(output)
    if not out:
        return {"compliant": False, "reason": "empty"}

    ratio = len(out) / max(len(src), 1)
    if not 0.5 <= ratio <= 2.0:
        return {"compliant": False, "reason": f"length_ratio={ratio:.2f}"}

    def content(text):
        return {w.strip(".,;:!?…\"'()") for w in text.split()
                if len(w) >= 4 and w not in _STOP}

    src_words = content(src)
    if src_words and not (src_words & content(out)):
        return {"compliant": False, "reason": "no_shared_content_word"}
    return {"compliant": True, "reason": None}

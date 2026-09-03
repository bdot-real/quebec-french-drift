"""Unicode-safe normalisation and term matching.

Everything here exists because naive `term.lower() in output.lower()` silently
loses real hits on French text:

* macOS and many editors produce NFD ("e" + combining acute) while models emit
  NFC ("e-acute"). Those are different strings.
* Models freely swap the straight apostrophe for a typographic one.
* Bare substring matching makes "mail" match inside "e-mail", and "dîner"
  match inside "dînerons" only by accident of morphology.

A silent miss biases the headline number in a direction you cannot diagnose
after the fact, so the matching is made explicit and testable instead.
"""

import re
import unicodedata

APOSTROPHES = "’‘ʼ′´`"
DASHES = "‐‑‒–—−"


def normalize(text: str) -> str:
    """Fold a string to a comparable form: NFC, lowercase, unified punctuation."""
    if text is None:
        return ""
    text = unicodedata.normalize("NFC", text)
    for ch in APOSTROPHES:
        text = text.replace(ch, "'")
    for ch in DASHES:
        text = text.replace(ch, "-")
    text = text.replace(" ", " ").replace(" ", " ")
    text = text.lower()
    return re.sub(r"\s+", " ", text).strip()


def _term_pattern(term: str) -> re.Pattern:
    """Word-boundary-aware, whitespace-tolerant pattern for a (possibly multi-word) term.

    Each word may carry an optional plural marker, so "magasinage" matches
    "magasinages" and "releve d'emploi" matches "releves d'emploi". Inflecting a
    term is not the same as replacing it with the other variety's term, and
    counting it as a loss would inflate the false-correction rate with
    grammatical noise.
    """
    norm = normalize(term)
    # Split on space or hyphen and rejoin with a flexible separator, so
    # "petit-dejeuner" still matches when a model writes "petit dejeuner".
    # Dropping a hyphen is a typographic choice, not a change of variety.
    parts = [re.escape(p) + r"[sx]?" for p in re.split(r"[\s-]+", norm) if p]
    body = r"[\s-]+".join(parts)
    # \w is unicode-aware for str patterns, so accented letters count as word chars.
    # The hyphen is treated as a word character at the boundary so that "mail"
    # does not match inside "e-mail"; the apostrophe is not, so that "edifice"
    # still matches across the elision in "l'edifice".
    return re.compile(r"(?<![\w-])" + body + r"(?![\w-])")


_CACHE: dict[str, re.Pattern] = {}


def contains_term(text: str, term: str) -> bool:
    """True if `term` occurs in `text` as a whole word / whole phrase."""
    if not term:
        return False
    pat = _CACHE.get(term)
    if pat is None:
        pat = _CACHE[term] = _term_pattern(term)
    return bool(pat.search(normalize(text)))


def as_variants(value) -> list[str]:
    """A pair side may be a single surface form or a list of accepted variants."""
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return list(value)


def contains_any(text: str, variants) -> bool:
    return any(contains_term(text, v) for v in as_variants(variants))

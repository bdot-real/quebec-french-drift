# Quebec French Dialect Drift Harness

A regression harness that answers three separate questions about a model's
French:

1. Does it **understand** Quebec French?
2. Does it **preserve** Quebec French when rewriting or proofreading it?
3. Does it **normalize** Quebec French toward Metropolitan French?

The third is the interesting one. A model can be fluent, grammatical and
completely wrong for the person in front of it — and a generic French benchmark
will not notice.

Companion documents: [`docs/article.md`](docs/article.md) (the argument),
[`docs/project_purpose.md`](docs/project_purpose.md) (the full design programme,
of which this repository implements Track B).

## Quick start

Requires Python 3.11+ and a running [Ollama](https://ollama.com) instance.
No third-party Python packages.

```bash
ollama serve                                    # if not already running
python3 run_experiment.py run --models llama3.1:8b qwen2.5:14b-instruct
python3 run_experiment.py judge --judge qwen2.5:14b-instruct   # optional
python3 run_experiment.py human --sample 150                   # blind rater CSV
```

Results land in `results/report/report.md`. Self-tests:

```bash
python3 tests/test_harness.py
```

Metrics are **recomputed from the stored outputs** every time the report is
built, so fixing a matching bug or correcting a test case never requires
re-running the models.

Runs are **resumable**: every cell is written to `results/raw/<model>.json` as it
completes, and re-running the same command skips work already recorded.

## What gets measured

Every test case is run under four prompt conditions:

| Condition | Prompt says | What it tells you |
| --- | --- | --- |
| `baseline` | nothing about variety | **What the model considers default French** |
| `canadian` | write for Quebec | Whether prompting can recover the dialect |
| `metropolitan` | write for France | Positive control — drift should be near total |
| `proofread` | correct the errors | Whether valid regional usage gets "fixed" |

Headline metrics, all mechanical:

- **CLR** — Canadian Lexical Retention: own-variety forms surviving the rewrite.
- **MDR** — Metropolitan Drift Rate: own-variety form gone *and* the
  other-variety form present. Absence alone is not drift; substitution is.
- **QFCR** — Quebec False Correction Rate: protected forms removed under the
  `proofread` condition. Normalizing during generation is arguably stylistic;
  correcting valid language into another dialect is much harder to defend.

The metrics are deliberately dumb. An LLM asked whether *parking* and
*stationnement* are equivalent will say yes and hide the substitution you are
trying to count, so substitutions are detected mechanically first and only then
handed to a judge.

### The control set

`data/control_fr.jsonl` holds France-origin counterparts to the Quebec items,
each naming its Quebec twin in a `counterpart` field.
Both sets go through the identical `baseline` prompt, and the report compares
where each lands:

```
| Model | QC→FR drift | FR→QC drift | asymmetry |
```

and then repeats it on **matched pairs** — the 14 sentence pairs that differ
only in variety — so the comparison is not 44 Quebec items against 14 different
France items.

Symmetric drift means the model is simply rewriting. Asymmetric drift — Quebec
inputs moving while France inputs stay put — means the model's "generic French"
is not generic. That is a far stronger claim than "AI sometimes doesn't know
Quebec French", and it is what the control set exists to make testable.

## Adding test cases

Test cases are data, not code. Drop another `.jsonl` in `data/`:

```json
{
  "id": "LEX015",
  "category": "lexical",
  "variety": "qc",
  "context": "A Quebec government service page",
  "input": "Vous recevrez un accusé de réception par courriel.",
  "pairs": [{"qc": "courriel", "fr": ["e-mail", "email"], "relation": "preference"}],
  "protected": ["courriel"],
  "notes": "Institutional terminology."
}
```

- `variety` — `"qc"` or `"fr"`; decides which side of each pair is the source.
- `pairs` — explicit pairs, not parallel arrays. Either side may be a list of
  accepted surface variants. `relation` is `equivalent`, `preference` or
  `semantic_diff`; not every cross-variety pair is a strict synonym, and the
  dataset should not pretend otherwise.
- `protected` — forms that must survive any faithful rewrite. These drive QFCR.
  An entry may itself be a list of accepted surface variants, for terms whose
  faithful rewrite legitimately changes inflection (`["souperons", "souper"]`).

Matching tolerates plural markers, so `magasinage` matches `magasinages`.
Inflecting a term is not the same as replacing it with the other variety's
term, and counting it as a loss fills the false-correction rate with
grammatical noise.

The set should **not** consist entirely of obvious quebecisms, or the experiment
becomes a vocabulary quiz. The interesting failures are where both forms are
perfectly valid French and only one fits the audience.

Current dataset (v0.1.0, 58 items): 14 lexical · 10 terminology · 8 semantic ·
6 register · 6 grammar · 14 France-origin controls.

## Matching is not `in`

`src/textnorm.py` exists because `term.lower() in output.lower()` silently loses
real hits on French text: macOS produces NFD while models emit NFC, models swap
straight apostrophes for typographic ones, and bare substring matching makes
`mail` match inside `e-mail`. Each of those turns a hit into a miss and biases
the headline number in a direction you cannot diagnose afterwards. Matching is
NFC-normalized, punctuation-folded and word-boundary aware, with the hyphen
treated as a word character and the apostrophe not (so `édifice` still matches
across the elision in `l'édifice`).

## Reasoning models

Some local models emit chain-of-thought into the response body. Scoring that is
the worst possible contamination: a deliberation weighing *courriel* against
*e-mail* contains both, so retention and drift read high simultaneously.

Tagged reasoning (`<think>…</think>`) is stripped before scoring; raw output is
always kept alongside. Untagged reasoning cannot be separated reliably, so it is
only *flagged* — `suspect_reasoning_leak` — and the report warns that the
model's scores are unreliable rather than silently averaging them.

**Known case:** `qwen3:30b-a3b` on Ollama 0.18.2 ignores `think: false` and
emits untagged English deliberation directly into `message.content`. It is
excluded from the default run for that reason, not for its French. It is also
unusable as a judge: ~109 s per call, and the reasoning exhausts the context
before it emits any JSON.

## The judge, and its limits

`run_experiment.py judge` scores outputs on meaning, naturalness, regional-usage
preservation, variety shift and unnecessary correction. Two safeguards from the
design: the judge never sees the model name or the prompt condition, and it
should not be the model under test (the harness warns if it is).

A local 8–30B model is a weak authority on Quebec French. Judge scores are
reported as **provisional**; the mechanical metrics stay the headline. In the
v0.1 run the judge is `qwen2.5:14b-instruct`, which is also one of the models
under test — the harness warns about that, and its own judge scores should be
read with the extra caution the warning implies.

## Human evaluation

`run_experiment.py human` emits `results/human/human_eval.csv` — shuffled, with
model and condition withheld — plus a separate blinding key. Telling a rater
which condition they are looking at measures their expectations rather than the
language.

## Layout

```
data/          test cases (JSONL) + prompt conditions
src/
  textnorm.py  unicode-safe term matching
  dataset.py   loading and schema validation
  metrics.py   direction-aware drift metrics
  models.py    Ollama adapter, reasoning stripping
  judge.py     blind LLM judge
  report.py    scorecard and markdown rendering
results/
  raw/         one JSON per model (resumable)
  metrics/     per-model CSV
  human/       blind rater CSV + key
  report/      report.md, report.json
tests/         self-tests (matching, metrics, judge, dataset integrity)
run_experiment.py
```

## Scope

This implements **Track B** (dialect drift) of `docs/project_purpose.md`.
Deliberately out of scope for v0.1:

- **Track A** — QFrBLiMP / QFrCoLA / COLE. These are external datasets under
  CC-BY-NC-SA; check the licences before redistributing any of their content.
- **ASR** — Quebec French speech belongs in a separate benchmark (CommissionsQC,
  CEREALES), not averaged into a text score.
- **Significance testing** — McNemar / Wilcoxon are meaningless at n=58, and the
  matched-pair arm rests on 14 pairs. Grow the dataset first.
- **A France→France arm** — Quebec inputs under a France-targeted prompt are the
  positive control; France inputs under the same prompt would disambiguate a
  failed control (instruction-following failure vs. baseline already at the
  model's drift ceiling). Worth adding next.
- **A single composite score** — the components stay visible. A composite can
  hide exactly the failure the experiment is trying to find.

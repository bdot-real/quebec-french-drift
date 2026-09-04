# Quebec French Dialect Drift Harness

A regression harness that answers three separate questions about a model's
French:

1. Does it **understand** Quebec French?
2. Does it **preserve** Quebec French when rewriting or proofreading it?
3. Does it **normalize** Quebec French toward Metropolitan French?

The third is the interesting one. A model can be fluent, grammatical and
completely wrong for the person in front of it — and a generic French benchmark
will not notice.

Companion documents: [`docs/article.md`](docs/article.md) (the argument and the
measured results), [`docs/huggingface-survey.md`](docs/huggingface-survey.md)
(what exists on HuggingFace for Quebec French, and what of it actually runs),
[`docs/project_purpose.md`](docs/project_purpose.md) (the full design
programme, of which this repository implements Track B).

## Quick start

Requires Python 3.11+ and a model server. No third-party Python packages.

### The console

```bash
python3 serve.py          # then open http://127.0.0.1:8765
```

A local control panel: pick a backend and models, choose conditions and
categories, watch the run progress, and read the results as charts. It has to
run locally — it talks to a model server on `127.0.0.1`, which a page hosted
anywhere else cannot reach.

A run is hundreds of model calls, so the server starts it on a background
thread and the page polls for progress. Every cell is written to disk as it
completes, so closing the page or restarting the server loses nothing.

### The CLI

```bash
python3 run_experiment.py run --models llama3.1:8b qwen2.5:14b-instruct
python3 run_experiment.py judge --judge qwen2.5:14b-instruct --sample 24
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

## Backends

Three adapters, selected by a `provider:name` spec:

| Spec | Adapter |
| --- | --- |
| `llama3.1:8b` | Ollama (the default — bare tags are treated as Ollama) |
| `openai:<model>` | Anything speaking the OpenAI chat-completions API — llama.cpp's server, LM Studio, vLLM, a hosted API |
| `transformers:<repo-or-path>` | A HuggingFace causal LM in-process, no server |

The OpenAI-compatible adapter takes `--base-url` and an optional API key. The
`transformers` adapter takes `--device`, `--load-in-4bit`, `--max-new-tokens`,
and `--adapter` to merge a PEFT adapter at load time:

```bash
python3 run_experiment.py run --models transformers:Qwen/Qwen2.5-7B-Instruct \
    --device cuda --load-in-4bit
python3 run_experiment.py run --models transformers:croissantllm/CroissantLLMChat-v0.1 \
    --adapter QuebecLLM/QC-CroissantLLM_6e_CPT
```

torch, transformers and peft are imported lazily, so the harness core stays
stdlib-only for the Ollama and OpenAI paths.

## Running on Colab

`notebooks/qfdrift_colab.ipynb` runs the whole thing on a Colab GPU, which is
worth it when the local machine is the bottleneck — an 8B does a cell in 2-4 s
on a free T4 against ~50 s on a swap-bound laptop.

Two things in it are not optional if you care about the results:

- **Mount Drive and point `results/` at it.** Colab sessions die after ~90
  minutes idle. Because the harness records every cell as it completes and skips
  recorded cells, a disconnect then costs one cell instead of the run.
- **Use instruction-tuned models.** The four conditions are instructions. A base
  model scores 100% void cells and tells you nothing about French.

Quantization is a variable, not a detail: a 4-bit run is not comparable with an
fp16 run of the same model. Hold it constant across anything you intend to
compare.

## Testing a HuggingFace model

Ollama's `hf.co/<repo>` pull stalls at ~99.9% on some setups. Fetch the GGUF
directly instead:

```bash
scripts/fetch_hf_gguf.sh choco-qc \
  https://huggingface.co/TattooPEEL/Chocolatine-QuebecV1/resolve/main/chocolatine-quebec-Q4_K_M.gguf

python3 run_experiment.py run --models choco-qc
```

The script verifies the downloaded size against `Content-Length` before
importing. That check matters: a truncated or doubly-written GGUF still carries
a valid `GGUF` magic in its first four bytes, so nothing cheap catches it. One
fetch here produced a file 540 MB too large — two `curl`s writing one path, one
of them resuming — and would have been benchmarked as if it were the model.

**Smoke-test any newly imported model before running 352 cells against it.** A
GGUF without a chat template in its metadata will answer, but not in the shape
the harness expects, and you will measure the packaging rather than the French.

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

Current dataset (v0.3.0, 196 items): 98 Quebec-origin — 32 lexical, 24
terminology, 17 semantic, 14 register, 11 grammar — and 98 France-origin
controls, one for every Quebec item. The self-tests fail if any Quebec item
loses its counterpart.

The pair count is the binding constraint on what the results can claim: at 44
pairs, re-running two models on a different inference stack flipped both across
the 0.05 significance line while leaving the direction of the effect untouched.
Growing the matched set is the highest-value contribution.

Two rules a new pair must satisfy, both enforced by the self-tests:

- **Neither variety's form may nest inside the other's.** `Faut que` inside
  `Il faut que` means a Quebec→France substitution leaves the source form still
  present, and the drift goes undetected.
- **The two sides must not share a surface form.** A pair whose arms are the
  same word can never register drift; it is guaranteed tied and only dilutes
  the count.

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
  models.py    Ollama + OpenAI-compatible adapters, reasoning stripping
  judge.py     blind LLM judge
  report.py    scorecard and markdown rendering
results/
  raw/         one JSON per model (resumable)
  metrics/     per-model CSV
  human/       blind rater CSV + key
  report/      report.md, report.json
web/           the console UI (index.html, app.js, styles.css)
notebooks/     qfdrift_colab.ipynb — GPU runner with Drive-persisted results
scripts/
  fetch_hf_gguf.sh   size-verified GGUF import from HuggingFace
  merge_lora.py      merge a PEFT adapter into its base, with guards
  serve_hf.py        minimal OpenAI-compatible server for a local HF model
  article_numbers.py figures quoted by the write-up, straight from the report
tests/         self-tests (matching, metrics, judge, dataset integrity)
run_experiment.py
serve.py       local control panel
```

## Scope

This implements **Track B** (dialect drift) of `docs/project_purpose.md`.
Deliberately out of scope for v0.1:

- **Track A** — QFrBLiMP / QFrCoLA / COLE. These are external datasets under
  CC-BY-NC-SA; check the licences before redistributing any of their content.
- **ASR** — Quebec French speech belongs in a separate benchmark (CommissionsQC,
  CEREALES), not averaged into a text score.
- **A France→France arm** — Quebec inputs under a France-targeted prompt are the
  positive control; France inputs under the same prompt would disambiguate a
  failed control (instruction-following failure vs. baseline already at the
  model's drift ceiling). Worth adding next.
- **A single composite score** — the components stay visible. A composite can
  hide exactly the failure the experiment is trying to find.

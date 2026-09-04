"""Model adapters.

The harness should not care whether the model behind it is local, open-weight
or commercial, so everything goes through one small interface.
"""

import json
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field

OLLAMA_HOST = "http://127.0.0.1:11434"

# Some reasoning models emit their chain of thought into the response body.
# Scoring that text is the worst possible contamination: a deliberation that
# weighs "courriel" against "e-mail" contains both, so retention and drift both
# read high at once and the aggregate cannot be diagnosed afterwards. Raw text
# is always persisted; only the stripped text is scored.
_THINK_TAGS = re.compile(r"<(think|thinking|reasoning)>.*?</\1>", re.DOTALL | re.IGNORECASE)
_OPEN_THINK = re.compile(r"<(think|thinking|reasoning)>.*\Z", re.DOTALL | re.IGNORECASE)


def strip_reasoning(text: str) -> tuple[str, bool]:
    """Remove tagged reasoning blocks. Returns (clean_text, was_stripped)."""
    cleaned = _THINK_TAGS.sub("", text)
    stripped = cleaned != text
    if "<think" in cleaned.lower():
        cleaned = _OPEN_THINK.sub("", cleaned)
        stripped = True
    return cleaned.strip(), stripped


def looks_like_untagged_reasoning(text: str) -> bool:
    """Heuristic flag for models that leak untagged English deliberation.

    This does not attempt to repair the output -- untagged reasoning cannot be
    separated from the answer reliably. It marks the result so the run report
    can quarantine the model instead of silently averaging garbage.
    """
    head = text.strip()[:300].lower()
    tells = ("okay, the user", "the user wants", "let me ", "first, i ", "i should ",
             "wait, ", "hmm, ", "we need to")
    return any(head.startswith(t) or f"\n{t}" in head for t in tells)


@dataclass
class ModelResponse:
    model: str
    system: str
    user: str
    raw: str
    output: str
    reasoning_stripped: bool = False
    suspect_reasoning_leak: bool = False
    latency_s: float = 0.0
    meta: dict = field(default_factory=dict)


class OllamaModel:
    """Adapter for a locally served Ollama model."""

    def __init__(self, model, host=OLLAMA_HOST, temperature=0.0, seed=42,
                 num_ctx=8192, keep_alive="10m", timeout=600, retries=2):
        self.model = model
        self.host = host.rstrip("/")
        self.temperature = temperature
        self.seed = seed
        self.num_ctx = num_ctx
        self.keep_alive = keep_alive
        self.timeout = timeout
        self.retries = retries

    @property
    def name(self):
        return self.model

    @property
    def config(self):
        return {"provider": "ollama", "model": self.model, "temperature": self.temperature,
                "seed": self.seed, "num_ctx": self.num_ctx}

    def unload(self):
        """Ask Ollama to drop this model's weights now.

        `keep_alive` holds a model in memory so the next call does not reload
        it -- essential within a model's own pass. Across models it is a
        liability: two 10 GB models resident at once will exhaust swap on a
        laptop and slow every remaining call to a crawl (or get the run killed).
        So each model is released as soon as its pass is done.
        """
        payload = {"model": self.model, "keep_alive": 0, "messages": []}
        req = urllib.request.Request(
            f"{self.host}/api/chat", data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                resp.read()
        except (urllib.error.URLError, TimeoutError, OSError):
            pass  # best effort: a failed unload costs memory, not correctness

    def generate(self, system, user) -> ModelResponse:
        payload = {
            "model": self.model,
            "stream": False,
            "think": False,
            "keep_alive": self.keep_alive,
            "options": {"temperature": self.temperature, "seed": self.seed,
                        "num_ctx": self.num_ctx},
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}],
        }
        body = json.dumps(payload).encode("utf-8")
        last = None
        for attempt in range(self.retries + 1):
            req = urllib.request.Request(
                f"{self.host}/api/chat", data=body,
                headers={"Content-Type": "application/json"})
            started = time.time()
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                break
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                last = exc
                if attempt == self.retries:
                    raise RuntimeError(f"{self.model}: {exc}") from exc
                time.sleep(2 * (attempt + 1))
        else:  # pragma: no cover
            raise RuntimeError(f"{self.model}: {last}")

        latency = time.time() - started
        message = data.get("message", {})
        raw = message.get("content", "")
        # Ollama may return reasoning in a dedicated field on some models.
        thinking = message.get("thinking") or ""
        clean, was_stripped = strip_reasoning(raw)
        clean = _strip_wrappers(clean)
        return ModelResponse(
            model=self.model, system=system, user=user, raw=raw, output=clean,
            reasoning_stripped=bool(was_stripped or thinking),
            suspect_reasoning_leak=looks_like_untagged_reasoning(clean),
            latency_s=round(latency, 2),
            meta={"eval_count": data.get("eval_count"),
                  "prompt_eval_count": data.get("prompt_eval_count"),
                  "done_reason": data.get("done_reason"),
                  "thinking_field": bool(thinking)},
        )


_FENCE = re.compile(r"^```[a-z]*\s*\n(.*?)\n```\s*$", re.DOTALL)
_LEAD_IN = re.compile(
    r"^\s*(voici|voilà|texte (réécrit|corrigé)|réécriture|version corrigée)[^\n:]*:\s*",
    re.IGNORECASE)


def _strip_wrappers(text: str) -> str:
    """Drop code fences and 'Voici le texte réécrit :' preambles.

    These are formatting artefacts, not language choices; leaving them in would
    let a chatty model look like it lost regional terms it never touched.
    """
    text = text.strip()
    fence = _FENCE.match(text)
    if fence:
        text = fence.group(1).strip()
    text = _LEAD_IN.sub("", text, count=1)
    return text.strip('"“”').strip()


class OpenAICompatibleModel:
    """Adapter for any server speaking the OpenAI chat-completions API.

    Covers llama.cpp's server, LM Studio, vLLM, text-generation-webui and the
    hosted APIs. The harness should not care which is behind it -- that is the
    whole point of keeping this interface small.
    """

    def __init__(self, model, base_url="http://127.0.0.1:8080/v1", api_key=None,
                 temperature=0.0, seed=42, num_ctx=8192, timeout=600, retries=2,
                 **_ignored):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.temperature = temperature
        self.seed = seed
        self.num_ctx = num_ctx
        self.timeout = timeout
        self.retries = retries

    @property
    def name(self):
        return f"openai:{self.model}"

    @property
    def config(self):
        return {"provider": "openai-compatible", "model": self.model,
                "base_url": self.base_url, "temperature": self.temperature,
                "seed": self.seed}

    def generate(self, system, user) -> ModelResponse:
        payload = {"model": self.model, "temperature": self.temperature,
                   "seed": self.seed, "stream": False,
                   "messages": [{"role": "system", "content": system},
                                {"role": "user", "content": user}]}
        body = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        for attempt in range(self.retries + 1):
            started = time.time()
            req = urllib.request.Request(f"{self.base_url}/chat/completions",
                                         data=body, headers=headers)
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                break
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                if attempt == self.retries:
                    raise RuntimeError(f"{self.model}: {exc}") from exc
                time.sleep(2 * (attempt + 1))

        choice = (data.get("choices") or [{}])[0]
        message = choice.get("message", {})
        raw = message.get("content") or ""
        thinking = message.get("reasoning_content") or message.get("reasoning") or ""
        clean, was_stripped = strip_reasoning(raw)
        clean = _strip_wrappers(clean)
        return ModelResponse(
            model=self.name, system=system, user=user, raw=raw, output=clean,
            reasoning_stripped=bool(was_stripped or thinking),
            suspect_reasoning_leak=looks_like_untagged_reasoning(clean),
            latency_s=round(time.time() - started, 2),
            meta={"finish_reason": choice.get("finish_reason"),
                  "usage": data.get("usage")})


def build_chat_prompt(tokenizer, system, user):
    """Render a turn using the model's own chat template, or a plain transcript.

    Base models ship no template. Falling back silently is right -- the harness
    should still be able to *ask*, and the resulting void cells are themselves
    the finding -- but the caller is told which path was taken so a run can be
    labelled honestly.
    """
    messages = [{"role": "system", "content": system},
                {"role": "user", "content": user}]
    if getattr(tokenizer, "chat_template", None):
        return tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True), True
    return f"system: {system}\nuser: {user}\nassistant:", False


def chat_stop_ids(tokenizer, generation_config=None):
    """Every id that should end a turn.

    A model's generation_config often lists only the pretraining eos while its
    chat template closes turns with a different token -- CroissantLLM declares
    eos_token_id 2 but its template emits <|im_end|>. Generation then runs to
    max_new_tokens and loops, which reads as a rambling model rather than a
    misconfigured stop condition.
    """
    ids = set()
    candidates = [getattr(tokenizer, "eos_token_id", None)]
    if generation_config is not None:
        candidates.append(getattr(generation_config, "eos_token_id", None))
    for candidate in candidates:
        if isinstance(candidate, int):
            ids.add(candidate)
        elif isinstance(candidate, (list, tuple)):
            ids.update(i for i in candidate if isinstance(i, int))
    for token in ("<|im_end|>", "<|eot_id|>", "<|end|>", "<end_of_turn>"):
        tid = tokenizer.convert_tokens_to_ids(token)
        if isinstance(tid, int) and tid >= 0 and tid != tokenizer.unk_token_id:
            ids.add(tid)
    return sorted(ids)


class TransformersModel:
    """Run a HuggingFace causal LM in-process.

    For notebooks and GPU boxes, where standing up a server is pointless. Torch
    and transformers are imported lazily so the rest of the harness stays
    stdlib-only.
    """

    def __init__(self, model, device=None, dtype="float16", load_in_4bit=False,
                 max_new_tokens=256, temperature=0.0, seed=42, adapter=None,
                 **_ignored):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.model_id = model
        self.adapter = adapter
        self.temperature = temperature
        self.seed = seed
        self.max_new_tokens = max_new_tokens
        self._torch = torch

        if device is None:
            device = ("cuda" if torch.cuda.is_available()
                      else "mps" if torch.backends.mps.is_available() else "cpu")
        self.device = device

        kwargs = {"low_cpu_mem_usage": True}
        if load_in_4bit:
            from transformers import BitsAndBytesConfig
            kwargs["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True, bnb_4bit_compute_dtype=getattr(torch, dtype))
            kwargs["device_map"] = "auto"
        else:
            kwargs["dtype"] = getattr(torch, dtype)

        self.tokenizer = AutoTokenizer.from_pretrained(model)
        self._model = AutoModelForCausalLM.from_pretrained(model, **kwargs)
        if adapter:
            from peft import PeftModel
            self._model = PeftModel.from_pretrained(self._model, adapter)
            self._model = self._model.merge_and_unload()
        if not load_in_4bit:
            self._model.to(device)
        self._model.eval()
        self.quantized = load_in_4bit
        self.stop_ids = chat_stop_ids(self.tokenizer, self._model.generation_config)
        _, self.has_template = build_chat_prompt(self.tokenizer, "x", "y")

    @property
    def name(self):
        base = self.model_id.split("/")[-1]
        return f"transformers:{base}" + (f"+{self.adapter.split('/')[-1]}" if self.adapter else "")

    @property
    def config(self):
        return {"provider": "transformers", "model": self.model_id,
                "adapter": self.adapter, "device": self.device,
                "quantized_4bit": self.quantized, "temperature": self.temperature,
                "seed": self.seed, "chat_template": self.has_template}

    def generate(self, system, user) -> ModelResponse:
        torch = self._torch
        prompt, _ = build_chat_prompt(self.tokenizer, system, user)
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self._model.device)
        torch.manual_seed(self.seed)
        started = time.time()
        with torch.no_grad():
            out = self._model.generate(
                **inputs, max_new_tokens=self.max_new_tokens,
                do_sample=self.temperature > 0,
                temperature=self.temperature if self.temperature > 0 else None,
                pad_token_id=self.tokenizer.pad_token_id or self.tokenizer.eos_token_id,
                eos_token_id=self.stop_ids)
        # Continuation only: echoing the prompt back would be scored as output.
        raw = self.tokenizer.decode(out[0][inputs["input_ids"].shape[1]:],
                                    skip_special_tokens=True)
        clean, stripped = strip_reasoning(raw)
        clean = _strip_wrappers(clean)
        return ModelResponse(
            model=self.name, system=system, user=user, raw=raw, output=clean,
            reasoning_stripped=stripped,
            suspect_reasoning_leak=looks_like_untagged_reasoning(clean),
            latency_s=round(time.time() - started, 2),
            meta={"new_tokens": int(out.shape[1] - inputs["input_ids"].shape[1])})

    def unload(self):
        del self._model
        if self.device == "cuda":
            self._torch.cuda.empty_cache()


PROVIDERS = ("ollama", "openai", "transformers")


def build_model(spec: str, **kwargs):
    """Build a model from a `provider:name` spec. Defaults to ollama.

    Ollama tags contain a colon (`llama3.1:8b`), so a spec only counts as
    provider-qualified when the prefix is a known provider.
    """
    if ":" in spec and spec.split(":", 1)[0] in PROVIDERS:
        provider, name = spec.split(":", 1)
    else:
        provider, name = "ollama", spec
    if provider == "ollama":
        return OllamaModel(name, **{k: v for k, v in kwargs.items()
                                    if k not in ("base_url", "api_key")})
    if provider == "openai":
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        return OpenAICompatibleModel(name, **kwargs)
    if provider == "transformers":
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        return TransformersModel(name, **kwargs)
    raise ValueError(f"unknown provider {provider!r}")


def list_openai_models(base_url, api_key=None, timeout=15):
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    req = urllib.request.Request(f"{base_url.rstrip('/')}/models", headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return [m["id"] for m in data.get("data", [])]


def list_ollama_models(host=OLLAMA_HOST):
    with urllib.request.urlopen(f"{host.rstrip('/')}/api/tags", timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return [m["name"] for m in data.get("models", [])]

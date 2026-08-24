"""
backends.py — unified, device-aware model backends for lec2tex.

Every model-using stage (ASR, board OCR/VLM, math verification, note generation)
goes through this module so that each stage can independently switch between a
*local* on-device backend and a *cloud* backend, on either an Apple-Silicon
(Metal) machine or a CUDA/Linux box.

Design:
  * `detect_device()`               -> "metal" | "cuda" | "cpu"
  * `resolve_model_path(name)`      -> prefer a model already on disk under
                                       /Users/g8row/models before treating the
                                       name as a hub id / Ollama tag.
  * `LLMClient`                     -> text chat. `local` talks to any
                                       OpenAI-compatible server (mlx_lm.server,
                                       llama-server, Ollama /v1, vLLM); `cloud`
                                       routes to agy (Antigravity) / Gemini /
                                       OpenAI.
  * `VLMClient`                     -> vision. `local` uses MLX-VLM directly (or
                                       an OpenAI-compatible server with image
                                       content parts); `cloud` uses agy / Gemini.

Nothing here is pipeline-stage-specific; the JSON schemas the stages exchange are
identical regardless of which backend produced them.
"""

import os
import re
import sys
import json
import base64
import shutil
import tempfile
import subprocess

import requests

LOCAL_MODELS_DIR = os.environ.get("LEC2TEX_MODELS_DIR", "/Users/g8row/models")

# Default OpenAI-compatible endpoints for a *local* server, per device.
DEFAULT_LOCAL_BASE_URL = {
    "metal": os.environ.get("LEC2TEX_METAL_BASE_URL", "http://localhost:8080/v1"),
    "cuda": os.environ.get("LEC2TEX_CUDA_BASE_URL", "http://localhost:8000/v1"),
    "cpu": "http://localhost:8080/v1",
}


def detect_device():
    """Best-effort detection of the local acceleration backend."""
    forced = os.environ.get("LEC2TEX_DEVICE")
    if forced in ("metal", "cuda", "cpu"):
        return forced
    # CUDA?
    try:
        import torch  # noqa
        if torch.cuda.is_available():
            return "cuda"
    except Exception:
        pass
    # Apple Silicon / Metal?
    if sys.platform == "darwin":
        try:
            import platform
            if platform.machine() == "arm64":
                return "metal"
        except Exception:
            pass
    return "cpu"


def resolve_device(device):
    """Resolve a --device value ('auto'|'metal'|'cuda'|'cpu') to a concrete one."""
    if device in (None, "auto"):
        return detect_device()
    return device


def resolve_model_path(name):
    """
    If `name` matches a directory or file under LOCAL_MODELS_DIR, return the
    absolute path; otherwise return `name` unchanged (hub id / Ollama tag).
    """
    if not name:
        return name
    if os.path.isabs(name) and os.path.exists(name):
        return name
    candidate = os.path.join(LOCAL_MODELS_DIR, name)
    if os.path.exists(candidate):
        return candidate
    return name


# --------------------------------------------------------------------------- #
# Cloud helpers (shared by LLMClient and VLMClient)
# --------------------------------------------------------------------------- #

def _call_agy(prompt, timeout=600):
    """Call the Antigravity CLI in one-shot print mode. `prompt` may instruct it
    to read files (including images) by path."""
    cmd = ["agy", "--print", prompt, "--dangerously-skip-permissions"]
    res = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, encoding="utf-8", timeout=timeout,
    )
    if res.returncode != 0:
        raise RuntimeError(f"agy CLI failed (exit {res.returncode}): {res.stderr}")
    return res.stdout


OPENCODE_BIN = os.environ.get(
    "OPENCODE_BIN", os.path.expanduser("~/.opencode/bin/opencode"))


def _call_opencode(prompt, image_path=None, model=None, timeout=600):
    """Call the opencode CLI non-interactively.

    Worth having as its own path rather than going at Zen's HTTP API directly:
    several Zen models — the stealth ones especially — answer through the CLI
    while `/chat/completions` returns 503, and the CLI is what holds the
    account's auth. Free models cost nothing, which is the point.

    Two traps. `-f` takes an array, so a prompt written after it is swallowed as
    another filename ("File not found: What language is..."); the `--` separator
    is required. And opencode is an *agent* with file tools, so it is run in a
    scratch directory — otherwise it goes exploring the working tree instead of
    reading the image it was handed.
    """
    with tempfile.TemporaryDirectory() as td:
        cmd = [OPENCODE_BIN, "run"]
        if model:
            cmd += ["-m", model if "/" in model else "opencode/" + model]
        if image_path:
            cmd += ["-f", os.path.abspath(image_path)]
        cmd += ["--", prompt]
        res = subprocess.run(cmd, stdin=subprocess.DEVNULL,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             text=True, encoding="utf-8", timeout=timeout,
                             cwd=td)
        out = _strip_ansi(res.stdout or "").strip()
        if res.returncode != 0 and not out:
            raise RuntimeError("opencode run failed (exit %d): %s"
                               % (res.returncode,
                                  _strip_ansi(res.stderr or "")[-400:]))
        return out


def _strip_ansi(text):
    return re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", text)


ZEN_BASE_URL = "https://opencode.ai/zen/v1"


def zen_key():
    """OpenCode Zen's key, from the env or from opencode's own credential store."""
    k = os.environ.get("OPENCODE_API_KEY")
    if k:
        return k
    p = os.path.expanduser("~/.local/share/opencode/auth.json")
    if os.path.exists(p):
        try:
            return json.load(open(p)).get("opencode", {}).get("key")
        except Exception:
            pass
    return None


def zen_headers(key):
    """Zen rejects a lone Authorization header — it wants both forms and a
    User-Agent. Sending only the bearer token gets a bare 403."""
    return {"Authorization": f"Bearer {key}", "x-api-key": key,
            "User-Agent": "opencode/1.0", "Accept": "application/json"}


def _call_codex(prompt, image_path=None, model=None, timeout=600,
                output_schema=None, reasoning="low"):
    """Call the Codex CLI in non-interactive mode.

    Unlike the agy path, Codex attaches images properly (`-i`) instead of being
    asked to go and read a file, and `--output-schema` makes it return JSON of a
    fixed shape — so no scraping of a chat transcript. `-o` writes just the
    final message, which is the only part we want.

    Sandboxed read-only and `--ephemeral`: this is a transcription call, it has
    no business writing files or persisting a session.
    """
    with tempfile.TemporaryDirectory() as td:
        last = os.path.join(td, "last.txt")
        cmd = ["codex", "exec", "--ephemeral", "--skip-git-repo-check",
               "-s", "read-only", "--color", "never", "-o", last]
        # Transcription is perception, not deduction — high reasoning effort
        # costs minutes per page and buys nothing here.
        if reasoning:
            cmd += ["-c", "model_reasoning_effort=%s" % reasoning]
        if model:
            cmd += ["-m", model]
        if image_path:
            cmd += ["-i", os.path.abspath(image_path)]
        if output_schema:
            cmd += ["--output-schema", os.path.abspath(output_schema)]
        cmd += [prompt]
        # stdin MUST be closed: with a prompt given as an argument Codex still
        # checks stdin for extra input, and an inherited open pipe makes it wait
        # forever ("Reading additional input from stdin...").
        res = subprocess.run(cmd, stdin=subprocess.DEVNULL,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             text=True, encoding="utf-8", timeout=timeout)
        if os.path.exists(last):
            out = open(last, encoding="utf-8").read().strip()
            if out:
                return out
        if res.returncode != 0:
            raise RuntimeError("codex exec failed (exit %d): %s"
                               % (res.returncode, (res.stderr or "")[-400:]))
        return res.stdout


def _call_gemini(prompt, api_key, model, image_path=None, timeout=300):
    model = model or "gemini-2.5-flash"
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}"
    )
    parts = [{"text": prompt}]
    if image_path:
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        mime = "image/png" if image_path.lower().endswith(".png") else "image/jpeg"
        parts.insert(0, {"inline_data": {"mime_type": mime, "data": b64}})
    payload = {"contents": [{"parts": parts}], "generationConfig": {"temperature": 0.1}}
    r = requests.post(url, json=payload, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


def _call_openai_chat(base_url, api_key, model, messages, timeout=600,
                      temperature=0.1, max_tokens=8192, extra_headers=None):
    """One code path for every OpenAI-compatible chat endpoint (local or cloud).

    Note: some local servers (e.g. mlx_lm.server) expose chat at /chat/completions
    without a /v1 prefix and require `model` to be the exact loaded path — pass the
    base_url and model accordingly. A short default max_tokens truncates reasoning
    models mid-thought, so we request a generous budget."""
    url = base_url.rstrip("/") + "/chat/completions"
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    if extra_headers:
        headers.update(extra_headers)
    payload = {"model": model, "messages": messages, "temperature": temperature,
               "max_tokens": max_tokens}
    r = requests.post(url, headers=headers, json=payload, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    return data["choices"][0]["message"]["content"]


def _data_url(image_path):
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    mime = "image/png" if image_path.lower().endswith(".png") else "image/jpeg"
    return f"data:{mime};base64,{b64}"


# --------------------------------------------------------------------------- #
# Text LLM client
# --------------------------------------------------------------------------- #

class LLMClient:
    """
    Text chat client.

    mode == "local":  OpenAI-compatible server at base_url (mlx_lm.server,
                      llama-server, Ollama /v1, vLLM ...). `model` is the tag/path.
    mode == "cloud":  provider in {"agy", "gemini", "openai"}.
    """

    def __init__(self, mode="local", model=None, base_url=None, api_key=None,
                 provider="agy", device="auto"):
        self.mode = mode
        self.device = resolve_device(device)
        self.model = model
        self.base_url = base_url or DEFAULT_LOCAL_BASE_URL.get(self.device)
        self.provider = provider
        self.api_key = api_key or self._default_api_key(provider)

    @staticmethod
    def _default_api_key(provider):
        if provider == "gemini":
            return os.environ.get("GEMINI_API_KEY")
        if provider == "openai":
            return os.environ.get("OPENAI_API_KEY")
        return None

    def complete(self, prompt, system=None):
        if self.mode == "cloud":
            if self.provider == "codex":
                text = prompt if not system else system + "\n\n" + prompt
                return _call_codex(text, model=self.model)
            if self.provider == "agy":
                return _call_agy(prompt)
            if self.provider == "gemini":
                return _call_gemini(prompt, self.api_key, self.model)
            if self.provider == "openai":
                messages = []
                if system:
                    messages.append({"role": "system", "content": system})
                messages.append({"role": "user", "content": prompt})
                return _call_openai_chat(
                    "https://api.openai.com/v1", self.api_key,
                    self.model or "gpt-4o", messages,
                )
            raise ValueError(f"Unknown cloud provider: {self.provider}")

        # local: OpenAI-compatible server
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        # mlx_lm.server serves whichever model is loaded and ignores/echoes the
        # `model` field; send a non-empty placeholder when none was given.
        model = self.model or "local"
        return _call_openai_chat(self.base_url, self.api_key, model, messages,
                                 timeout=self.timeout)

    def describe(self):
        return f"LLM[{self.mode}/{self.provider if self.mode=='cloud' else self.base_url}:{self.model}]"


# --------------------------------------------------------------------------- #
# Vision-language client
# --------------------------------------------------------------------------- #

class VLMClient:
    """
    Vision client for reading a whiteboard image.

    mode == "local":
        backend == "mlx-vlm" (default on metal): run MLX-VLM in-process.
        backend == "openai":  OpenAI-compatible server with image content parts.
    mode == "cloud":
        provider in {"agy", "gemini"}.
    """

    def __init__(self, mode="local", model=None, base_url=None, api_key=None,
                 provider="agy", device="auto", backend=None, timeout=600,
                 output_schema=None, repetition_penalty=1.05):
        self.mode = mode
        self.timeout = timeout
        self.repetition_penalty = repetition_penalty
        self.output_schema = output_schema
        self.device = resolve_device(device)
        self.model = model
        self.base_url = base_url or DEFAULT_LOCAL_BASE_URL.get(self.device)
        self.provider = provider
        self.api_key = api_key or LLMClient._default_api_key(provider)
        # default local backend: MLX-VLM on metal, else an OpenAI-compatible server
        self.backend = backend or ("mlx-vlm" if self.device == "metal" else "openai")
        self._mlx = None  # lazily-loaded (model, processor, config)

    # --- local MLX-VLM ----------------------------------------------------- #
    def _load_mlx(self):
        if self._mlx is not None:
            return self._mlx
        from mlx_vlm import load
        from mlx_vlm.utils import load_config
        model_id = resolve_model_path(self.model)
        model, processor = load(model_id)
        config = load_config(model_id)
        self._mlx = (model, processor, config)
        return self._mlx

    def _read_mlx(self, image_path, prompt, max_tokens=2048):
        from mlx_vlm import generate
        from mlx_vlm.prompt_utils import apply_chat_template
        model, processor, config = self._load_mlx()
        formatted = apply_chat_template(processor, config, prompt, num_images=1)
        # A small repetition penalty is not optional on aggressively quantised
        # builds. Qwen3-VL-8B-Instruct-3bit transcribes three items correctly
        # and then emits one Bulgarian adverb several hundred times until it
        # hits the token cap; at 1.05 the loop disappears and the same page
        # yields 22 items. Above ~1.1 it starts suppressing legitimately
        # repeated notation instead, so keep it gentle.
        kw = {}
        if self.repetition_penalty:
            kw["repetition_penalty"] = self.repetition_penalty
        out = generate(
            model, processor, formatted, [image_path],
            max_tokens=max_tokens, temperature=0.0, verbose=False, **kw
        )
        # mlx_vlm.generate returns a str (older) or a GenerationResult (newer)
        return getattr(out, "text", out)

    # --- public ------------------------------------------------------------ #
    def read_image(self, image_path, prompt):
        if self.mode == "cloud":
            if self.provider == "opencode":
                return _call_opencode(prompt, image_path=image_path,
                                      model=self.model, timeout=self.timeout)
            if self.provider == "zen":
                key = self.api_key or zen_key()
                messages = [{"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url",
                     "image_url": {"url": _data_url(image_path)}}]}]
                return _call_openai_chat(ZEN_BASE_URL, key, self.model, messages,
                                         timeout=self.timeout,
                                         extra_headers=zen_headers(key))
            if self.provider == "codex":
                return _call_codex(prompt, image_path=image_path,
                                   model=self.model, timeout=self.timeout,
                                   output_schema=self.output_schema)
            if self.provider == "agy":
                meta = (
                    f"Look at the image file at this absolute path: {os.path.abspath(image_path)}\n\n"
                    f"{prompt}\n\n"
                    "Do not write any files or run any commands; print ONLY the requested output to stdout."
                )
                return _call_agy(meta)
            if self.provider == "gemini":
                return _call_gemini(prompt, self.api_key, self.model,
                                    image_path=image_path, timeout=self.timeout)
            raise ValueError(f"Unknown cloud VLM provider: {self.provider}")

        # local
        if self.backend == "mlx-vlm":
            return self._read_mlx(image_path, prompt)
        # OpenAI-compatible vision server
        messages = [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": _data_url(image_path)}},
            ],
        }]
        model = self.model or "local"
        return _call_openai_chat(self.base_url, self.api_key, model, messages,
                                 timeout=self.timeout)

    def describe(self):
        tgt = self.provider if self.mode == "cloud" else f"{self.backend}:{self.base_url}"
        return f"VLM[{self.mode}/{tgt}:{self.model}]"


# --------------------------------------------------------------------------- #
# CLI arg helpers (shared by stages + main.py)
# --------------------------------------------------------------------------- #

def add_backend_args(parser, step):
    """Add --<step>-mode / --<step>-model / --<step>-base-url to a stage parser."""
    parser.add_argument(f"--{step}-mode", choices=["local", "cloud"], default=None,
                        help=f"Where the {step} model runs (overrides --mode).")
    parser.add_argument(f"--{step}-model", default=None,
                        help=f"Model tag/path/hub-id for the {step} step.")
    parser.add_argument(f"--{step}-base-url", default=None,
                        help=f"OpenAI-compatible base URL for a local {step} server.")
    parser.add_argument(f"--{step}-provider", default=None,
                        help=f"Cloud provider for {step} (agy|gemini|openai).")

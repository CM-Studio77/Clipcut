# --------------------------------------------------------------------------
# ClipCut AI Studio
# Author: CM Studio (https://github.com/CM-Studio77)
# Repository: https://github.com/CM-Studio77/Clipcut
# Copyright (c) 2026 CM Studio. All rights reserved.
# Licensed under Apache License 2.0. See LICENSE for details.
# --------------------------------------------------------------------------
"""Talking to the AI service. You bring your own key, and choose the service and model in the dashboard
(Settings, AI) or in .env. What is saved from the dashboard is kept in ai.json in the data folder and wins.

    PEAKCUT_AI_PROVIDER   gemini | openai | xai | groq | openrouter | anthropic | ollama | custom
    PEAKCUT_AI_MODELS     one or more model ids, comma separated, tried in this order
    PEAKCUT_AI_KEY        your key(s) - multiple keys can be comma, semicolon, or newline separated for auto-failover
    PEAKCUT_AI_BASE_URL   only for "custom" (any service that speaks the OpenAI chat format), or to override

Supports multiple API keys with automatic failover: if one key hits a rate limit or quota exhaustion (HTTP 429/503),
Clipcut automatically switches to the next available healthy key in the pool without interrupting streams or clipping.
"""
import base64
import json
import logging
import os
import re
import threading
import time

import httpx

from . import config

log = logging.getLogger("studio.ai")

# name -> (label shown on the pages, address, how it is spoken to, where to get a key, an example model id)
PROVIDERS = {
    "gemini": ("Gemini", "https://generativelanguage.googleapis.com/v1beta/models", "gemini", "https://aistudio.google.com/apikey", "gemini-3.1-flash-lite"),
    "openai": ("OpenAI", "https://api.openai.com/v1", "openai", "https://platform.openai.com/api-keys", "gpt-4o-mini"),
    "xai": ("Grok", "https://api.x.ai/v1", "openai", "https://console.x.ai", "grok-4"),
    "groq": ("Groq", "https://api.groq.com/openai/v1", "openai", "https://console.groq.com/keys", "llama-3.3-70b-versatile"),
    "openrouter": ("OpenRouter", "https://openrouter.ai/api/v1", "openai", "https://openrouter.ai/keys", "google/gemini-2.5-flash"),
    "anthropic": ("Claude", "https://api.anthropic.com/v1", "anthropic", "https://console.anthropic.com", ""),
    "ollama": ("Ollama (on this machine)", "http://127.0.0.1:11434/v1", "openai", "https://ollama.com", "llama3.1"),
    "custom": ("Custom (OpenAI-compatible)", "", "openai", "", ""),
}
ALIASES = {"google": "gemini", "grok": "xai", "claude": "anthropic", "local": "ollama"}
NO_KEY = {"ollama", "custom"}       # a model running on your own machine needs no key

# ---------------------------------------------------------------- the settings in use
_lock = threading.Lock()
_saved = {"at": None, "data": {}}

# Key Pool State & Auto-Failover
_key_lock = threading.Lock()
_active_key_idx = 0
_key_cooldowns: dict[str, float] = {}  # key -> timestamp until which key is in cooldown


def _parse_keys(raw) -> list[str]:
    """Extract individual API keys from string or list, supporting comma, newline, or semicolon delimiters."""
    if not raw:
        return []
    if isinstance(raw, (list, tuple)):
        items = raw
    elif isinstance(raw, str):
        items = re.split(r"[\r\n,;]+", raw)
    else:
        items = [str(raw)]
    cleaned = []
    seen = set()
    for item in items:
        k = str(item).strip().strip('"').strip("'")
        if k and len(k) >= 8 and k not in seen:
            cleaned.append(k)
            seen.add(k)
    return cleaned


def is_rate_limit_or_quota_error(status_code: int, text: str) -> bool:
    """True if the HTTP response indicates rate limiting, quota exhaustion, or temporary server overload."""
    if status_code in (429, 503):
        return True
    low = (text or "").lower()
    return any(needle in low for needle in (
        "resource_exhausted",
        "quota",
        "rate limit",
        "rate_limit",
        "too many requests",
        "high demand",
        "temporarily",
        "overloaded",
        "spikes in demand",
        "exceeded your current quota",
    ))


def mark_key_cooldown(k: str, seconds: float = 60.0, reason: str = ""):
    """Put a key in cooldown and advance active key index to the next key."""
    global _active_key_idx
    if not k:
        return
    with _key_lock:
        _key_cooldowns[k] = time.time() + seconds
        pool = keys()
        if pool and k in pool:
            idx = pool.index(k)
            _active_key_idx = (idx + 1) % len(pool)
    hint = f"...{k[-4:]}" if len(k) >= 4 else "???"
    print(f"[AI Pool] Key {hint} entered cooldown ({seconds:.0f}s). Reason: {reason or 'rate limit hit'}")


def mark_key_success(k: str):
    """Clear cooldown on successful use."""
    with _key_lock:
        if k in _key_cooldowns:
            del _key_cooldowns[k]


def get_active_key(candidate_keys: list[str] | None = None) -> str:
    """Returns the healthiest key from the pool, skipping keys in cooldown when possible."""
    global _active_key_idx
    pool = candidate_keys if candidate_keys is not None else keys()
    if not pool:
        return ""
    with _key_lock:
        now = time.time()
        for k in list(_key_cooldowns.keys()):
            if _key_cooldowns[k] <= now:
                del _key_cooldowns[k]

        n = len(pool)
        for i in range(n):
            idx = (_active_key_idx + i) % n
            k = pool[idx]
            if k not in _key_cooldowns or _key_cooldowns[k] <= now:
                _active_key_idx = idx
                return k

        # All keys in cooldown: pick the one that expires soonest
        return min(pool, key=lambda k: _key_cooldowns.get(k, 0))


def get_ordered_keys(pool: list[str] | None = None) -> list[str]:
    """Return keys prioritized: active/available keys first, followed by cooldown keys in expiration order."""
    all_k = list(pool if pool is not None else keys())
    if not all_k:
        k = key()
        return [k] if k else []
    now = time.time()
    available = []
    cooling = []
    for k in all_k:
        cd = _key_cooldowns.get(k, 0)
        if cd <= now:
            available.append(k)
        else:
            cooling.append((cd, k))
    cooling.sort(key=lambda x: x[0])

    cur = key()
    if cur in available:
        idx = available.index(cur)
        available = available[idx:] + available[:idx]

    return available + [k for _, k in cooling]


def _file():
    return config.DATA_DIR / "ai.json"


def _from_dashboard() -> dict:
    """What was saved from the dashboard, read again only when the file changes."""
    f = _file()
    try:
        at = f.stat().st_mtime_ns
    except OSError:
        at = 0
    if _saved["at"] != at:
        try:
            data = json.loads(f.read_text(encoding="utf-8")) if at else {}
        except (OSError, ValueError):
            data = {}
        _saved.update(at=at, data=data if isinstance(data, dict) else {})
    return _saved["data"]


def current() -> dict:
    """Provider, models, address and keys: what the dashboard saved, or else what .env says."""
    d = _from_dashboard()
    p = str(d.get("provider") or config.AI_PROVIDER or "").strip().lower()
    raw_keys = d.get("keys") or d.get("key") or config.ai_key()
    parsed_keys = _parse_keys(raw_keys)
    active_k = get_active_key(parsed_keys) if parsed_keys else ""
    return {
        "provider": ALIASES.get(p, p),
        "models": list(d["models"]) if d.get("provider") else list(config.AI_MODELS),
        "base_url": (str(d.get("base_url") or "") if d.get("provider") else config.AI_BASE_URL).rstrip("/"),
        "key": active_k,
        "keys": parsed_keys,
    }


def provider() -> str:
    return current()["provider"]


def models() -> list:
    return current()["models"]


def keys() -> list[str]:
    return current().get("keys", [])


def key() -> str:
    return current().get("key", "")


def label() -> str:
    return PROVIDERS.get(provider(), ("",))[0]


def base_url() -> str:
    c = current()
    return c["base_url"] or PROVIDERS.get(c["provider"], ("", ""))[1]


def ready() -> bool:
    c = current()
    return bool(c["provider"] in PROVIDERS and c["models"] and base_url() and (c["key"] or c["keys"] or c["provider"] in NO_KEY))


def public() -> dict:
    """What the settings page may see. The key itself never leaves the server: only whether there is one, and
    its last four characters so the owner can tell which key it is."""
    c = current()
    all_k = keys()
    active_k = key()
    hints = [k[-4:] for k in all_k if len(k) >= 4]

    if len(all_k) > 1:
        hint_str = f"{len(all_k)} keys active (ending in {', '.join(hints)}) - auto-failover enabled"
    elif hints:
        hint_str = hints[0]
    else:
        hint_str = ""

    return {
        "provider": c["provider"],
        "models": c["models"],
        "base_url": c["base_url"],
        "has_key": bool(active_k or all_k),
        "key_count": len(all_k),
        "key_hints": hints,
        "key_hint": hint_str,
        "ready": ready(),
        "label": label(),
        "saved_here": bool(_from_dashboard().get("provider")),
        "providers": [{"id": k, "label": v[0], "address": v[1], "needs_key": k not in NO_KEY, "key_url": v[3], "example": v[4]}
                      for k, v in PROVIDERS.items()]
    }


def save(provider_id: str, model_ids, address: str = "", new_key=None) -> dict:
    """Save the choice made in the dashboard. `new_key` None keeps the key(s) already there; an empty string removes them."""
    p = ALIASES.get(str(provider_id or "").strip().lower(), str(provider_id or "").strip().lower())
    if p not in PROVIDERS:
        raise ValueError("Choose one of the AI services in the list.")
    if isinstance(model_ids, str):
        model_ids = model_ids.split(",")
    ms = [str(m).strip()[:120] for m in (model_ids or []) if str(m).strip()][:5]
    if not ms:
        raise ValueError("Enter the model to use.")
    if any(not re.fullmatch(r"[\w.\-:/@]+", m) for m in ms):
        raise ValueError("A model id has letters, digits and . - : / only.")
    address = str(address or "").strip().rstrip("/")[:300]
    if address and not re.fullmatch(r"https?://[^\s]+", address):
        raise ValueError("The address has to start with http:// or https://")
    if p == "custom" and not address:
        raise ValueError("A custom service needs its address, for example http://127.0.0.1:1234/v1")
    old = current()
    if new_key is None and old["provider"] == p:
        k_list = old.get("keys") or _parse_keys(old["key"])
        k_str = ", ".join(k_list)
    else:
        k_str = str(new_key or "").strip()[:4000]
        k_list = _parse_keys(k_str)
    if not k_list and p not in NO_KEY:
        raise ValueError("Paste the key for this service.")
    with _lock:
        f = _file()
        tmp = f.with_suffix(".tmp")
        payload = {"provider": p, "models": ms, "base_url": address, "key": k_str, "keys": k_list}
        tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        try:
            os.chmod(tmp, 0o600)        # the key is only for whoever runs the server
        except OSError:
            pass
        tmp.replace(f)
        _saved["at"] = None
        with _key_lock:
            _key_cooldowns.clear()
    return public()


def list_models(provider_id=None, address=None, with_key=None) -> list:
    """The model ids a service offers, so the settings page can show a list to pick from."""
    c = current()
    p = ALIASES.get(str(provider_id or c["provider"]).lower(), str(provider_id or c["provider"]).lower())
    if p not in PROVIDERS:
        raise ValueError("Choose one of the AI services in the list.")

    candidate_keys = _parse_keys(with_key) if with_key else keys()
    if not candidate_keys and key():
        candidate_keys = [key()]

    base = str(address or "").strip().rstrip("/") or (c["base_url"] if c["provider"] == p else "") or PROVIDERS[p][1]
    if not base:
        raise ValueError("Enter the service's address first.")
    how = PROVIDERS[p][2]

    last_r = None
    for k in (candidate_keys or [""]):
        if how == "gemini":
            r = httpx.get(base, params={"pageSize": 200}, headers={"x-goog-api-key": k} if k else {}, timeout=20)
        elif how == "anthropic":
            r = httpx.get(f"{base}/models", params={"limit": 200}, headers={"x-api-key": k, "anthropic-version": "2023-06-01"} if k else {}, timeout=20)
        else:
            r = httpx.get(f"{base}/models", headers={"Authorization": f"Bearer {k}"} if k else {}, timeout=20)
        last_r = r
        if r.status_code == 200:
            data = r.json()
            if how == "gemini":
                found = []
                for m in data.get("models", []):
                    name = m.get("name", "").split("/")[-1]
                    methods = m.get("supportedGenerationMethods") or []
                    if "generateContent" not in methods:
                        continue
                    low = name.lower()
                    if any(x in low for x in ("-tts", "image", "embedding", "imagen")) or low == "aqa":
                        continue
                    found.append(name)
            else:
                found = [m.get("id", "") for m in data.get("data", []) if isinstance(m, dict)]
            return sorted({m for m in found if m})[:400]
        elif is_rate_limit_or_quota_error(r.status_code, r.text) and len(candidate_keys) > 1:
            continue
    if last_r is not None:
        raise AIError(f"HTTP {last_r.status_code} {last_r.text[:200]}")
    return []


def test() -> dict:
    """One tiny request with the settings in use, to prove the key(s), the address and the model all work."""
    ms = models()
    if not ready():
        raise ValueError("Save a service, a model and a key first.")
    out, sent, wrote = call(ms[0], 'Answer with a JSON array that holds the single string "ok".', {"type": "ARRAY", "items": {"type": "STRING"}})
    cur = key()
    all_k = keys()
    return {
        "ok": True,
        "model": ms[0],
        "tokens": sent + wrote,
        "answer": str(out)[:80],
        "active_key": cur[-4:] if len(cur) >= 4 else "",
        "key_count": len(all_k),
        "message": f"Verified working with key ending in {cur[-4:]} ({len(all_k)} keys in pool with auto-failover)" if len(all_k) > 1 else "AI connected successfully!"
    }


class AIError(RuntimeError):
    """A failed AI call. `wait` is how many seconds the service asked us to wait before trying again, when it
    said so (a Retry-After header, or Gemini's retryDelay)."""
    def __init__(self, message, wait=None, daily=False):
        super().__init__(message)
        self.wait = wait
        self.daily = daily        # the limit is for the whole day, so waiting a minute won't help


problem = {"text": "", "at": 0.0}       # why the AI last failed, for the dashboard; cleared when it answers again


def explain(e) -> str:
    """What went wrong with an AI call, in words the owner can act on."""
    text, low = str(e), str(e).lower()
    name = (models() or ["?"])[0]
    if "api key" in low or "api_key" in low or "unauthorized" in low or "401" in text or "403" in text or "permission" in low:
        return f"{label()} refused the key. Paste a working key under Settings, AI."
    if "no longer available to new users" in low or "retired" in low:
        return f"{label()} says the model \"{name}\" is retired. Open Settings, AI, press Find models and pick a newer one."
    if (text.startswith("HTTP 404") or " 404 " in text) and "model" in low and any(w in low for w in ("not found", "does not exist", "unknown", "not supported")):
        return f"{label()} doesn't know the model \"{name}\". Open Settings, AI, press Find models and pick one from the list."
    if "429" in text or "quota" in low or "rate limit" in low or "exhausted" in low:
        pool_len = len(keys())
        if pool_len > 1:
            return f"{label()} says all {pool_len} keys in pool have hit their rate limit or quota. Waiting for cooldown."
        return f"{label()} says the key has hit its limit or has no credit left. Check the account with {label()}, add another key, or try again later."
    if "connect" in low or "timed out" in low or "timeout" in low or "getaddrinfo" in low or "refused" in low or "nodename" in low or "servname" in low or "nameresolutionerror" in low or "name resolution" in low:
        return f"PeakCut couldn't reach {label()}. Check the internet connection" + (" and that Ollama is running." if provider() == "ollama" else ".")
    return ""


def note_problem(e):
    why = explain(e)
    if why:
        problem.update(text=why, at=time.time())


def clear_problem():
    problem.update(text="", at=0.0)


def asked_wait(r) -> float | None:
    """How long the service asked us to wait, in seconds, or None when it didn't say."""
    try:
        v = (r.headers.get("retry-after") or "").strip()
        if v:
            return max(0.0, float(v))
    except (ValueError, AttributeError):
        pass
    m = re.search(r'"retryDelay"\s*:\s*"(\d+(?:\.\d+)?)s"', getattr(r, "text", "") or "")
    return float(m.group(1)) if m else None


def _fail(r, model):
    text = r.text[:300]
    for k in keys():
        if k:
            text = text.replace(k, "<key>")
    limited = r.status_code in (429, 503)
    raise AIError(f"HTTP {r.status_code} {text}", wait=asked_wait(r) if limited else None,
                  daily=limited and bool(re.search(r"PerDay|per day|daily", r.text or "", re.I)))


# ---------------------------------------------------------------- the schema, said in words for chat models
def _json_schema(s):
    """Gemini's schema spelling (ARRAY, OBJECT...) as ordinary JSON Schema."""
    if isinstance(s, dict):
        return {k: (v.lower() if k == "type" and isinstance(v, str) else _json_schema(v)) for k, v in s.items()}
    if isinstance(s, list):
        return [_json_schema(x) for x in s]
    return s


def _wrapped(prompt, schema):
    return (prompt + "\n\nAnswer with JSON only, no other text and no code fences: one object with a single key "
            "\"items\", whose value follows this JSON Schema:\n" + json.dumps(_json_schema(schema)))


def _json_chunks(text: str):
    """Every balanced {...} or [...] in the text, in the order they appear."""
    out, depth, start, in_str, esc = [], 0, None, False, False
    for i, ch in enumerate(text):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch in "{[":
            if depth == 0:
                start = i
            depth += 1
        elif ch in "}]":
            depth -= 1
            if depth == 0 and start is not None:
                out.append(text[start:i + 1])
                start = None
            elif depth < 0:
                depth = 0
    return out


def _parse(text):
    """The JSON in an answer, even if the model wrapped it in a code fence or a sentence."""
    text = (text or "").strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
    out = None
    try:
        out = json.loads(text)
    except ValueError:
        for chunk in _json_chunks(text):
            try:
                out = json.loads(chunk)
                break
            except ValueError:
                continue
        if out is None:
            m = re.search(r"[\[{].*[\]}]", text, re.S)
            if not m:
                raise AIError("The AI did not answer with JSON.")
            try:
                out = json.loads(m.group(0))
            except ValueError:
                raise AIError("The AI did not answer with JSON.")
    if isinstance(out, dict) and "items" in out:
        out = out["items"]
    return out


# ---------------------------------------------------------------- one call
def call(model: str, prompt: str, schema: dict, timeout: float | None = None):
    """Ask one model. Returns (the parsed JSON answer, tokens sent, tokens written back)."""
    how = PROVIDERS[provider()][2]
    return {"gemini": _gemini, "openai": _openai, "anthropic": _anthropic}[how](model, prompt, schema, timeout)


def see(prompt: str, image: bytes, timeout: float | None = None) -> tuple[str, int, int]:
    """Ask one model about one picture: (the answer as text, tokens in, tokens out) with multi-key failover."""
    if not ready() or not image or not models():
        return "", 0, 0
    model = models()[0]
    b64 = base64.b64encode(image).decode()
    how = PROVIDERS[provider()][2]
    key_pool = [k for k in get_ordered_keys() if k] or [""]

    if how == "gemini":
        body = {"contents": [{"role": "user", "parts": [
            {"text": prompt},
            {"inline_data": {"mimeType": "image/jpeg", "data": b64}}]}]}
        last_r = None
        for attempt, k in enumerate(key_pool):
            try:
                r = httpx.post(f"{base_url()}/{model}:generateContent", json=body,
                               headers={"x-goog-api-key": k}, timeout=timeout or 120)
                if r.status_code == 200:
                    mark_key_success(k)
                    data = r.json()
                    text = "".join(p.get("text", "") for p in data["candidates"][0]["content"]["parts"])
                    u = data.get("usageMetadata", {})
                    sent = int(u.get("promptTokenCount") or 0)
                    return text, sent, max(0, int(u.get("totalTokenCount") or 0) - sent)
                last_r = r
                if is_rate_limit_or_quota_error(r.status_code, r.text):
                    mark_key_cooldown(k, 60.0, f"see HTTP {r.status_code}")
                    if attempt < len(key_pool) - 1:
                        continue
                _fail(r, model)
            except (httpx.RequestError, httpx.TimeoutException) as e:
                mark_key_cooldown(k, 30.0, str(e))
                if attempt < len(key_pool) - 1:
                    continue
        if last_r is not None:
            _fail(last_r, model)
        return "", 0, 0

    if how == "anthropic":
        body = {"model": model, "max_tokens": 300, "messages": [{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": b64}},
            {"type": "text", "text": prompt}]}]}
        last_r = None
        for attempt, k in enumerate(key_pool):
            try:
                r = httpx.post(f"{base_url()}/messages", json=body, timeout=timeout or 120,
                               headers={"x-api-key": k, "anthropic-version": "2023-06-01"})
                if r.status_code == 200:
                    mark_key_success(k)
                    data = r.json()
                    text = "".join(p.get("text", "") for p in data.get("content") or [] if p.get("type") == "text")
                    u = data.get("usage") or {}
                    return text, int(u.get("input_tokens") or 0), int(u.get("output_tokens") or 0)
                last_r = r
                if is_rate_limit_or_quota_error(r.status_code, r.text):
                    mark_key_cooldown(k, 60.0, f"see HTTP {r.status_code}")
                    if attempt < len(key_pool) - 1:
                        continue
                _fail(r, model)
            except (httpx.RequestError, httpx.TimeoutException) as e:
                mark_key_cooldown(k, 30.0, str(e))
                if attempt < len(key_pool) - 1:
                    continue
        if last_r is not None:
            _fail(last_r, model)
        return "", 0, 0

    last_r = None
    body = {"model": model, "stream": False, "messages": [{"role": "user", "content": [
        {"type": "text", "text": prompt},
        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + b64}}]}]}
    for attempt, k in enumerate(key_pool):
        headers = {"Authorization": f"Bearer {k}"} if k else {}
        try:
            r = httpx.post(f"{base_url()}/chat/completions", json=body, headers=headers, timeout=timeout or 120)
            if r.status_code == 200:
                mark_key_success(k)
                data = _openai_body(r)
                text = (data["choices"][0]["message"].get("content") or "")
                u = data.get("usage") or {}
                return text, int(u.get("prompt_tokens") or 0), int(u.get("completion_tokens") or 0)
            last_r = r
            if is_rate_limit_or_quota_error(r.status_code, r.text):
                mark_key_cooldown(k, 60.0, f"see HTTP {r.status_code}")
                if attempt < len(key_pool) - 1:
                    continue
            _fail(r, model)
        except (httpx.RequestError, httpx.TimeoutException) as e:
            mark_key_cooldown(k, 30.0, str(e))
            if attempt < len(key_pool) - 1:
                continue
    if last_r is not None:
        _fail(last_r, model)
    return "", 0, 0


def _gemini(model, prompt, schema, timeout=None):
    """Execute Gemini generateContent with automatic multi-key failover and quota/spike retry."""
    body = {"contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.4, "responseMimeType": "application/json", "responseSchema": schema}}
    key_pool = [k for k in get_ordered_keys() if k]
    if not key_pool:
        raise AIError("No Gemini API key available. Paste a working key under Settings, AI.")

    clean_model = model.split("/")[-1] if model.startswith("models/") else model
    last_r = None
    last_err = None
    for attempt, k in enumerate(key_pool):
        try:
            r = httpx.post(f"{base_url()}/{clean_model}:generateContent", json=body,
                           headers={"x-goog-api-key": k}, timeout=timeout or 120)
            if r.status_code == 200:
                mark_key_success(k)
                data = r.json()
                text = "".join(p.get("text", "") for p in data["candidates"][0]["content"]["parts"])
                u = data.get("usageMetadata", {})
                sent = int(u.get("promptTokenCount") or 0)
                return json.loads(text), sent, max(0, int(u.get("totalTokenCount") or 0) - sent)

            last_r = r
            err_text = r.text
            if r.status_code == 400 and any(s in err_text for s in ("JSON mode is not enabled", "response_schema", "responseSchema")):
                fallback_body = {"contents": [{"role": "user", "parts": [{"text": _wrapped(prompt, schema)}]}]}
                r2 = httpx.post(f"{base_url()}/{clean_model}:generateContent", json=fallback_body,
                                headers={"x-goog-api-key": k}, timeout=timeout or 120)
                if r2.status_code == 200:
                    mark_key_success(k)
                    data = r2.json()
                    text = "".join(p.get("text", "") for p in data["candidates"][0]["content"]["parts"])
                    u = data.get("usageMetadata", {})
                    sent = int(u.get("promptTokenCount") or 0)
                    return _parse(text), sent, max(0, int(u.get("totalTokenCount") or 0) - sent)
                last_r = r2
                err_text = r2.text
            is_limit = is_rate_limit_or_quota_error(r.status_code, err_text)
            is_model_unavail = "no longer available to new users" in err_text.lower()
            if is_limit or is_model_unavail:
                mark_key_cooldown(k, 60.0 if is_limit else 300.0, f"HTTP {r.status_code}: {err_text[:80]}")
                if attempt < len(key_pool) - 1:
                    print(f"[AI Pool] Rotating to next key (attempt {attempt + 2}/{len(key_pool)})...")
                    continue
            _fail(r, model)
        except (httpx.RequestError, httpx.TimeoutException) as e:
            last_err = e
            mark_key_cooldown(k, 30.0, f"Network timeout/error: {e}")
            if attempt < len(key_pool) - 1:
                continue
            raise AIError(f"Network error contacting Gemini: {e}")

    if last_r is not None:
        _fail(last_r, model)
    if last_err is not None:
        raise AIError(f"Failed to reach Gemini: {last_err}")


def _openai_body(r):
    """The answer, whether the service sent plain JSON or an event stream."""
    try:
        data = r.json()
    except ValueError:
        data = _from_events(r.text)
    for ch in data.get("choices") or []:
        msg = ch.get("message") or {}
        if (msg.get("content") or "").strip():
            continue
        for cl in msg.get("tool_calls") or []:
            args = (cl.get("function") or {}).get("arguments")
            if args:
                msg["content"] = args
                break
    return data


def _from_events(text: str) -> dict:
    """Read an answer out of a server-sent event stream."""
    parts, usage, calls = [], {}, {}
    for line in (text or "").splitlines():
        line = line.strip()
        if not line.startswith("data:"):
            continue
        chunk = line[5:].strip()
        if not chunk or chunk == "[DONE]":
            continue
        try:
            d = json.loads(chunk)
        except ValueError:
            continue
        usage = d.get("usage") or usage
        for ch in d.get("choices") or []:
            for piece in ((ch.get("message") or {}), (ch.get("delta") or {})):
                if piece.get("content"):
                    parts.append(piece["content"])
                for cl in piece.get("tool_calls") or []:
                    i = cl.get("index", 0)
                    calls[i] = calls.get(i, "") + ((cl.get("function") or {}).get("arguments") or "")
    message = {"content": "".join(parts)}
    if not message["content"] and calls:
        message["content"] = "".join(calls.values())
    return {"choices": [{"message": message}], "usage": usage}


def _openai(model, prompt, schema, timeout=None):
    """Execute OpenAI-compatible chat completion with multi-key failover."""
    body = {"model": model, "messages": [{"role": "user", "content": _wrapped(prompt, schema)}], "stream": False}
    extras = [{"temperature": 0.4, "response_format": {"type": "json_object"}}, {"response_format": {"type": "json_object"}}, {}]
    key_pool = [k for k in get_ordered_keys() if k] or [""]

    last_r = None
    for attempt, k in enumerate(key_pool):
        headers = {"Authorization": f"Bearer {k}"} if k else {}
        r = None
        for extra in extras:
            try:
                r = httpx.post(f"{base_url()}/chat/completions", json={**body, **extra}, headers=headers, timeout=timeout or 180)
                if r.status_code not in (400, 422):
                    break
            except (httpx.RequestError, httpx.TimeoutException):
                break
        if r is not None and r.status_code == 200:
            mark_key_success(k)
            data = _openai_body(r)
            u = data.get("usage") or {}
            return _parse(data["choices"][0]["message"].get("content")), int(u.get("prompt_tokens") or 0), int(u.get("completion_tokens") or 0)
        last_r = r
        if r is not None and is_rate_limit_or_quota_error(r.status_code, r.text):
            mark_key_cooldown(k, 60.0, f"HTTP {r.status_code}")
            if attempt < len(key_pool) - 1:
                continue
        if r is not None:
            _fail(r, model)
    if last_r is not None:
        _fail(last_r, model)
    raise AIError("AI service failed to respond.")


def _anthropic(model, prompt, schema, timeout=None):
    """Execute Anthropic message creation with multi-key failover."""
    body = {"model": model, "max_tokens": 8192, "messages": [{"role": "user", "content": _wrapped(prompt, schema)}]}
    key_pool = [k for k in get_ordered_keys() if k] or [""]

    last_r = None
    for attempt, k in enumerate(key_pool):
        try:
            r = httpx.post(f"{base_url()}/messages", json=body, timeout=timeout or 180,
                           headers={"x-api-key": k, "anthropic-version": "2023-06-01"})
            if r.status_code == 200:
                mark_key_success(k)
                data = r.json()
                text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
                u = data.get("usage") or {}
                return _parse(text), int(u.get("input_tokens") or 0), int(u.get("output_tokens") or 0)
            last_r = r
            if is_rate_limit_or_quota_error(r.status_code, r.text):
                mark_key_cooldown(k, 60.0, f"HTTP {r.status_code}")
                if attempt < len(key_pool) - 1:
                    continue
            _fail(r, model)
        except (httpx.RequestError, httpx.TimeoutException) as e:
            mark_key_cooldown(k, 30.0, str(e))
            if attempt < len(key_pool) - 1:
                continue
    if last_r is not None:
        _fail(last_r, model)
    raise AIError("AI service failed to respond.")

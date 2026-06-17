#!/usr/bin/env python3
"""Model-agnostic completion over an OpenAI-compatible Chat Completions API.

stdlib only (urllib). Default target is OpenRouter; point base_url at a local
Ollama/vLLM endpoint for a fully self-hosted, non-US path.

  from provider import complete, ProviderError
  text = complete("deepseek/deepseek-v4-flash", [{"role":"user","content":"..."}])

Env:
  OPENROUTER_API_KEY (or MYINC_API_KEY)  — bearer token
  MYINC_BASE_URL                         — override base url (e.g. local Ollama)
"""
import json
import os
import urllib.error
import urllib.request

DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"


class ProviderError(RuntimeError):
    pass


def _base_url():
    return os.environ.get("MYINC_BASE_URL", DEFAULT_BASE_URL).rstrip("/")


def _api_key():
    return os.environ.get("OPENROUTER_API_KEY") or os.environ.get("MYINC_API_KEY") or ""


def complete(model, messages, base_url=None, api_key=None,
             temperature=0, max_tokens=1500, timeout=60):
    base_url = (base_url or _base_url()).rstrip("/")
    api_key = api_key if api_key is not None else _api_key()
    is_local = "localhost" in base_url or "127.0.0.1" in base_url

    if not api_key and not is_local:
        raise ProviderError(
            "No API key. Set OPENROUTER_API_KEY (or MYINC_API_KEY), or point "
            "MYINC_BASE_URL at a local Ollama/vLLM endpoint."
        )

    payload = json.dumps({
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }).encode("utf-8")

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = "Bearer " + api_key
    # OpenRouter etiquette headers (harmless elsewhere).
    headers.setdefault("HTTP-Referer", "https://github.com/plugtheliam/myinc-os")
    headers.setdefault("X-Title", "myinc-os-harness")

    req = urllib.request.Request(base_url + "/chat/completions", data=payload,
                                 headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8")
        except Exception:
            pass
        hint = ""
        if "No allowed providers" in body or "no allowed providers" in body.lower():
            hint = ("\nHINT: OpenRouter account privacy is blocking providers. "
                    "Allow them at https://openrouter.ai/settings/privacy")
        raise ProviderError("HTTP %s from %s: %s%s" % (e.code, base_url, body[:400], hint))
    except urllib.error.URLError as e:
        raise ProviderError("Network error reaching %s: %s" % (base_url, e))

    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        raise ProviderError("Unexpected response shape: " + json.dumps(data)[:400])


if __name__ == "__main__":
    import sys
    model = sys.argv[1] if len(sys.argv) > 1 else "deepseek/deepseek-v4-flash"
    prompt = sys.argv[2] if len(sys.argv) > 2 else "Reply with the single word OK."
    try:
        print(complete(model, [{"role": "user", "content": prompt}], max_tokens=50))
    except ProviderError as e:
        print("ProviderError: " + str(e))
        sys.exit(1)

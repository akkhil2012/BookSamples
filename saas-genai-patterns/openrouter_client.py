"""
Shared OpenRouter client — used by every pattern example.

OpenRouter exposes an OpenAI-compatible /chat/completions endpoint,
so one tiny helper is all we need.

    export OPENROUTER_API_KEY=sk-or-...
"""

import os
import requests

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

DEFAULT_MODEL = "openai/gpt-4o-mini"   # cheap default; override per call


def chat(messages, model=DEFAULT_MODEL, api_key=None, **kwargs) -> str:
    """Minimal chat completion call. Returns the assistant text."""
    resp = requests.post(
        OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {api_key or API_KEY}",
            "Content-Type": "application/json",
        },
        json={"model": model, "messages": messages, **kwargs},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


if __name__ == "__main__":
    print(chat([{"role": "user", "content": "Say hello in one line."}]))

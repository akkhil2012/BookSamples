"""
PATTERN 3 — Model gateway / abstraction layer

One routing layer over many models, handling:
  * per-tenant model selection (enterprise pins a model)
  * cost-based routing (simple queries -> cheap model)
  * failover (primary fails -> fallback model)

OpenRouter is convenient here: one API key, many providers,
so the "gateway" is just routing logic.
"""

from openrouter_client import chat

# Per-tenant policy: which model tier each customer is entitled to.
TENANT_MODEL_POLICY = {
    "acme":   {"cheap": "openai/gpt-4o-mini",        "smart": "anthropic/claude-sonnet-4.5"},
    "globex": {"cheap": "meta-llama/llama-3.1-8b-instruct", "smart": "openai/gpt-4o"},
}

FALLBACK_MODEL = "openai/gpt-4o-mini"


def classify_complexity(prompt: str) -> str:
    """Toy router: long or analytical prompts go to the smart tier.
    (In production: a small classifier or confidence-gated routing.)"""
    hard_words = {"analyze", "compare", "design", "architecture", "why"}
    if len(prompt.split()) > 40 or set(prompt.lower().split()) & hard_words:
        return "smart"
    return "cheap"


def gateway_chat(tenant_id: str, prompt: str) -> str:
    tier = classify_complexity(prompt)
    model = TENANT_MODEL_POLICY[tenant_id][tier]
    print(f"[gateway] tenant={tenant_id} tier={tier} model={model}")
    try:
        return chat([{"role": "user", "content": prompt}], model=model)
    except Exception as e:
        print(f"[gateway] primary failed ({e}); failing over to {FALLBACK_MODEL}")
        return chat([{"role": "user", "content": prompt}], model=FALLBACK_MODEL)


if __name__ == "__main__":
    print(gateway_chat("acme", "What is 2+2?"))
    print()
    print(gateway_chat("acme", "Compare event-driven and request-driven architecture for billing."))

"""
PATTERN 8 — Data minimization / BYO-key

Regulated tenants demand: minimize what leaves the boundary.
Three techniques in one example:
  1. BYO-key   : the tenant's own OpenRouter key is used (their account,
                 their data-processing agreement, their controls).
  2. Minimize  : strip PII and send only the fields the task needs.
  3. Local-first: if the task can be answered locally (rules/SLM),
                 nothing egresses at all.
"""

import re
import os
from openrouter_client import chat

TENANTS = {
    # cloud_ok tenants use the platform key; regulated tenants bring their own
    "acme":   {"cloud_ok": True,  "api_key": None},
    "pharmco": {"cloud_ok": True, "api_key": os.environ.get("PHARMCO_OPENROUTER_KEY")},
    "bankco": {"cloud_ok": False, "api_key": None},   # zero egress allowed
}


def minimize(record: dict) -> dict:
    """Send only what the task needs; drop/blank direct identifiers."""
    allowed_fields = {"complaint", "product", "order_age_days"}
    return {k: v for k, v in record.items() if k in allowed_fields}


def local_answer(record: dict) -> str | None:
    """Local-first tier: deterministic rules / on-device SLM.
    Returns an answer without any network egress when possible."""
    if record["order_age_days"] <= 30 and "broken" in record["complaint"].lower():
        return "Eligible for replacement under 30-day policy. (answered locally)"
    return None


def handle_ticket(tenant_id: str, record: dict) -> str:
    tenant = TENANTS[tenant_id]

    # Tier 1: try to answer without egress
    if (answer := local_answer(record)):
        return answer

    # Tier 2: cloud LLM — only if allowed, only minimized data, tenant's key
    if not tenant["cloud_ok"]:
        return "[no-egress tenant] escalating to human queue instead of cloud LLM."

    safe_record = minimize(record)
    return chat(
        [{"role": "user", "content":
          f"Suggest a resolution for this support ticket: {safe_record}"}],
        api_key=tenant["api_key"],          # BYO-key if the tenant provided one
    )


if __name__ == "__main__":
    ticket = {
        "customer_name": "Rahul Sharma",          # never leaves the boundary
        "email": "rahul@example.com",             # never leaves the boundary
        "complaint": "Screen arrived broken",
        "product": "Tablet X2",
        "order_age_days": 12,
    }
    print("acme  :", handle_ticket("acme", ticket))     # answered locally!
    ticket2 = {**ticket, "complaint": "Wants to change billing cycle", "order_age_days": 90}
    print("bankco:", handle_ticket("bankco", ticket2))  # no egress -> human queue
    print("acme  :", handle_ticket("acme", ticket2))    # minimized -> cloud

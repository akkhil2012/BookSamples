"""
PATTERN 6 — AI audit trail

Log every AI interaction: who, when, model, prompt, retrieved context, output.
Bonus: hash-chain each record to the previous one (append-only,
tamper-evident) — the same idea as an HMAC-signed audit journal.
"""

import hashlib
import json
from datetime import datetime, timezone
from openrouter_client import chat, DEFAULT_MODEL

AUDIT_LOG = []   # in production: append-only store (WORM bucket, ledger table)


def _hash_record(record: dict, prev_hash: str) -> str:
    payload = json.dumps(record, sort_keys=True) + prev_hash
    return hashlib.sha256(payload.encode()).hexdigest()


def audited_chat(tenant_id: str, user_id: str, prompt: str, context: list[str]) -> str:
    output = chat([
        {"role": "system", "content": "Context:\n" + "\n".join(context)},
        {"role": "user", "content": prompt},
    ])

    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "tenant_id": tenant_id,
        "user_id": user_id,
        "model": DEFAULT_MODEL,
        "prompt": prompt,
        "retrieved_context": context,
        "output": output,
    }
    prev_hash = AUDIT_LOG[-1]["hash"] if AUDIT_LOG else "GENESIS"
    AUDIT_LOG.append({"record": record, "hash": _hash_record(record, prev_hash)})
    return output


def verify_chain() -> bool:
    """Recompute the chain; any edited record breaks every hash after it."""
    prev = "GENESIS"
    for entry in AUDIT_LOG:
        if _hash_record(entry["record"], prev) != entry["hash"]:
            return False
        prev = entry["hash"]
    return True


if __name__ == "__main__":
    audited_chat("acme", "ravi", "Summarize our refund policy.",
                 ["Refunds allowed within 30 days."])
    audited_chat("acme", "meera", "Draft a support macro for late delivery.", [])

    print(f"log entries : {len(AUDIT_LOG)}")
    print(f"chain valid : {verify_chain()}")

    # Tamper with history -> verification fails
    AUDIT_LOG[0]["record"]["output"] = "edited after the fact"
    print(f"after tamper: {verify_chain()}")

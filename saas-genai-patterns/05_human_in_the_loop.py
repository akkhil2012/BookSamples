"""
PATTERN 5 — Human-in-the-loop escalation

AI drafts; a human approves before any customer-facing ACTION executes.
Rule of thumb: reads can be autonomous, writes need a gate —
and every approval decision is logged for audit.
"""

import json
from datetime import datetime, timezone
from openrouter_client import chat

APPROVAL_LOG = []          # in production: an audit table / append-only journal
REQUIRES_APPROVAL = {"issue_refund", "send_customer_email", "change_contract"}


def execute_action(action: str, payload: dict):
    print(f"[EXECUTED] {action} -> {payload}")


def propose_and_gate(action: str, customer_msg: str):
    # 1. AI drafts the action content
    draft = chat([
        {"role": "system",
         "content": f"Draft the content for action '{action}'. Be brief and professional."},
        {"role": "user", "content": customer_msg},
    ])
    print(f"\n--- AI DRAFT for '{action}' ---\n{draft}\n")

    # 2. Gate: human approves or rejects (here via console input)
    if action in REQUIRES_APPROVAL:
        decision = input("Approve this action? (y/n): ").strip().lower()
        approved = decision == "y"
    else:
        approved = True   # low-risk actions can auto-execute

    # 3. Log the decision — the gate is only useful if it's auditable
    APPROVAL_LOG.append({
        "ts": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "approved": approved,
        "draft": draft,
    })

    # 4. Execute only after approval
    if approved:
        execute_action(action, {"content": draft})
    else:
        print("[REJECTED] Action not executed.")


if __name__ == "__main__":
    propose_and_gate(
        "issue_refund",
        "Customer says the product arrived broken and wants their money back.",
    )
    print("\nApproval log:")
    print(json.dumps(APPROVAL_LOG, indent=2))

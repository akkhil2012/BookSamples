"""
PATTERN 2 — RAG-per-tenant with permission-aware retrieval

Beyond the tenant boundary, retrieval must respect ENTITLEMENTS:
a user must not retrieve via AI what they cannot see in the UI.

Rule demonstrated: filter by (tenant_id AND user's allowed ACL groups)
BEFORE the LLM ever sees the text.
"""

from openrouter_client import chat

# Documents carry an ACL just like the source system does.
DOCS = [
    {"tenant_id": "acme", "acl": ["employee"], "text": "Office wifi password process: raise IT ticket."},
    {"tenant_id": "acme", "acl": ["hr"],       "text": "CONFIDENTIAL: Planned layoffs of 5% in Q3."},
    {"tenant_id": "acme", "acl": ["finance"],  "text": "CONFIDENTIAL: Q2 revenue was $4.2M, below plan."},
]

USERS = {
    "ravi":  {"tenant_id": "acme", "groups": ["employee"]},
    "meera": {"tenant_id": "acme", "groups": ["employee", "hr"]},
}


def permission_aware_retrieve(user: dict, query: str):
    """Both filters are hard filters, applied at retrieval time."""
    return [
        d["text"] for d in DOCS
        if d["tenant_id"] == user["tenant_id"]                 # tenant boundary
        and set(d["acl"]) & set(user["groups"])                # entitlement check
    ]


def ask(username: str, question: str) -> str:
    user = USERS[username]
    context = permission_aware_retrieve(user, question)
    return chat([
        {"role": "system", "content":
            "Answer only from the context. If it's not in the context, say "
            "'I don't have access to that information.'\n\nContext:\n"
            + "\n".join(f"- {c}" for c in context)},
        {"role": "user", "content": question},
    ])


if __name__ == "__main__":
    q = "Are any layoffs planned?"
    print("ravi  (employee)    :", ask("ravi", q))    # should NOT know
    print("meera (employee+hr) :", ask("meera", q))   # allowed to know

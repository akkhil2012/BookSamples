"""
PATTERN 1 — Copilot embedded in the workflow (tenant-scoped RAG)

The universal SaaS copilot pattern:
  user question -> retrieve ONLY that tenant's documents -> ground the LLM.

Key rule demonstrated: tenant_id is a HARD filter in retrieval.
Cross-tenant leakage through a shared store is the #1 failure mode.
"""

from openrouter_client import chat

# --- A shared document store (like one vector DB used by all tenants) ------
DOCUMENT_STORE = [
    {"tenant_id": "acme",  "text": "Acme refund policy: refunds allowed within 30 days."},
    {"tenant_id": "acme",  "text": "Acme support hours: 9am-6pm IST, Mon-Fri."},
    {"tenant_id": "globex", "text": "Globex refund policy: NO refunds, store credit only."},
    {"tenant_id": "globex", "text": "Globex support hours: 24x7 via chat."},
]


def retrieve(tenant_id: str, query: str, k: int = 2):
    """Toy retriever: keyword overlap scoring.
    The important part is the WHERE clause: tenant_id must match, always."""
    query_words = set(query.lower().split())
    scored = [
        (len(query_words & set(doc["text"].lower().split())), doc)
        for doc in DOCUMENT_STORE
        if doc["tenant_id"] == tenant_id          # <-- HARD tenant boundary
    ]
    scored.sort(key=lambda s: s[0], reverse=True)
    return [doc["text"] for _, doc in scored[:k]]


def tenant_copilot(tenant_id: str, question: str) -> str:
    context = retrieve(tenant_id, question)
    return chat([
        {"role": "system", "content":
            "You are a support copilot. Answer ONLY from the provided context. "
            "If the context does not contain the answer, say you don't know.\n\n"
            "Context:\n" + "\n".join(f"- {c}" for c in context)},
        {"role": "user", "content": question},
    ])


if __name__ == "__main__":
    q = "What is the refund policy?"
    # Same question, different tenants -> different grounded answers.
    print("ACME  :", tenant_copilot("acme", q))
    print("GLOBEX:", tenant_copilot("globex", q))

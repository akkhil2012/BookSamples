# AI/GenAI Patterns Now Standard in SaaS — Simple Python Examples

Minimal, runnable examples (OpenRouter API) — one file per pattern.
Each file is deliberately small so the pattern is the star, not the plumbing.

## Setup

```bash
pip install requests
export OPENROUTER_API_KEY=sk-or-...
python 01_tenant_scoped_copilot.py
```

## The Patterns

| # | File | Pattern | The one rule it demonstrates |
|---|------|---------|------------------------------|
| 1 | `01_tenant_scoped_copilot.py` | Copilot embedded in workflow | `tenant_id` is a **hard filter** in retrieval — never a soft one |
| 2 | `02_permission_aware_rag.py` | RAG-per-tenant, permission-aware | A user can't retrieve via AI what they can't see in the UI |
| 3 | `03_model_gateway.py` | Model gateway / abstraction | Route by cost & tenant policy; fail over gracefully |
| 4 | `04_guardrails_middleware.py` | Guardrails as middleware | PII redaction + injection checks sit *between* app and model, per-tenant configurable |
| 5 | `05_human_in_the_loop.py` | Human-in-the-loop escalation | Reads can be autonomous; **writes need an approval gate** — and the gate is logged |
| 6 | `06_ai_audit_trail.py` | AI audit trail | Log prompt + context + model + output; hash-chain makes it tamper-evident |
| 7 | `07_agent_scoped_tools.py` | Agentic workflow (capability-scoped) | Governance = **constrain the tools**, not filter the output (MCP-style) |
| 8 | `08_data_minimization.py` | Data minimization / BYO-key | Local-first tier → minimized fields → tenant's own key; zero-egress tenants never hit the cloud |

## The pattern behind the patterns

Every example re-uses the same four platform primitives SaaS already has:
**tenant isolation, entitlements, metering-ready logging, and audit.**
AI features shouldn't invent new governance — they should inherit it.

> Educational examples only: retrievers are toy keyword matchers, stores are
> in-memory dicts, and "auth" is a lookup table. In production you'd use a
> vector DB with namespace isolation, a policy engine (OPA/Cedar), signed
> capability tokens, and an append-only audit store.

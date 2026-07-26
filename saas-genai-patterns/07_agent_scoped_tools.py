"""
PATTERN 7 — Agentic workflow with capability-scoped tools

The agent calls the platform's own APIs — but governance shifts from
"filter the output" to "constrain the tools":
the agent only ever SEES the tools its capability token allows.

This is the MCP-style idea: authorization decides the toolset,
not a post-hoc filter on what the model said.
"""

import json
from openrouter_client import chat

# --- Platform "APIs" --------------------------------------------------------
def get_order_status(order_id: str) -> str:
    return f"Order {order_id}: shipped, arriving Tuesday."

def issue_refund(order_id: str) -> str:
    return f"Refund issued for order {order_id}."

TOOL_REGISTRY = {
    "get_order_status": {"fn": get_order_status, "desc": "Get status of an order. arg: order_id"},
    "issue_refund":     {"fn": issue_refund,     "desc": "Issue a refund. arg: order_id"},
}

# Capability token: which tools this session is ALLOWED to use.
CAPABILITY_TOKENS = {
    "support_readonly": ["get_order_status"],                  # tier-1 agent
    "support_full":     ["get_order_status", "issue_refund"],  # supervisor
}


def run_agent(capability: str, user_msg: str) -> str:
    allowed = CAPABILITY_TOKENS[capability]
    # The model is only TOLD about tools it is entitled to call.
    tool_docs = "\n".join(f"- {name}: {TOOL_REGISTRY[name]['desc']}" for name in allowed)

    decision = chat([
        {"role": "system", "content":
            "You are a support agent. Available tools:\n" + tool_docs + "\n\n"
            'Reply ONLY with JSON: {"tool": <name or null>, "arg": <string or null>, '
            '"reply": <message to user>}'},
        {"role": "user", "content": user_msg},
    ])
    plan = json.loads(decision.replace("```json", "").replace("```", "").strip())

    tool = plan.get("tool")
    if tool:
        if tool not in allowed:               # defense in depth: enforce again
            return f"[denied] capability '{capability}' cannot call '{tool}'"
        result = TOOL_REGISTRY[tool]["fn"](plan["arg"])
        return f"{plan['reply']}\n[tool result] {result}"
    return plan["reply"]


if __name__ == "__main__":
    msg = "Order 123 arrived damaged. Refund me now."
    print("READ-ONLY session:\n", run_agent("support_readonly", msg))
    print("\nFULL session:\n", run_agent("support_full", msg))

<!-- What this file is: The exact inputs, outputs and errors of the three MCP tools. -->
# Contract: MCP tools

Contract tests snapshot the server's tool list (names, descriptions, input schemas). Any unplanned
change fails CI (FR-014). Exact shapes below are the target; the snapshot becomes the source of truth
after the first passing run.

| Tool | Input | Output | Side effect | Default access |
|---|---|---|---|---|
| `get_expense_report` | `report_id` (string, `EXP-NNNN`) | the synthetic report | none | reader, auditor |
| `get_policy_clause` | `clause_id` (string, `POL-NNN`) | clause id, title, text | none | reader, auditor |
| `flag_expense_report` | `report_id`, `reason` (1–500 chars) | `flag_id`, status `flagged` | inserts one flag record | auditor only |

## Common behaviour (all tools)

1. Token is verified first. Missing, bad or unknown token → refused, outcome `denied`, reason
   `unauthenticated`.
2. Tool not on the agent's allow-list → refused, outcome `denied`, reason `not_permitted`.
3. Unknown tool name → refused, outcome `denied`, reason `unknown_tool`.
4. Input is validated; extra fields rejected; invalid → error `invalid_input`, outcome `failed`
   with reason `invalid_input`, no side effect.
5. Every outcome writes one span and one audit entry. If the audit write fails the call returns
   `audit_unavailable` and any pending change is rolled back.

## Error shape

```json
{"error": "not_permitted", "message": "Agent 'reader' may not call 'flag_expense_report'", "run_id": "..."}
```

Error codes: `unauthenticated`, `not_permitted`, `unknown_tool`, `invalid_input`, `not_found`,
`audit_unavailable`, `internal_error`.

## Demo agent profiles

- `reader`: `get_expense_report`, `get_policy_clause`
- `auditor`: all three tools

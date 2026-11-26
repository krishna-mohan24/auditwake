# Data Model: 001

Plain-language notes in italics for beginners.

## Config (files, not database)

**AgentProfile** (`config/agents.yaml`)
- `name` (unique), `description`, `allowed_tools` (list of tool names), `token_sha256` (hex).
- Rules: unknown tool names in `allowed_tools` fail startup; raw tokens never stored.
- *A profile says who an agent is and what it may call. Only the hash of its secret is kept.*

**ExpenseReport** (`data/reports.json`, synthetic)
- `report_id`, `submitter` (fake name), `submitter_email` (fake), `status`,
  `items[]` = {`category`, `amount`, `currency`, `date`, `note`}, `payment_number` (fake test number).
- Read-only. Never modified.

**PolicyClause** (`data/policy.json`, synthetic)
- `clause_id`, `title`, `text`.

## Database tables (Postgres)

**runs**
- `run_id` (text, = trace id, primary key), `agent`, `status` in {`running`, `completed`,
  `completed_with_denials`, `failed`}, `started_at`, `finished_at`.

**audit_entries** (append-only)
- `seq` bigint identity primary key (defines chain order)
- `ts` timestamptz, `run_id` (indexed), `agent` (verified name or `unknown`), `tool`,
  `outcome` in {`allowed`, `denied`, `failed`}, `reason` (short text), `input_summary` (jsonb, already
  redacted), `duration_ms`, `prev_hash` (hex), `entry_hash` (hex, unique)
- Indexes: `run_id`, `ts` (for retention and listing).
- Protections: trigger rejects UPDATE and DELETE; app role has INSERT and SELECT only.
- Chain rule: `entry_hash = SHA256(canonical_json(entry fields without entry_hash) + prev_hash)`;
  first entry uses a fixed genesis `prev_hash`.
- *Canonical JSON means sorted keys and no extra spaces, so the same data always hashes the same.*

**flags**
- `flag_id` identity, `report_id`, `reason`, `agent`, `run_id`, `created_at`. Duplicate flags allowed.
- Written in the same transaction as its audit entry.

**chain_checkpoints** (for retention)
- `through_seq`, `entry_hash`, `created_at`. Before pruning entries older than 90 days, the hash of the
  last pruned entry is saved here so verification can start from the checkpoint.

## Audit entry input summary (what is stored)

| Tool | Stored in `audit_entries.input_summary` |
|---|---|
| `get_expense_report` | `report_id` |
| `get_policy_clause` | `clause_id` |
| `flag_expense_report` | `report_id` and `reason` with personal data replaced by placeholders (`[NAME]`, `[EMAIL]`, `[PHONE]`, `[CARD]`) |

Tool results are never stored in the audit entry; only the outcome and reason code are. Unknown tools
store the tool name only.

## State transitions

- Run: `running` → `completed` | `completed_with_denials` | `failed`. A denial moves the run towards
  `completed_with_denials` but never stops it.
- Audit entry: created once, never changes.

## Validation rules (from spec)

- `report_id`: pattern like `EXP-0001`; `clause_id`: pattern like `POL-001`; `reason`: 1–500 chars.
- Unknown fields in tool input are rejected.
- Oversized input (over 10 KB) is rejected before any logic runs.

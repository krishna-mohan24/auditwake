# Contract: audit log and verification

## Entry (as stored and hashed)

```json
{
  "seq": 42,
  "ts": "2026-11-26T18:00:00.123Z",
  "run_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "agent": "reader",
  "tool": "flag_expense_report",
  "outcome": "denied",
  "reason": "not_permitted",
  "input_summary": {"report_id": "EXP-0007", "reason": "[REDACTED]"},
  "duration_ms": 3,
  "prev_hash": "…64 hex…",
  "entry_hash": "…64 hex…"
}
```

- `entry_hash = SHA-256( canonical_json(all fields except entry_hash) )` where `prev_hash` is one of
  those fields, so each entry commits to the one before it.
- Canonical JSON: UTF-8, keys sorted, separators `,` and `:`, no whitespace.
- Tokens, raw personal data and raw tool results never appear in an entry.

## Verification command

`auditwake verify-log [--from-checkpoint]`

- Walks entries in `seq` order, recomputes each hash, checks `prev_hash` links and that `seq` has no gaps.
- Output when intact: `OK: N entries verified`, exit code 0.
- Output when broken: `BROKEN at seq=K: <reason>` (hash mismatch, link mismatch, or missing seq),
  exit code 1.

## Guarantees and limits (say this honestly in docs)

- Detects edits, deletions and reordering of past entries by someone who does not also recompute the
  whole chain.
- Does **not** stop an attacker who controls the database and rewrites everything. Periodic external
  checkpoint hashes are a later improvement, not part of 001.

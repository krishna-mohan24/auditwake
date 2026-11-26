# Glossary

Plain-language definitions. Add a term here the first time a doc or task uses it.

| Term | Meaning |
|---|---|
| Agent | A program that asks an AI model what to do next and uses tools to do it |
| MCP | Model Context Protocol: a standard way for agents to find and call tools |
| Tool | A small function an agent may call, such as "get expense report" |
| Allow-list | The tools one agent is permitted to call; everything else is refused |
| Token (credential) | A secret string an agent presents to prove who it is |
| Hash | A fixed-length fingerprint of data; the same input always gives the same hash |
| Hash chain | Each log entry includes the previous entry's hash, so editing history breaks the chain |
| Audit log | Append-only record of every tool call: who, what, when, outcome |
| Trace / span | A trace is the story of one run; a span is one step in it with timing |
| OpenTelemetry (OTel) | Open standard for producing traces and logs |
| OTLP | The protocol OTel uses to send spans to a backend |
| Redaction | Replacing personal data with placeholders before it is stored |
| Fake provider | A scripted stand-in for the AI model so tests need no keys or cost |
| Eval | A fixed set of test cases scoring behaviour the same way each time |
| Baseline | The saved eval score a change must not drop below |
| Advisory lock | A Postgres lock our code takes so only one writer extends the chain at a time |
| Fail closed | When a safety check cannot run, refuse the action instead of allowing it |
| ADR | Architecture Decision Record: a short note explaining a major choice |
| Run id | One identifier for a whole agent run; equals the trace id |
| Luhn check | A checksum that tells real card-number patterns from random digits |
| Migration | A versioned change to the database structure |
| Trigger | Code the database runs automatically when rows change |
| Transaction | Several database writes that all succeed or all fail together |
| Median / p95 | Median is the middle value; p95 means 95% of calls were faster than this |
| SLI / SLO | A measured quality of the service / the target for it |
| STRIDE | Six threat types: Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege |
| Mutation check | Breaking the code on purpose to prove the tests or gate would catch it |
| Spike | A short experiment to remove a risk before building |
| Test pyramid | Many fast unit tests, fewer integration tests, very few end-to-end tests |
| Threshold | The minimum score a check must reach to pass |
| Constant-time compare | Comparing secrets so timing does not leak how much matched |
| Canonical JSON | JSON with sorted keys and no extra spaces so the same data always hashes the same |

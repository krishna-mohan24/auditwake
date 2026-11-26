# Developer tooling (optional, local-only)

These tools help the person *building* Auditwake. They are **not** part of the product, add no
dependencies to the Python code, and nothing in the repo requires them.

## Rules

- **Optional.** The project must build, test and run without any of them (constitution XI).
- **Measure, don't trust vendor claims.** Savings figures below are the vendors' own. Record only
  numbers measured with CodeBurn on our own sessions, labelled with date and tool version
  (constitution IX). Until then, no number goes in this file.
- **Verify before installing.** Use the official repo path only. Third-party plugins and proxies
  run code on this machine; look-alike forks exist. Check the date and source before installing
  anything new, and record it here.
- **One change at a time.** Install one tool, use it for a few sessions, compare, then decide.

## Tools

| Tool | What it does | Install (official source) | Status |
|---|---|---|---|
| CodeBurn | Shows where Claude Code tokens and money go, by project, model and task | `brew install codeburn`; Claude Code plugin: `/plugin install codeburn --marketplace getagentseal/codeburn` ([repo](https://github.com/getagentseal/codeburn)) | Installed |
| Ponytail | Nudges the agent to write the smallest working solution | `/plugin marketplace add DietrichGebert/ponytail`, then (separate prompt) `/plugin install ponytail@ponytail` ([repo](https://github.com/DietrichGebert/ponytail)) | Planned |
| Headroom | Local proxy that compresses context before it is sent to the model | `uv tool install --python 3.13 "headroom-ai[all]"`, then `headroom wrap claude` ([repo](https://github.com/chopratejas/headroom)) | Planned, try after Ponytail |

## Cautions

- **Ponytail vs teaching.** Terse output conflicts with constitution XII (beginner-friendly).
  Use `lite` or `/ponytail off` when writing specs, docs, tasks and explanations.
- **Headroom is a proxy** in the path of all model traffic. First try it in a single throwaway
  session (`headroom wrap` is session-scoped; `headroom unwrap claude` undoes durable wrapping).
  Open question: whether it works with a subscription login or needs an API key.
- **Do not run `codeburn guard install`** without review; it edits Claude Code hooks.

## Measurement log

| Date | Tool + version | Baseline (CodeBurn) | With tool (CodeBurn) | Notes |
|---|---|---|---|---|
| _none yet_ | | | | |

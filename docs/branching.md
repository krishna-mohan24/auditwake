# Branching rule

Every change gets its own branch and a pull request. Nobody commits directly to `main`.

## Name format

```
<TYPE>-<SIDE>/<short-kebab-description>
```

| Part | Allowed values | Meaning |
|---|---|---|
| TYPE | `FEAT` | new behaviour or capability |
| | `FIX` | bug fix (must add a regression test) |
| | `DOC` | documentation, specs, ADRs only |
| SIDE | `APP` | application code, API, `/web` viewer |
| | `AGENT` | agent, tools, model access, guardrails, evals, prompts, skills |
| | `INFRA` | CI, Docker, Terraform, repo and process files |

- Pick SIDE by where most of the change lands. If it truly spans several, split it into several branches.
- Description: lowercase words joined by `-`, 2 to 5 words, no spaces, no ticket noise.
- Valid pattern: `^(FEAT|FIX|DOC)-(APP|AGENT|INFRA)/[a-z0-9]+(-[a-z0-9]+)*$`

## Examples

| Branch | Why |
|---|---|
| `FEAT-AGENT/mcp-allow-list` | new tool permission gate |
| `FEAT-APP/audit-hash-chain` | audit log code |
| `FEAT-INFRA/ci-eval-gate` | CI workflow |
| `FIX-AGENT/redact-phone-numbers` | redaction bug, adds a regression test |
| `DOC-INFRA/branch-naming-rule` | process documentation |
| `DOC-APP/threat-model` | docs describing the application |

## Commit and pull request titles (fixed format)

```
<type emoji><side emoji> <TYPE>-<SIDE>: <short summary>
```

The two emojis are fixed, not chosen freely. Branch names stay plain ASCII (no emoji) because emoji in
branch names break many tools.

| TYPE | Emoji | | SIDE | Emoji |
|---|---|---|---|---|
| `FEAT` | ✨ | | `APP` | 💻 |
| `FIX` | 🐛 | | `AGENT` | 🤖 |
| `DOC` | 📝 | | `INFRA` | 🔧 |

Examples:
- `✨🤖 FEAT-AGENT: add allow-list gate`
- `🐛🤖 FIX-AGENT: redact phone numbers in summaries`
- `📝🔧 DOC-INFRA: add commit emoji rule`

Rules enforced by the `commit-rules` pre-commit hook (`scripts/check_commit_msg.py`):
1. Subject matches the format and both emojis match the TYPE and SIDE.
2. You are not committing on `main` or a detached HEAD.
3. The branch name matches the pattern above.
4. Merge and revert commits are exempt. Attribution trailers (Co-Authored-By) go in the body.

Enable on a fresh clone: `pre-commit install && pre-commit install --hook-type commit-msg`.
The pull request title uses the same format. Changing a mapping needs a constitution amendment.

## Workflow

1. `git switch main && git pull`
2. `git switch -c FEAT-AGENT/mcp-allow-list`
3. Commit small, tests first; pre-commit (gitleaks, ruff) runs on every commit.
4. Push the branch, open a pull request, wait for CI to be green, merge, delete the branch.
5. One spec task or small group of tasks per branch, so each pull request is easy to review.

## Existing work

The first spec, plan and task commits were made before this rule existed, so they sit on `main`.
From the next change onward, the rule applies.

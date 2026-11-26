"""Commit-msg hook: enforce the fixed commit and branch rules in docs/branching.md."""

import re
import subprocess
import sys

TYPE_EMOJI = {"FEAT": "✨", "FIX": "🐛", "DOC": "📝"}
SIDE_EMOJI = {"APP": "💻", "AGENT": "🤖", "INFRA": "🔧"}

BRANCH_RE = re.compile(r"^(FEAT|FIX|DOC)-(APP|AGENT|INFRA)/[a-z0-9]+(-[a-z0-9]+)*$")
SUBJECT_RE = re.compile(r"^(\S)(\S) (FEAT|FIX|DOC)-(APP|AGENT|INFRA): (\S.{2,70})$")


def current_branch() -> str:
    out = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    return out.stdout.strip()


def check_subject(subject: str) -> str | None:
    match = SUBJECT_RE.match(subject)
    if not match:
        return "subject must look like: ✨🤖 FEAT-AGENT: short summary (3 to 71 chars after the colon)"
    type_emoji, side_emoji, commit_type, side, _ = match.groups()
    if type_emoji != TYPE_EMOJI[commit_type]:
        return (
            f"{commit_type} must use {TYPE_EMOJI[commit_type]} first, not {type_emoji}"
        )
    if side_emoji != SIDE_EMOJI[side]:
        return f"{side} must use {SIDE_EMOJI[side]} second, not {side_emoji}"
    return None


def check_branch(branch: str) -> str | None:
    if branch in ("main", "HEAD", ""):
        return f"do not commit on '{branch or 'detached HEAD'}'; create a branch (see docs/branching.md)"
    if not BRANCH_RE.match(branch):
        return f"branch '{branch}' must match <TYPE>-<SIDE>/<kebab-description>"
    return None


def main(path: str) -> int:
    with open(path, encoding="utf-8") as handle:
        lines = [
            line for line in handle.read().splitlines() if not line.startswith("#")
        ]
    subject = lines[0] if lines else ""
    if subject.startswith(("Merge ", "Revert ")):
        return 0
    problems = [
        p for p in (check_subject(subject), check_branch(current_branch())) if p
    ]
    for problem in problems:
        print(f"commit rule: {problem}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))

"""CI check: pull request branch name and title must follow docs/branching.md."""

import os
import sys

from check_commit_msg import check_branch, check_subject

# Bot branches use their own names. Dependabot commit and title prefixes are set in its config.
EXEMPT_BRANCH_PREFIXES = ("dependabot/",)


def check(head_ref: str, title: str) -> list[str]:
    """Return a list of problems (empty when the branch and title are valid)."""
    if head_ref.startswith(EXEMPT_BRANCH_PREFIXES):
        return []
    problems = [check_branch(head_ref), check_subject(title)]
    return [problem for problem in problems if problem]


def main() -> int:
    head_ref = os.environ.get("HEAD_REF", "")
    title = os.environ.get("PR_TITLE", "")
    problems = check(head_ref, title)
    for problem in problems:
        print(f"::error::{problem}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

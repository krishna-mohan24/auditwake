"""Tests for the branch, commit and pull request title rules (docs/branching.md)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

import check_commit_msg as rules
import check_pr_meta as pr_meta

GOOD_BRANCHES = [
    "FEAT-AGENT/mcp-allow-list",
    "FIX-APP/redact-phone-numbers",
    "DOC-INFRA/branch-naming-rule",
]
BAD_BRANCHES = [
    "main",
    "feature/x",
    "feat-agent/lowercase-type",
    "FEAT-AGENT/Bad_Name",
    "FEAT-WEB/unknown-side",
    "FEAT-AGENT/",
]
GOOD_SUBJECTS = [
    "✨🤖 FEAT-AGENT: add allow-list gate",
    "🐛💻 FIX-APP: handle empty report",
    "📝🔧 DOC-INFRA: add commit emoji rule",
]
BAD_SUBJECTS = [
    "docs: old style message",
    "✨💻 FEAT-AGENT: wrong side emoji",
    "🐛🤖 FEAT-AGENT: wrong type emoji",
    "✨🤖 FEAT-AGENT: no",
    "✨🤖 FEAT-AGENT:missing space",
]


@pytest.mark.parametrize("branch", GOOD_BRANCHES)
def test_good_branch_names_pass(branch: str) -> None:
    assert rules.check_branch(branch) is None


@pytest.mark.parametrize("branch", BAD_BRANCHES)
def test_bad_branch_names_fail(branch: str) -> None:
    assert rules.check_branch(branch) is not None


@pytest.mark.parametrize("subject", GOOD_SUBJECTS)
def test_good_subjects_pass(subject: str) -> None:
    assert rules.check_subject(subject) is None


@pytest.mark.parametrize("subject", BAD_SUBJECTS)
def test_bad_subjects_fail(subject: str) -> None:
    assert rules.check_subject(subject) is not None


def test_pr_meta_accepts_valid_branch_and_title() -> None:
    assert (
        pr_meta.check("DOC-INFRA/branch-naming-rule", "📝🔧 DOC-INFRA: add rule") == []
    )


def test_pr_meta_reports_both_problems() -> None:
    problems = pr_meta.check("my-branch", "bad title")
    assert len(problems) == 2


def test_pr_meta_exempts_dependabot_branches() -> None:
    assert pr_meta.check("dependabot/pip/ruff-0.18", "📝🔧 DOC-INFRA: bump ruff") == []

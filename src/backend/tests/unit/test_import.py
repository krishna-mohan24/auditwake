"""T001: the package imports and its version matches the packaging metadata."""

from importlib.metadata import version

import auditwake_backend


def test_package_has_version() -> None:
    assert auditwake_backend.__version__


def test_version_matches_packaging_metadata() -> None:
    assert auditwake_backend.__version__ == version("auditwake-backend")

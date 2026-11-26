"""ADR-0011: the agents project can import the backend project (one-way dependency)."""

import auditwake_agents
import auditwake_backend


def test_agents_can_import_backend() -> None:
    assert auditwake_agents is not None
    assert auditwake_backend.__version__

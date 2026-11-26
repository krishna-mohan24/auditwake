"""Check that the local services from infra/compose.yaml are reachable (T003).

Run after `docker compose -f infra/compose.yaml up -d`. Exits 1 if any service is down.
"""

import os
import socket
import sys
import urllib.request

POSTGRES_PORT = int(os.environ.get("POSTGRES_PORT", "55432"))
JAEGER_UI_PORT = int(os.environ.get("JAEGER_UI_PORT", "16686"))


def postgres_up(port: int) -> bool:
    """True if something accepts TCP connections on the Postgres port."""
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=3):
            return True
    except OSError:
        return False


def jaeger_up(port: int) -> bool:
    """True if the Jaeger UI answers with HTTP 200."""
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=3) as resp:
            return resp.status == 200
    except OSError:
        return False


def main() -> int:
    checks = {
        f"Postgres on port {POSTGRES_PORT}": postgres_up(POSTGRES_PORT),
        f"Jaeger UI on port {JAEGER_UI_PORT}": jaeger_up(JAEGER_UI_PORT),
    }
    for name, ok in checks.items():
        print(f"{'OK  ' if ok else 'FAIL'} {name}")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    sys.exit(main())

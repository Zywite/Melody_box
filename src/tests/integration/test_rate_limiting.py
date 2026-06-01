import subprocess
import sys
from pathlib import Path


def test_rate_limits_standalone():
    """Run rate limiting tests in a fresh Python process (avoids module caching issues)."""
    script = Path(__file__).parent.parent / "scripts" / "rate_limit_standalone.py"
    result = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True, text=True, timeout=60,
    )
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
    assert result.returncode == 0, (
        f"Rate limit tests failed (exit={result.returncode})\n"
        f"{result.stdout}\n{result.stderr}"
    )

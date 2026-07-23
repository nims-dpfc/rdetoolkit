"""Coverage-policy contract for new v2 code.

EP table:

| Configuration | Partition | Expected | Test ID |
| --- | --- | --- | --- |
| ``tool.coverage.run`` | repository coverage settings | branch measurement enabled | TC-EP-HR-F6-001 |

BV table:

| Configuration | Boundary | Expected | Test ID |
| --- | --- | --- | --- |
| ``branch`` | boolean true | no truthy string surrogate | TC-BV-HR-F6-001 |
"""

from pathlib import Path
import tomllib


def test_branch_coverage_is_enabled__tc_ep_hr_f6_001() -> None:
    """TC-EP/BV-HR-F6-001: coverage measures branches with a real boolean."""
    # Given: the repository's canonical Python tool configuration
    root = Path(__file__).resolve().parents[2]
    config = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))

    # When: reading the coverage runtime policy
    branch = config["tool"]["coverage"]["run"].get("branch")

    # Then: branch measurement is explicitly enabled as a boolean
    assert branch is True

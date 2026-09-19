"""Protect monitoring from silently choosing old beta or withdrawn releases."""
from packaging.version import Version
from scripts.compatibility_matrix import python_version, released_versions


def test_release_selection_excludes_yanked_and_empty():
    versions = released_versions({"releases": {
        "2026.8.0": [{"yanked": False}],
        "2026.9.0b1": [{"yanked": False}],
        "2026.9.0": [{"yanked": False}],
        "2026.10.0b1": [{"yanked": True}],
        "2026.10.0": [],
        "2026.11.0.dev0": [{"yanked": False}],
    }})
    assert versions == [Version("2026.8.0"), Version("2026.9.0b1"), Version("2026.9.0")]
    assert not [v for v in versions if v.is_prerelease and v > Version("2026.9.0")]


def test_python_requirement():
    assert python_version(">=3.14.2") == "3.14"

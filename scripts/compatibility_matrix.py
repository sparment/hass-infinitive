"""Resolve exact HA releases and their Python requirements for scheduled CI."""
import json
import os
import re
import sys
import tomllib
from urllib.request import Request, urlopen

from packaging.version import Version


def fetch(url):
    request = Request(url, headers={"User-Agent": "hass-infinitive-compatibility"})
    with urlopen(request, timeout=30) as response:
        return response.read()


def python_version(requirement):
    match = re.search(r">=\s*(\d+\.\d+)(?:\.\d+)?", requirement)
    if not match:
        raise ValueError(f"Unrecognized HA Python requirement: {requirement}")
    return match[1]


def released_versions(data):
    return sorted(
        Version(version) for version, files in data["releases"].items()
        if files and any(not item.get("yanked", False) for item in files)
        and not Version(version).is_devrelease
    )


def main():
    entries = []
    if "--dev" in sys.argv or "--all" in sys.argv:
        commit = json.loads(fetch("https://api.github.com/repos/home-assistant/core/commits/dev"))["sha"]
        metadata = tomllib.loads(fetch(
            f"https://raw.githubusercontent.com/home-assistant/core/{commit}/pyproject.toml"
        ).decode())
        entries.append({"channel": "development", "version": commit,
                        "python": python_version(metadata["project"]["requires-python"]),
                        "package": f"https://github.com/home-assistant/core/archive/{commit}.zip"})
    if "--dev" not in sys.argv:
        versions = released_versions(json.loads(fetch("https://pypi.org/pypi/homeassistant/json")))
        stable = max(version for version in versions if not version.is_prerelease)
        candidates = [("stable", stable)]
        upcoming = [version for version in versions if version.is_prerelease and version > stable]
        if upcoming:
            candidates.append(("beta", max(upcoming)))
        else:
            print("No newer prerelease is published; stable alone will run.", file=sys.stderr)
        for channel, version in candidates:
            info = json.loads(fetch(f"https://pypi.org/pypi/homeassistant/{version}/json"))["info"]
            entries.append({"channel": channel, "version": str(version),
                            "python": python_version(info["requires_python"]),
                            "package": f"homeassistant=={version}"})
    matrix = json.dumps({"include": entries})
    print(matrix)
    if output := os.environ.get("GITHUB_OUTPUT"):
        with open(output, "a") as stream:
            stream.write(f"matrix={matrix}\n")


if __name__ == "__main__":
    main()

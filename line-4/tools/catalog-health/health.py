"""Validate basic referential health of a finite dependency catalog."""
import json
import sys
from pathlib import Path


def inspect_catalog(catalog):
    if not isinstance(catalog, dict) or not isinstance(catalog.get("packages"), dict):
        raise ValueError("catalog must contain an object named packages")
    packages = catalog["packages"]
    missing = []
    releases = 0
    for name, versions in packages.items():
        if not isinstance(name, str) or not name.strip() or not isinstance(versions, dict):
            raise ValueError("package names and release maps must be non-empty objects")
        for version, metadata in versions.items():
            if not isinstance(version, str) or not version.strip() or not isinstance(metadata, dict):
                raise ValueError("release labels and metadata must be non-empty objects")
            dependencies = metadata.get("dependencies", [])
            if not isinstance(dependencies, list) or any(not isinstance(d, str) or not d.strip() for d in dependencies):
                raise ValueError("dependencies must be a list of strings")
            releases += 1
            for dependency in dependencies:
                target = dependency.split()[0]
                if target not in packages:
                    missing.append({"package": name, "version": version, "dependency": target})
    return {"packages": len(packages), "releases": releases,
            "missing_dependency_targets": missing, "healthy": not missing}


def main(argv):
    if len(argv) == 2 and argv[1] == "demo":
        catalog = {"packages": {"alpha": {"1": {"dependencies": ["beta >=1"]}},
                                "beta": {"1": {"dependencies": []}}}}
    elif len(argv) == 2:
        try:
            catalog = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(json.dumps({"error": str(exc)}))
            return 2
    else:
        print("usage: health.py demo|CATALOG.json")
        return 2
    try:
        print(json.dumps(inspect_catalog(catalog), sort_keys=True))
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

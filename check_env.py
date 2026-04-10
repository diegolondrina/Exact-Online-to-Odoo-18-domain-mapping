#!/usr/bin/env python3
"""Environment check for the Exact Online -> Odoo 18 mapping project.

Run manually to verify the environment before starting work:

    python check_env.py

The check is purely informational: it reports problems but never blocks
any workflow.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REQUIRED_PACKAGES: list[tuple[str, str]] = [
    ("openpyxl", "generate_workbook.py, format_workbooks.py"),
    ("requests", "Exact_REST_API_scraper.py"),
    ("bs4", "Exact_REST_API_scraper.py (pip package: beautifulsoup4)"),
]

REQUIRED_DIRS: list[str] = [
    "metadata/exact",
    "metadata/odoo",
    "mappings/data",
    "references",
    ".claude/skills/new-domain",
    ".claude/skills/map",
    ".claude/skills/quality-gate",
    ".claude/skills/deliver",
]

REQUIRED_FILES: list[str] = [
    "CLAUDE.md",
    "README.md",
    "requirements.txt",
    ".claude/skills/new-domain/SKILL.md",
    ".claude/skills/map/SKILL.md",
    ".claude/skills/quality-gate/SKILL.md",
    ".claude/skills/deliver/SKILL.md",
    "generate_workbook.py",
    "format_workbooks.py",
    "Exact_REST_API_scraper.py",
]


def find_project_root() -> Path:
    """Walk up from this script to find the repo root (identified by CLAUDE.md)."""
    here = Path(__file__).resolve().parent
    for candidate in [here, *here.parents]:
        if (candidate / "CLAUDE.md").exists():
            return candidate
    # Fallback: assume cwd is the root. The REQUIRED_FILES check will catch
    # the mistake and surface a clear error to the user.
    return Path.cwd()


def check_packages() -> list[str]:
    missing: list[str] = []
    for pkg, used_by in REQUIRED_PACKAGES:
        if importlib.util.find_spec(pkg) is None:
            missing.append(f"{pkg}  (used by {used_by})")
    return missing


def check_paths(root: Path) -> tuple[list[str], list[str]]:
    missing_dirs = [d for d in REQUIRED_DIRS if not (root / d).is_dir()]
    missing_files = [f for f in REQUIRED_FILES if not (root / f).is_file()]
    return missing_dirs, missing_files


def main() -> int:
    root = find_project_root()
    missing_pkgs = check_packages()
    missing_dirs, missing_files = check_paths(root)

    bar = "=" * 60
    print(bar)
    print("Exact Online to Odoo 18 mapping project")
    print(f"Project root: {root}")
    print(f"Python:       {sys.version.split()[0]}")
    print(bar)

    ok = not (missing_pkgs or missing_dirs or missing_files)

    if ok:
        print("Environment check: OK")
        print("  - Python packages installed: openpyxl, requests, beautifulsoup4")
        print("  - Project structure: all required directories and files present")
        print("  - Skills available: /new-domain, /map, /quality-gate, /deliver")
        print()
        print("Ready to work. Say hello, describe the domain you want to map,")
        print("or invoke a skill directly with its slash command.")
        return 0

    print("Environment check: ISSUES FOUND")
    if missing_pkgs:
        print()
        print("Missing Python packages:")
        for p in missing_pkgs:
            print(f"  - {p}")
        print("  Fix: pip install -r requirements.txt")
    if missing_dirs:
        print()
        print("Missing directories:")
        for d in missing_dirs:
            print(f"  - {d}/")
    if missing_files:
        print()
        print("Missing files:")
        for f in missing_files:
            print(f"  - {f}")
        print("  If CLAUDE.md or skill files are missing, you may have opened")
        print("  Claude Code in the wrong directory. Confirm you are inside")
        print("  the cloned Exact-Online-to-Odoo-18-domain-mapping repo.")
    print()
    print("The session will continue, but some workflows may fail until the")
    print("issues above are resolved.")
    return 0  # informational only — never block the session


if __name__ == "__main__":
    sys.exit(main())

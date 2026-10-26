#!/usr/bin/env python3
"""Check a bisman-automations integration repo against the shared standards.

Usage:
    python scripts/check_repo.py PATH_TO_REPO [--github]

Run it from a checkout of bisman-automations/.github (CI does this in the
"standards" job of ha-validate.yml). It needs only the Python standard library.

Each finding is an error (the repo is out of step and CI fails) or a warning
(worth a look, CI stays green). --github prints them as workflow annotations.

What "in step" means is written down in this repo's README.md ("Standards")
and the files under templates/repo/. When you change a standard, change the
template, this checker and the README together, then bring every repo along.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

ORG = "bisman-automations"
OWNER = "@donavanbecker"

# The thin caller workflows every repo has, and the shared workflow each calls.
CALLERS = {
    "test.yml": "ha-test.yml",
    "validate.yml": "ha-validate.yml",
    "draft-release.yml": "ha-draft-release.yml",
    "release-check.yml": "ha-release-check.yml",
}

# Workflow files from the older per-repo layouts, replaced by the callers.
RETIRED_WORKFLOWS = {
    "ci.yml",
    "hacs.yml",
    "hassfest.yml",
    "label-pr.yml",
    "release.yml",
    "tests.yml",
    "validate.yaml",
}

REQUIRED_FILES = [
    ".github/CODEOWNERS",
    ".github/dependabot.yml",
    ".gitignore",
    "AGENTS.md",
    "CHANGELOG.md",
    "CLAUDE.md",
    "LICENSE",
    "README.md",
    "hacs.json",
    "pyproject.toml",
    "requirements_test.txt",
    "requirements_test_min.txt",
]

# Files replaced by the standard ones (pytest.ini -> pyproject.toml,
# requirements.txt -> requirements_test.txt) or by the org-wide defaults in
# bisman-automations/.github (issue and PR templates, release categories,
# CONTRIBUTING, SECURITY and SUPPORT). Repo-specific advice that used to live in
# those files belongs in the README (users) or CLAUDE.md (contributors).
RETIRED_FILES = [
    "pytest.ini",
    "requirements.txt",
    ".github/release.yml",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/ISSUE_TEMPLATE",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "SUPPORT.md",
]

HACS_KEYS = ["name", "homeassistant", "render_readme"]
HACS_OPTIONAL = {"hacs", "zip_release", "filename", "hide_default_branch", "country"}

GITIGNORE_REQUIRED = [
    "__pycache__/",
    ".pytest_cache/",
    ".ruff_cache/",
    ".mypy_cache/",
    ".coverage",
    ".venv/",
    ".DS_Store",
    ".env",
]

KAC_INTRO = (
    "The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)"
)
SHARED_BEGIN = "<!-- BEGIN bisman-automations shared rules -->"
SHARED_END = "<!-- END bisman-automations shared rules -->"
README_SECTIONS = ["Installation", "Setup", "Troubleshooting", "Development", "License"]
LICENSE_MIN_LINES = 15  # A full MIT text is 21 lines; Apache-2.0 is ~200.


class Report:
    """Collects findings and prints them."""

    def __init__(self, github: bool) -> None:
        self.github = github
        self.name = ""
        self.errors = 0
        self.warnings = 0

    def error(self, path: str, message: str) -> None:
        self.errors += 1
        self._print("error", path, message)

    def warning(self, path: str, message: str) -> None:
        self.warnings += 1
        self._print("warning", path, message)

    def _print(self, level: str, path: str, message: str) -> None:
        if self.github:
            print(f"::{level} file={path}::{message}")
        else:
            print(f"{level.upper():7} {path}: {message}")


def load_json(path: Path, report: Report, rel: str) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as err:
        report.error(rel, f"can't read as JSON: {err}")
        return None


def flatten(data: object, prefix: str = "") -> set[str]:
    """Return every leaf key path in a translations dict."""
    if isinstance(data, dict):
        keys: set[str] = set()
        for key, value in data.items():
            keys |= flatten(value, f"{prefix}{key}.")
        return keys
    return {prefix.rstrip(".")}


def check_layout(repo: Path, report: Report) -> None:
    for rel in REQUIRED_FILES:
        if not (repo / rel).exists():
            report.error(
                rel, "missing (see templates/repo in bisman-automations/.github)"
            )
    for rel in RETIRED_FILES:
        if (repo / rel).exists():
            report.error(rel, "replaced by the shared standard; remove it")


def check_workflows(repo: Path, report: Report) -> None:
    folder = repo / ".github" / "workflows"
    present = {p.name for p in folder.glob("*")} if folder.is_dir() else set()
    for caller, shared in CALLERS.items():
        rel = f".github/workflows/{caller}"
        if caller not in present:
            report.error(rel, "missing caller workflow")
            continue
        text = (folder / caller).read_text(encoding="utf-8")
        target = f"uses: {ORG}/.github/.github/workflows/{shared}@main"
        if target not in text:
            report.error(
                rel, f"should call {ORG}/.github/.github/workflows/{shared}@main"
            )
    for name in sorted(present & RETIRED_WORKFLOWS):
        report.error(
            f".github/workflows/{name}",
            "replaced by the shared caller workflows; remove it",
        )
    for name in sorted(present - set(CALLERS) - RETIRED_WORKFLOWS):
        report.warning(
            f".github/workflows/{name}",
            "not one of the standard workflows; is it still needed?",
        )

    dependabot = repo / ".github" / "dependabot.yml"
    if dependabot.exists():
        text = dependabot.read_text(encoding="utf-8")
        for ecosystem in ("github-actions", "pip"):
            if (
                f'package-ecosystem: "{ecosystem}"' not in text
                and f"package-ecosystem: {ecosystem}" not in text
            ):
                report.error(".github/dependabot.yml", f"no {ecosystem} updates")
        if "pytest-homeassistant-custom-component" not in text:
            report.error(
                ".github/dependabot.yml",
                "must ignore pytest-homeassistant-custom-component (the minimum pin is deliberate)",
            )

    codeowners = repo / ".github" / "CODEOWNERS"
    if codeowners.exists() and OWNER not in codeowners.read_text(encoding="utf-8"):
        report.error(".github/CODEOWNERS", f"should assign {OWNER}")


def check_integration(repo: Path, report: Report) -> tuple[str | None, dict | None]:
    manifests = sorted((repo / "custom_components").glob("*/manifest.json"))
    if len(manifests) != 1:
        report.error(
            "custom_components", f"expected one integration, found {len(manifests)}"
        )
        return None, None
    manifest_path = manifests[0]
    domain = manifest_path.parent.name
    rel = f"custom_components/{domain}/manifest.json"
    manifest = load_json(manifest_path, report, rel)
    if manifest is None:
        return domain, None

    keys = list(manifest)
    expected = [
        "domain",
        "name",
        *sorted(k for k in keys if k not in ("domain", "name")),
    ]
    if keys != expected:
        report.error(
            rel,
            "keys must be domain, name, then the rest alphabetically (hassfest order)",
        )
    if manifest.get("domain") != domain:
        report.error(
            rel,
            f"domain {manifest.get('domain')!r} doesn't match the folder {domain!r}",
        )
    if "categories" in manifest:
        report.error(rel, "remove 'categories': the published hassfest rejects it")
    if any(
        str(r).lower().startswith("pillow") for r in manifest.get("requirements", [])
    ):
        report.error(
            rel,
            "Pillow in requirements is rejected by hassfest; Home Assistant ships it",
        )
    if manifest.get("codeowners") != [OWNER]:
        report.error(
            rel, f"codeowners should be [{OWNER!r}] (an org handle isn't a valid owner)"
        )
    repo_name = report.name
    for key, url in (
        ("documentation", f"https://github.com/{ORG}/{repo_name}"),
        ("issue_tracker", f"https://github.com/{ORG}/{repo_name}/issues"),
    ):
        if manifest.get(key) != url:
            report.warning(rel, f"{key} is {manifest.get(key)!r}, expected {url!r}")
    version = str(manifest.get("version", ""))
    if not re.fullmatch(r"\d+\.\d+\.\d+((a|b|rc)\d+)?", version):
        report.error(rel, f"version {version!r} isn't X.Y.Z")
    for dep_key in ("dependencies", "after_dependencies"):
        deps = manifest.get(dep_key)
        if deps is not None and deps != sorted(deps):
            report.warning(rel, f"{dep_key} isn't sorted")

    # Translations: Home Assistant loads custom integration text only from
    # translations/<lang>.json, so en.json must exist and match strings.json.
    folder = manifest_path.parent
    en = folder / "translations" / "en.json"
    strings = folder / "strings.json"
    if not en.exists():
        report.error(
            f"custom_components/{domain}/translations/en.json",
            "missing: Home Assistant shows raw keys without it",
        )
    elif strings.exists():
        en_keys = flatten(load_json(en, report, "translations/en.json") or {})
        strings_keys = flatten(load_json(strings, report, "strings.json") or {})
        if en_keys != strings_keys:
            only_strings = sorted(strings_keys - en_keys)[:5]
            only_en = sorted(en_keys - strings_keys)[:5]
            report.error(
                f"custom_components/{domain}/translations/en.json",
                f"keys differ from strings.json (only in strings.json: {only_strings}; only in en.json: {only_en})",
            )
    else:
        report.error(
            f"custom_components/{domain}/strings.json",
            "missing (keep it identical to translations/en.json)",
        )

    brand = folder / "brand"
    for icon in ("icon.png", "icon@2x.png", "dark_icon.png", "dark_icon@2x.png"):
        if not (brand / icon).exists():
            report.warning(
                f"custom_components/{domain}/brand/{icon}", "missing brand image"
            )
    return domain, manifest


def check_hacs(repo: Path, report: Report) -> str | None:
    path = repo / "hacs.json"
    if not path.exists():
        return None
    data = load_json(path, report, "hacs.json")
    if data is None:
        return None
    keys = [k for k in data if k not in HACS_OPTIONAL]
    if keys != HACS_KEYS:
        report.error(
            "hacs.json",
            f"keys should be {HACS_KEYS} in that order (then optional keys)",
        )
    if data.get("render_readme") is not True:
        report.error("hacs.json", "render_readme should be true")
    minimum = str(data.get("homeassistant", ""))
    if not re.fullmatch(r"\d{4}\.\d+\.\d+", minimum):
        report.error(
            "hacs.json", f"homeassistant {minimum!r} isn't a release like 2026.3.0"
        )
        return None
    return minimum


def check_requirements(repo: Path, report: Report, minimum: str | None) -> None:
    current = repo / "requirements_test.txt"
    if current.exists():
        text = current.read_text(encoding="utf-8")
        if re.search(r"^pytest-homeassistant-custom-component\s*==", text, re.M):
            report.error(
                "requirements_test.txt",
                "leave pytest-homeassistant-custom-component unpinned here (the newest-HA job)",
            )
        if not re.search(r"^ruff==", text, re.M):
            report.error(
                "requirements_test.txt",
                "pin ruff (ruff==X.Y.Z) so lint only changes via Dependabot",
            )
    minimum_file = repo / "requirements_test_min.txt"
    if minimum_file.exists():
        text = minimum_file.read_text(encoding="utf-8")
        if not re.search(
            r"^pytest-homeassistant-custom-component==0\.13\.\d+", text, re.M
        ):
            report.error(
                "requirements_test_min.txt",
                "pin pytest-homeassistant-custom-component to the release for hacs.json's minimum",
            )
        if minimum:
            month = ".".join(minimum.split(".")[:2])
            if month not in text:
                report.warning(
                    "requirements_test_min.txt",
                    f"the comment should name the Home Assistant it pins ({month}.x, from hacs.json)",
                )

    pyproject = repo / "pyproject.toml"
    if pyproject.exists():
        text = pyproject.read_text(encoding="utf-8")
        for table in (
            "[tool.pytest.ini_options]",
            "[tool.ruff]",
            "[tool.ruff.lint]",
            "[tool.ruff.lint.isort]",
        ):
            if table not in text:
                report.error("pyproject.toml", f"missing {table}")
        if re.search(r"^\[project\]", text, re.M):
            report.error(
                "pyproject.toml",
                "no [project] table: the version lives only in manifest.json",
            )


def check_changelog(repo: Path, report: Report, version: str | None) -> None:
    path = repo / "CHANGELOG.md"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0] != "# Changelog":
        report.error("CHANGELOG.md", "first line should be '# Changelog'")
    if KAC_INTRO not in text:
        report.error(
            "CHANGELOG.md",
            "missing the Keep a Changelog 1.1.0 / Semantic Versioning intro",
        )
    if "## [Unreleased]" not in lines:
        report.error("CHANGELOG.md", "missing '## [Unreleased]'")
    headings = re.findall(r"^## \[([^\]]+)\](.*)$", text, re.M)
    for name, rest in headings:
        if name == "Unreleased":
            continue
        if not re.fullmatch(r" - \d{4}-\d{2}-\d{2}", rest):
            report.error("CHANGELOG.md", f"'## [{name}]' needs ' - YYYY-MM-DD'")
        if not re.search(rf"^\[{re.escape(name)}\]: https://github\.com/", text, re.M):
            report.error("CHANGELOG.md", f"no compare link for [{name}] at the bottom")
    if not re.search(r"^\[Unreleased\]: https://github\.com/.+/compare/", text, re.M):
        report.error("CHANGELOG.md", "no [Unreleased] compare link at the bottom")
    allowed = {"Added", "Changed", "Deprecated", "Removed", "Fixed", "Security"}
    for heading in sorted(set(re.findall(r"^### (.+)$", text, re.M)) - allowed):
        report.error(
            "CHANGELOG.md",
            f"'### {heading}' isn't a Keep a Changelog type ({', '.join(sorted(allowed))})",
        )
    if version and not any(name == version for name, _ in headings):
        report.error("CHANGELOG.md", f"no section for manifest.json version {version}")
    versions = [name for name, _ in headings if name != "Unreleased"]
    if versions and version and versions[0] != version:
        report.warning(
            "CHANGELOG.md",
            f"newest section is {versions[0]}, manifest.json says {version}",
        )


def check_readme(
    repo: Path,
    report: Report,
    domain: str | None,
    manifest: dict | None,
    minimum: str | None,
) -> None:
    path = repo / "README.md"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    name = report.name
    if "my.home-assistant.io/redirect/hacs_repository" not in text:
        report.error("README.md", "missing the HACS 'open this repository' My button")
    if (
        manifest
        and manifest.get("config_flow")
        and domain
        and f"config_flow_start/?domain={domain}" not in text
    ):
        report.error(
            "README.md", "missing the 'start setting up' (config_flow_start) My button"
        )
    badges = {
        "HACS": "img.shields.io/badge/HACS-Custom",
        "Home Assistant minimum": "img.shields.io/badge/Home%20Assistant-",
        "release": f"img.shields.io/github/v/release/{ORG}/{name}",
        "Test": f"github.com/{ORG}/{name}/actions/workflows/test.yml/badge.svg",
        "Validate": f"github.com/{ORG}/{name}/actions/workflows/validate.yml/badge.svg",
        "License": f"img.shields.io/github/license/{ORG}/{name}",
    }
    for label, needle in badges.items():
        if needle not in text:
            report.error("README.md", f"missing the {label} badge")
    if minimum:
        month = ".".join(minimum.split(".")[:2])
        if f"Home%20Assistant-{month}%2B" not in text:
            report.error(
                "README.md", f"the Home Assistant badge should say {month}+ (hacs.json)"
            )
    h2 = re.findall(r"^## (.+?)\s*$", text, re.M)
    for section in README_SECTIONS:
        if section not in h2:
            report.error("README.md", f"missing '## {section}'")


def check_docs(repo: Path, report: Report) -> None:
    claude = repo / "CLAUDE.md"
    if claude.exists():
        text = claude.read_text(encoding="utf-8")
        if SHARED_BEGIN not in text or SHARED_END not in text:
            report.error(
                "CLAUDE.md",
                "missing the shared rules block (templates/CLAUDE.shared.md)",
            )
        else:
            template = (
                Path(__file__).resolve().parent.parent
                / "templates"
                / "CLAUDE.shared.md"
            )
            if template.exists():
                shared = text[
                    text.index(SHARED_BEGIN) : text.index(SHARED_END) + len(SHARED_END)
                ]
                if shared.strip() != template.read_text(encoding="utf-8").strip():
                    report.error(
                        "CLAUDE.md",
                        "the shared rules block differs from templates/CLAUDE.shared.md",
                    )
    agents = repo / "AGENTS.md"
    if agents.exists() and "CLAUDE.md" not in agents.read_text(encoding="utf-8"):
        report.error("AGENTS.md", "should point to CLAUDE.md")

    license_path = repo / "LICENSE"
    if license_path.exists():
        text = license_path.read_text(encoding="utf-8")
        lines = [line for line in text.splitlines() if line.strip()]
        if len(lines) < LICENSE_MIN_LINES:
            report.error(
                "LICENSE",
                "looks like a stub; GitHub and HACS need the full license text",
            )
        if text.startswith("MIT License") and "Donavan Becker" not in text:
            report.warning("LICENSE", "copyright holder should be Donavan Becker")

    gitignore = repo / ".gitignore"
    if gitignore.exists():
        entries = {
            line.strip() for line in gitignore.read_text(encoding="utf-8").splitlines()
        }
        for entry in GITIGNORE_REQUIRED:
            if entry not in entries:
                report.error(".gitignore", f"missing {entry}")
    if (repo / "custom_components" / "__init__.py").exists():
        report.error("custom_components/__init__.py", "stray package marker; remove it")


def check(repo: Path, github: bool = False, name: str | None = None) -> Report:
    report = Report(github)
    report.name = name or repo.resolve().name
    check_layout(repo, report)
    check_workflows(repo, report)
    domain, manifest = check_integration(repo, report)
    minimum = check_hacs(repo, report)
    check_requirements(repo, report, minimum)
    check_changelog(repo, report, str(manifest.get("version")) if manifest else None)
    check_readme(repo, report, domain, manifest, minimum)
    check_docs(repo, report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("repo", type=Path, help="path to the integration repository")
    parser.add_argument(
        "--github", action="store_true", help="print GitHub Actions annotations"
    )
    parser.add_argument(
        "--name",
        help="repository name (default: the folder name), used for badge and manifest URLs",
    )
    args = parser.parse_args()
    report = check(args.repo, args.github, args.name)
    print(
        f"{args.name or args.repo.resolve().name}: {report.errors} error(s), {report.warnings} warning(s)"
    )
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())

"""Tests for check_repo.py.

Run from the root of this repository (CI's "Self check" workflow does):

    python -m unittest discover -s scripts -p "test_*.py" -v

Each test renders templates/repo into a temporary integration repo, the way a
new repo is started, checks that it passes, then breaks one standard and checks
that the checker reports it. That keeps the templates and the checker in step:
a template change the checker rejects (or a checker rule the templates break)
fails here first, before every integration repo's Validate run sees it.
"""

from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_repo  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "templates" / "repo"
SHARED = (ROOT / "templates" / "CLAUDE.shared.md").read_text(encoding="utf-8")

REPO = "ha-demo"
DOMAIN = "demo"
NAME = "Demo"
MINIMUM = "2026.3"
HARNESS = "0.13.320"
TRANSLATIONS = {
    "config": {
        "step": {"user": {"title": "Demo", "data": {"host": "Host"}}},
        "abort": {"already_configured": "Already configured"},
    }
}
# The smallest valid PNG, standing in for the brand images.
PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d4948445200000001000000010806000000"
    "1f15c4890000000d49444154789c6360000002000154a24f5d0000000049454e44ae426082"
)


def render(text: str) -> str:
    """Fill in the template placeholders for the demo integration."""
    return (
        text.replace("REPO", REPO)
        .replace("DOMAIN", DOMAIN)
        .replace("<domain>", DOMAIN)
        .replace("NAME", NAME)
        .replace("YYYY-MM-DD", "2026-10-26")
        .replace("YYYY.M", MINIMUM)
        .replace("0.13.NNN", HARNESS)
        .replace("3.1X", "3.14")
    )


def make_repo(parent: Path) -> Path:
    """Render templates/repo plus a minimal integration into parent/ha-demo."""
    repo = parent / REPO
    shutil.copytree(TEMPLATE, repo)
    for path in repo.rglob("*"):
        if path.is_file():
            path.write_text(render(path.read_text(encoding="utf-8")), encoding="utf-8")
    claude = repo / "CLAUDE.md"
    if check_repo.SHARED_BEGIN not in claude.read_text(encoding="utf-8"):
        claude.write_text(
            claude.read_text(encoding="utf-8") + "\n" + SHARED, encoding="utf-8"
        )

    folder = repo / "custom_components" / DOMAIN
    (folder / "translations").mkdir(parents=True)
    (folder / "brand").mkdir()
    manifest = {
        "domain": DOMAIN,
        "name": NAME,
        "codeowners": [check_repo.OWNER],
        "config_flow": True,
        "documentation": f"https://github.com/{check_repo.ORG}/{REPO}",
        "integration_type": "service",
        "iot_class": "local_polling",
        "issue_tracker": f"https://github.com/{check_repo.ORG}/{REPO}/issues",
        "requirements": [],
        "version": "1.0.0",
    }
    (folder / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    for target in (folder / "strings.json", folder / "translations" / "en.json"):
        target.write_text(json.dumps(TRANSLATIONS, indent=2) + "\n", encoding="utf-8")
    for icon in ("icon.png", "icon@2x.png", "dark_icon.png", "dark_icon@2x.png"):
        (folder / "brand" / icon).write_bytes(PNG)
    (folder / "__init__.py").write_text('"""Demo."""\n', encoding="utf-8")
    return repo


class CheckRepoTest(unittest.TestCase):
    """The rendered template passes; each broken standard is reported."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo = make_repo(Path(self._tmp.name))

    def run_check(self) -> tuple[check_repo.Report, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            report = check_repo.check(self.repo, name=REPO)
        return report, out.getvalue()

    def assert_error(self, needle: str) -> None:
        report, output = self.run_check()
        self.assertGreater(report.errors, 0, output)
        self.assertIn(needle, output)

    def edit(self, rel: str, old: str, new: str) -> None:
        path = self.repo / rel
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text, f"{rel} no longer contains {old!r}; update the test")
        path.write_text(text.replace(old, new), encoding="utf-8")

    def manifest(self) -> Path:
        return self.repo / "custom_components" / DOMAIN / "manifest.json"

    def update_manifest(self, **changes: object) -> None:
        data = json.loads(self.manifest().read_text(encoding="utf-8"))
        data.update(changes)
        self.manifest().write_text(json.dumps(data, indent=2), encoding="utf-8")

    # The baseline -----------------------------------------------------------

    def test_template_passes(self) -> None:
        report, output = self.run_check()
        self.assertEqual((report.errors, report.warnings), (0, 0), output)

    def test_github_annotations(self) -> None:
        (self.repo / "AGENTS.md").unlink()
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            check_repo.check(self.repo, github=True, name=REPO)
        self.assertIn("::error file=AGENTS.md::", out.getvalue())

    # Layout and workflows ---------------------------------------------------

    def test_missing_required_file(self) -> None:
        (self.repo / "CHANGELOG.md").unlink()
        self.assert_error("CHANGELOG.md: missing")

    def test_retired_file(self) -> None:
        (self.repo / "pytest.ini").write_text("[pytest]\n", encoding="utf-8")
        self.assert_error("pytest.ini: replaced by the shared standard")

    def test_retired_workflow(self) -> None:
        (self.repo / ".github/workflows/hassfest.yml").write_text(
            "name: x\n", encoding="utf-8"
        )
        self.assert_error("hassfest.yml: replaced by the shared caller workflows")

    def test_unknown_workflow_is_a_warning(self) -> None:
        (self.repo / ".github/workflows/extra.yml").write_text(
            "name: x\n", encoding="utf-8"
        )
        report, output = self.run_check()
        self.assertEqual((report.errors, report.warnings), (0, 1), output)

    def test_caller_must_use_shared_workflow(self) -> None:
        self.edit(".github/workflows/test.yml", "ha-test.yml@main", "ha-test.yml@v1")
        self.assert_error(
            "should call bisman-automations/.github/.github/workflows/ha-test.yml@main"
        )

    def test_dependabot_must_ignore_the_harness(self) -> None:
        self.edit(
            ".github/dependabot.yml",
            "pytest-homeassistant-custom-component",
            "something-else",
        )
        self.assert_error("must ignore pytest-homeassistant-custom-component")

    def test_codeowners(self) -> None:
        self.edit(".github/CODEOWNERS", check_repo.OWNER, "@someone")
        self.assert_error(f"should assign {check_repo.OWNER}")

    # Manifest, translations and HACS -----------------------------------------

    def test_manifest_categories_rejected(self) -> None:
        self.update_manifest(categories=["lighting"])
        self.assert_error("remove 'categories'")

    def test_manifest_pillow_rejected(self) -> None:
        self.update_manifest(requirements=["Pillow==11.0.0"])
        self.assert_error("Pillow in requirements")

    def test_manifest_org_codeowner_rejected(self) -> None:
        self.update_manifest(codeowners=["@bisman-automations"])
        self.assert_error("codeowners should be")

    def test_manifest_key_order(self) -> None:
        data = json.loads(self.manifest().read_text(encoding="utf-8"))
        reordered = {"version": data.pop("version"), **data}
        self.manifest().write_text(json.dumps(reordered), encoding="utf-8")
        self.assert_error("keys must be domain, name")

    def test_missing_en_json(self) -> None:
        (self.repo / "custom_components" / DOMAIN / "translations" / "en.json").unlink()
        self.assert_error("Home Assistant shows raw keys without it")

    def test_en_json_must_match_strings(self) -> None:
        en = self.repo / "custom_components" / DOMAIN / "translations" / "en.json"
        en.write_text(json.dumps({"config": {}}), encoding="utf-8")
        self.assert_error("keys differ from strings.json")

    def test_missing_brand_image_is_a_warning(self) -> None:
        (self.repo / "custom_components" / DOMAIN / "brand" / "dark_icon.png").unlink()
        report, output = self.run_check()
        self.assertEqual((report.errors, report.warnings), (0, 1), output)

    def test_hacs_minimum_format(self) -> None:
        self.edit("hacs.json", f"{MINIMUM}.0", MINIMUM)
        self.assert_error("isn't a release like 2026.3.0")

    # Requirements and pyproject -------------------------------------------------

    def test_newest_harness_must_be_unpinned(self) -> None:
        self.edit(
            "requirements_test.txt",
            "\npytest-homeassistant-custom-component\n",
            f"\npytest-homeassistant-custom-component=={HARNESS}\n",
        )
        self.assert_error("leave pytest-homeassistant-custom-component unpinned")

    def test_minimum_harness_must_be_pinned(self) -> None:
        self.edit("requirements_test_min.txt", f"=={HARNESS}", "")
        self.assert_error("pin pytest-homeassistant-custom-component")

    def test_pyproject_has_no_project_table(self) -> None:
        self.edit(
            "pyproject.toml",
            "[tool.pytest.ini_options]",
            '[project]\nname = "x"\n\n[tool.pytest.ini_options]',
        )
        self.assert_error("no [project] table")

    # CHANGELOG ------------------------------------------------------------------

    def test_changelog_needs_manifest_version(self) -> None:
        self.update_manifest(version="1.0.1")
        self.assert_error("no section for manifest.json version 1.0.1")

    def test_changelog_needs_date(self) -> None:
        self.edit("CHANGELOG.md", "## [1.0.0] - 2026-10-26", "## [1.0.0]")
        self.assert_error("needs ' - YYYY-MM-DD'")

    def test_changelog_types(self) -> None:
        self.edit("CHANGELOG.md", "### Added", "### New")
        self.assert_error("'### New' isn't a Keep a Changelog type")

    def test_changelog_rejects_unreleased_heading(self) -> None:
        self.edit(
            "CHANGELOG.md",
            "## [1.0.0] - 2026-10-26",
            "## [Unreleased]\n\n## [1.0.0] - 2026-10-26",
        )
        self.assert_error("remove '## [Unreleased]'")

    def test_changelog_rejects_unreleased_link(self) -> None:
        self.edit(
            "CHANGELOG.md",
            "[1.0.0]:",
            "[Unreleased]: https://github.com/bisman-automations/ha-demo/compare/v1.0.0...HEAD\n[1.0.0]:",
        )
        self.assert_error("remove the [Unreleased] compare link")

    def test_changelog_link_points_at_this_repo(self) -> None:
        self.edit(
            "CHANGELOG.md",
            "[1.0.0]: https://github.com/bisman-automations/ha-demo/",
            "[1.0.0]: https://github.com/bisman-automations/./",
        )
        self.assert_error("[1.0.0] link should start with")

    # README -----------------------------------------------------------------

    def test_readme_hacs_my_button(self) -> None:
        self.edit(
            "README.md", "my.home-assistant.io/redirect/hacs_repository", "example.com"
        )
        self.assert_error("missing the HACS 'open this repository' My button")

    def test_readme_minimum_badge_matches_hacs(self) -> None:
        self.edit("hacs.json", f"{MINIMUM}.0", "2026.4.0")
        self.assert_error("the Home Assistant badge should say 2026.4+")

    # CLAUDE.md, AGENTS.md, LICENSE, .gitignore ------------------------------------

    def test_shared_rules_must_match_template(self) -> None:
        claude = self.repo / "CLAUDE.md"
        text = claude.read_text(encoding="utf-8")
        claude.write_text(
            text.replace(check_repo.SHARED_END, "Edited.\n" + check_repo.SHARED_END),
            encoding="utf-8",
        )
        self.assert_error("the shared rules block differs")

    def test_agents_points_to_claude(self) -> None:
        (self.repo / "AGENTS.md").write_text("Agent notes.\n", encoding="utf-8")
        self.assert_error("should point to CLAUDE.md")

    def test_license_stub(self) -> None:
        (self.repo / "LICENSE").write_text(
            "Copyright 2026\n\nLicensed under the Apache License, Version 2.0.\n",
            encoding="utf-8",
        )
        self.assert_error("looks like a stub")

    def test_gitignore_entries(self) -> None:
        self.edit(".gitignore", ".ruff_cache/\n", "")
        self.assert_error("missing .ruff_cache/")

    def test_stray_package_marker(self) -> None:
        (self.repo / "custom_components" / "__init__.py").write_text(
            "", encoding="utf-8"
        )
        self.assert_error("stray package marker")


if __name__ == "__main__":
    unittest.main()

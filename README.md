# bisman-automations/.github

Shared workflows, templates and standards for every
[bisman-automations](https://github.com/bisman-automations) Home Assistant
integration. The organization profile shown on GitHub is
[`profile/README.md`](profile/README.md).

Everything here exists so the twelve integration repositories are built,
tested, documented and released the same way. A fix made here reaches every
repository: they all call these workflows at `@main`.

## Contents

| Path | What it is |
| --- | --- |
| [`.github/workflows/ha-test.yml`](.github/workflows/ha-test.yml) | Reusable tests: ruff, optional mypy, sidebar panel scripts, pytest on the oldest supported, newest and upcoming Home Assistant. |
| [`.github/workflows/ha-validate.yml`](.github/workflows/ha-validate.yml) | Reusable validation: hassfest, HACS, and the standards check (`scripts/check_repo.py`). |
| [`.github/workflows/ha-draft-release.yml`](.github/workflows/ha-draft-release.yml) | Reusable draft release: keeps a DRAFT release for the manifest version. Never publishes, never tags. |
| [`.github/workflows/ha-release-check.yml`](.github/workflows/ha-release-check.yml) | Reusable check run when a release is published (its tag is pushed). |
| [`.github/workflows/self-check.yml`](.github/workflows/self-check.yml) | CI for this repository: actionlint, ruff, and the checker's tests. |
| [`.github/ISSUE_TEMPLATE/`](.github/ISSUE_TEMPLATE), [`.github/PULL_REQUEST_TEMPLATE.md`](.github/PULL_REQUEST_TEMPLATE.md) | Organization-wide issue forms and pull request template. GitHub uses them for every repository that has none of its own. |
| [`CONTRIBUTING.md`](CONTRIBUTING.md), [`SECURITY.md`](SECURITY.md), [`SUPPORT.md`](SUPPORT.md) | Organization-wide community health files, used the same way. |
| [`scripts/check_repo.py`](scripts/check_repo.py) | The standards checker (Python standard library only). |
| [`templates/repo/`](templates/repo) | The files a new integration repository starts from; every existing repository matches them. |
| [`templates/CLAUDE.shared.md`](templates/CLAUDE.shared.md) | The shared rules block at the end of every repository's `CLAUDE.md`. |
| [`workflow-templates/`](workflow-templates) | The four caller workflows as organization starter workflows (**Actions → New workflow**). |

## Standards

What every integration repository has. `scripts/check_repo.py` checks all of
it in each repository's Validate run: errors fail the run, warnings don't.

### Layout

```
.github/
  CODEOWNERS               * @donavanbecker
  dependabot.yml           templates/repo/.github/dependabot.yml, unchanged
  workflows/
    test.yml               calls ha-test.yml@main (inputs vary per repo)
    validate.yml           calls ha-validate.yml@main
    draft-release.yml      calls ha-draft-release.yml@main
    release-check.yml      calls ha-release-check.yml@main
custom_components/<domain>/
  manifest.json            domain, name, then keys A-Z; codeowners ["@donavanbecker"]
  strings.json             identical to translations/en.json
  translations/en.json     what Home Assistant actually loads for custom integrations
  brand/                   icon.png, icon@2x.png, dark_icon.png, dark_icon@2x.png
tests/
AGENTS.md                  points to CLAUDE.md
CHANGELOG.md               Keep a Changelog 1.1.0
CLAUDE.md                  repo notes + the shared rules block
LICENSE                    full license text (MIT or Apache 2.0)
README.md                  badges, My buttons, standard sections
hacs.json                  name, homeassistant (the minimum), render_readme
pyproject.toml             pytest, ruff, mypy and coverage settings only
requirements_test.txt      newest Home Assistant: harness unpinned, ruff pinned
requirements_test_min.txt  oldest supported Home Assistant: harness pinned
```

Retired and reported as errors: `pytest.ini`, `requirements.txt`,
per-repository issue and PR templates, `.github/release.yml`, per-repository
`CONTRIBUTING.md`, `SECURITY.md` and `SUPPORT.md` (the organization defaults
here apply), and the old `ci.yml`, `tests.yml`, `hacs.yml`, `hassfest.yml`,
`release.yml`, `label-pr.yml` and `validate.yaml` workflows.

### Home Assistant versions

One rule for every repository:

- **Minimum** is `homeassistant` in `hacs.json`, and the README badge and
  Requirements say the same `YYYY.M`. `requirements_test_min.txt` pins
  `pytest-homeassistant-custom-component` to the newest harness release of
  that month, and CI fails if the pin drifts to another month. The minimum we
  advertise is the minimum we test.
- **Newest** is whatever `pytest-homeassistant-custom-component` installs
  unpinned from `requirements_test.txt`, so every run, and the Thursday
  schedule, tests the newest release.
- **Upcoming** (the beta harness) runs for information only and never fails.
- **Python:** Home Assistant 2026.3 and newer need Python 3.14. A repository
  whose minimum is 2026.2 or older sets `python-min: "3.13"`.
- Raise the minimum when code needs a newer Home Assistant, in the same change
  as `hacs.json`, the README, `requirements_test_min.txt` and a `Changed`
  CHANGELOG entry.

Harness releases for the minimums in use:

| Home Assistant | pytest-homeassistant-custom-component | Python |
| --- | --- | --- |
| 2025.3.4 | 0.13.225 | 3.13 |
| 2025.8.3 | 0.13.272 | 3.13 |
| 2025.11.3 | 0.13.297 | 3.13 |
| 2026.2.3 | 0.13.316 | 3.13 |
| 2026.3.4 | 0.13.320 | 3.14 |
| 2026.7.4 | 0.13.348 | 3.14 |
| 2026.9.4 | 0.13.367 | 3.14 |

Minimum-only pins that older Home Assistant releases need, with a comment in
`requirements_test_min.txt` saying why:

- `pycares==4.11.0` for Home Assistant 2025.x (aiodns 3 doesn't work with
  pycares 5).
- `aiohttp==3.11.13` for Home Assistant 2025.3 (it pins a release that was
  later yanked, so pip skips it unless it's named).

Dependabot ignores the harness, `homeassistant`, `aiohttp` and `pycares`, so
it never moves the minimum pins.

### Tests (`ha-test.yml`)

The caller passes only what differs from the defaults:

| Input | Default | Use |
| --- | --- | --- |
| `python` | `3.14` | Python for the newest and upcoming jobs. |
| `python-min` | `3.14` | `3.13` when the minimum is 2026.2 or older. |
| `requirements` | `requirements_test.txt` | Newest Home Assistant and lint. |
| `requirements-min` | `requirements_test_min.txt` | Oldest supported Home Assistant. |
| `core-requirements` | | Core integrations whose pip requirements the tests need (for example `frontend` or `homekit camera ffmpeg homekit_controller`), read from the installed Home Assistant so each job gets matching versions. |
| `setup` | | Extra shell run after installing, in every pytest job. |
| `pytest` | `pytest -q --cov` | The test command. |
| `pytest-next` | same as `pytest` | The command for the upcoming Home Assistant, for a wrapper that shims beta gaps. |
| `lint` | `true` | `ruff check` and `ruff format --check`. |
| `mypy` | | Paths to type-check; empty skips mypy. |
| `next` | `true` | Also test the upcoming Home Assistant. |
| `ffmpeg` | `false` | A static ffmpeg on `PATH` from imageio-ffmpeg, for tests that encode media. |

Ruff settings are the same everywhere (`templates/repo/pyproject.toml`); a
repository may add rules with `extend-select` or per-file ignores, with a
comment saying why. The scheduled Test and Validate runs are on Thursday, the
day after Home Assistant publishes betas; Dependabot proposes updates on
Mondays.

### Validation (`ha-validate.yml`)

- **hassfest**, Home Assistant's own manifest, translations and services
  checks. The published hassfest rejects `categories` in `manifest.json` and
  Pillow in `requirements`, so neither is used.
- **HACS**, every check on. `hacs-ignore` is only for a check that genuinely
  can't pass, with a comment in the caller. `hacs` defaults to `true`. Set
  it `false` only for a private repository: hacs/action refuses private repos
  before any check runs, and `hacs-ignore` cannot skip that.
- **standards**, `scripts/check_repo.py` against this repository's `main`.

The caller passes only what differs from the defaults:

| Input | Default | Use |
| --- | --- | --- |
| `hacs` | `true` | Run the HACS action. Set `false` only for a private repository: hacs/action refuses private repos before any check runs, and `hacs-ignore` cannot skip that. |
| `hacs-ignore` | | Space-separated HACS checks to skip. Empty runs them all. |
| `standards` | `true` | Run `scripts/check_repo.py`. |

### Releases

The same process in every repository. Nothing in CI publishes a release or
pushes a tag.

1. In one commit, `Release X.Y.Z`: bump `version` in
   `custom_components/<domain>/manifest.json` and move the CHANGELOG
   `## [Unreleased]` entries into `## [X.Y.Z] - YYYY-MM-DD`, with the compare
   links at the bottom.
2. Push to `main`.
3. **Draft release** creates or refreshes the DRAFT release `vX.Y.Z`:
   that version's CHANGELOG section, the commits since the previous release,
   a compare link, and `<domain>.zip` for installing without HACS.
4. Donavan reviews the draft on GitHub and publishes it. Publishing creates
   the tag.
5. **Release check** runs on the new tag and confirms it matches
   `manifest.json`, has a dated CHANGELOG section, and is on `main`.

Pushes without a version bump keep a draft for the next patch version from
the `Unreleased` notes, with a notice to bump `manifest.json` first.

**Tags are never moved, deleted or re-created**, and history on `main` is
never rewritten. Two repositories have a release tag that isn't on `main`
from before this rule: in `ha-button-actions` (`v1.0.0` to `v1.9.1`, after a
history rewrite) the draft workflow finds the commit on `main` with exactly the
same files, and in `ha-matter-bridge` (`v1.0.0`, amended after tagging) it
finds the amended copy of the tagged commit. Each repository's `CLAUDE.md`
says which.

Versions follow [Semantic Versioning](https://semver.org/): a fix or a
documentation, CI or tooling change is a patch; a new feature is a minor; a
change that needs users to act (a raised minimum Home Assistant counts when it
drops a release people use) is called out under `Changed`.

### Documentation

- **README.md**: the HACS, Home Assistant minimum, release, Test, Validate
  and License badges; the My buttons to open the repository in HACS and (for
  config-flow integrations) to start setup; and at least the `Installation`,
  `Setup`, `Troubleshooting`, `Development` and `License` sections. Start
  from `templates/repo/README.md`.
- **CHANGELOG.md**: [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/),
  `## [Unreleased]` at the top, dated sections, only the standard `###`
  types, compare links at the bottom, and a section for the manifest version.
- **CLAUDE.md**: notes for Claude and other coding agents (layout,
  conventions, checks, repository-specific release notes), ending with the
  shared rules block copied from `templates/CLAUDE.shared.md`. **AGENTS.md**
  points to it.
- **LICENSE**: the full license text, so GitHub and HACS detect it.

## Changing a standard

1. Change the template under `templates/`, `scripts/check_repo.py`, this
   README, and `scripts/test_check_repo.py` together.
2. Run the checks below and push to `main`.
3. Bring every integration repository along (their Validate runs report what's
   out of step), then release each one as usual.

Changes to the reusable workflows reach every repository at once, so keep
inputs backwards compatible: add an input with a default rather than changing
what an existing one means.

## Checks

```bash
# The checker's tests, and the checker against an integration checkout
python -m unittest discover -s scripts -p "test_*.py" -v
python scripts/check_repo.py ../ha-tv-mgmt

# Lint, as Self check runs it
pip install "$(grep -E '^ruff==' templates/repo/requirements_test.txt)"
ruff check scripts && ruff format --check scripts
actionlint .github/workflows/*.yml workflow-templates/*.yml templates/repo/.github/workflows/*.yml
```

## Starting a new integration

1. Copy `templates/repo/` (including its hidden `.github/` and
   `.gitignore`) and replace `REPO`, `DOMAIN`, `NAME`, `YYYY.M`, `0.13.NNN`,
   `3.1X` and `YYYY-MM-DD`. The caller workflows are also offered as starter
   workflows under **Actions → New workflow**.
2. Add `custom_components/<domain>/` with `manifest.json`, `strings.json`,
   `translations/en.json` and the four brand images.
3. Run `python scripts/check_repo.py ../<repo>` until it reports no errors.

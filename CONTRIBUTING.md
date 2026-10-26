# Contributing to bisman-automations

Thanks for helping. Every repository in this organization is a Home Assistant
custom integration, distributed through HACS, and they all work the same way.
This guide applies to every repo that doesn't have its own CONTRIBUTING.md
(none do).

## Reporting problems and ideas

Open an issue in the integration's repository with the bug report or feature
request form. For bugs, include the integration and Home Assistant versions
and, if you can, the diagnostics file (the integration's page > menu >
Download diagnostics). Security problems go through [SECURITY.md](SECURITY.md)
instead.

## Making a change

1. Fork the repository and create a branch.
2. Set up Python 3.14 (Home Assistant 2026.3 and newer need it) and install the
   test requirements:

   ```
   python3.14 -m venv .venv && . .venv/bin/activate
   pip install -r requirements_test.txt
   ```

3. Make the change, with tests. Keep entity IDs, unique IDs, service names and
   event names stable.
4. Run the checks CI runs:

   ```
   ruff check . && ruff format --check .
   pytest
   node --test tests/*.mjs   # only in repos with a sidebar panel and Node tests
   ```

   CI also runs the tests on the oldest supported Home Assistant (pinned in
   `requirements_test_min.txt`), hassfest, the HACS checks and a standards check.
5. Add an entry under `## [Unreleased]` in `CHANGELOG.md`
   ([Keep a Changelog](https://keepachangelog.com/en/1.1.0/)), and update the
   README if users will notice the change.
6. If you changed any text in `strings.json`, make the same change in
   `translations/en.json`.
7. Open a pull request and fill in the checklist.

## How releases work

The maintainer bumps the version in `manifest.json` and dates the CHANGELOG
section. Every push to `main` refreshes a draft GitHub release with those notes
and the integration zip; the maintainer reviews and publishes it, which creates
the tag and makes the update show in HACS. Versions follow
[Semantic Versioning](https://semver.org).

## Shared tooling

The CI workflows, issue and pull request templates, and the standards every
repo follows live in [bisman-automations/.github](https://github.com/bisman-automations/.github).
Improvements to CI belong there, so every repo gets them.

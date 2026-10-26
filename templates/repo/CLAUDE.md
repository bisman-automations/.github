# NAME: notes for Claude and other coding agents

Home Assistant custom integration (`DOMAIN`), installed through HACS. One or
two sentences on what it does. Read this before changing anything.

## Layout

- `custom_components/DOMAIN/`: the integration.
  - `__init__.py`: setup and unload.
  - ...
- `tests/`: pytest (and Node tests of the sidebar panel, if any).
- `README.md` is user documentation; `CHANGELOG.md` is the release history.

## Checks

The shared checks below, plus anything specific to this repo (mypy, Node
tests, extra setup such as core integration requirements).

## Conventions

Repo-specific conventions: data model, naming, UI wording, compatibility
shims and why they exist.

## Open decisions

- None.

SHARED_RULES

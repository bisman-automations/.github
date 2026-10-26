<!-- Organization-wide default pull request template for bisman-automations. -->

## What and why

<!-- What this changes for someone using the integration, and why. Link an
     issue if there is one ("Fixes #123"). -->

## Checklist

- [ ] `ruff check .` and `ruff format --check .` pass
- [ ] `pytest` passes (and `node --test tests/*.mjs` if the panel changed)
- [ ] Tests added or updated for the change
- [ ] `CHANGELOG.md` has an entry under `## [Unreleased]` (or the new version)
- [ ] `manifest.json` version bumped, if this is releasing
- [ ] `README.md` updated if behavior, options, entities or services changed
- [ ] `strings.json` and `translations/en.json` updated together, if text changed
- [ ] No personal details (names, addresses, account or device identifiers, real entity IDs)

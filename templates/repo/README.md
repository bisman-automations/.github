<p align="center">
  <img src="custom_components/DOMAIN/brand/icon.png" alt="NAME" width="128">
</p>

# NAME

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz/)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-YYYY.M%2B-blue.svg)](https://www.home-assistant.io/)
[![GitHub Release](https://img.shields.io/github/v/release/bisman-automations/REPO)](https://github.com/bisman-automations/REPO/releases)
[![Test](https://github.com/bisman-automations/REPO/actions/workflows/test.yml/badge.svg)](https://github.com/bisman-automations/REPO/actions/workflows/test.yml)
[![Validate](https://github.com/bisman-automations/REPO/actions/workflows/validate.yml/badge.svg)](https://github.com/bisman-automations/REPO/actions/workflows/validate.yml)
[![License](https://img.shields.io/github/license/bisman-automations/REPO)](LICENSE)

One or two plain sentences on what it does for the user.

## Requirements

- Home Assistant YYYY.M or newer.
- Anything else it needs (another integration, an app, hardware).

## Installation

### Marketplace (Home Assistant 2026.11 and newer)

[![Open your Home Assistant instance and open this repository in the Marketplace.](https://my.home-assistant.io/badges/marketplace_repository.svg)](https://my.home-assistant.io/redirect/marketplace_repository/?owner=bisman-automations&repository=REPO&category=integration)

1. Select the button above, or go to **Settings > Marketplace**, choose **Add
   from link**, enter `bisman-automations/REPO` under **GitHub link**, and
   select **Add**. Adding a repository from a link needs a GitHub connection;
   the Marketplace asks you to connect one if you haven't.
2. Install **NAME**. If a repair asks you to restart Home Assistant, restart it.

New versions show up under **Settings > Updates**. Already installed NAME with
HACS? There's nothing to do: Home Assistant moves it into the Marketplace the
first time it starts on 2026.11.

### HACS (Home Assistant 2026.10 and older)

[![Open your Home Assistant instance and open this repository in HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=bisman-automations&repository=REPO&category=integration)

1. Select the button above, or in HACS open the menu, choose **Custom
   repositories** and add `https://github.com/bisman-automations/REPO` as an
   **Integration**.
2. Download **NAME** and restart Home Assistant.

### Manual

1. Download `DOMAIN.zip` from the [latest release](https://github.com/bisman-automations/REPO/releases/latest).
2. Unzip it into `config/custom_components/DOMAIN/` and restart Home Assistant.

## Setup

[![Open your Home Assistant instance and start setting up NAME.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=DOMAIN)

Select the button above, or go to **Settings > Devices & services > Add
integration** and search for **NAME**.

<!-- Feature sections go here: entities, services/actions, events, the
     sidebar app, options. -->

## Troubleshooting

- **Diagnostics:** on the integration's page, open the menu and choose
  **Download diagnostics**. Attach the file to an issue (check it first for
  anything you'd rather not share).
- **Debug logs:** on the integration's page choose **Enable debug logging**,
  reproduce the problem, then **Disable debug logging** to download the log.
- Report problems at [Issues](https://github.com/bisman-automations/REPO/issues).

## Development

```
python3.14 -m venv .venv && . .venv/bin/activate
pip install -r requirements_test.txt
ruff check . && ruff format --check .
pytest
```

CI also tests the oldest supported Home Assistant (`requirements_test_min.txt`)
and runs hassfest and the HACS checks. Releases are drafted automatically from
`CHANGELOG.md` on every push to `main` and published by hand. See
[CLAUDE.md](CLAUDE.md) and [CONTRIBUTING](https://github.com/bisman-automations/.github/blob/main/CONTRIBUTING.md).

## License

[MIT](LICENSE)

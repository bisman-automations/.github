# BisMan Home Automations

BisMan Home Automations is a smart-home development organization focused on building practical, user-friendly Home Assistant integrations and automation tools. The projects in this organization are designed to make connected homes more capable, more convenient, and more integrated across devices, services, and ecosystems.

## What we do

The organization creates custom software for Home Assistant and related smart-home platforms, with a strong emphasis on:

- Home Assistant integrations that extend stock functionality
- Smart-home automations for daily life and convenience
- Device and service integrations for utilities, vehicles, lighting, irrigation, TVs, and appliances
- Enhancements that bridge vendor ecosystems like HomeKit, iOS Live Activities, and smart home hardware

## Examples of the kind of work included

The current repositories reflect a focus on real-world home automation problems, including:

- Utility usage and billing integrations for electric and gas providers
- Holiday lighting control and themed smart-light automation
- Appliance status and live activity notifications for washers, dryers, dishwashers, ovens, and refrigerators
- Extended HomeKit device support beyond Home Assistant's default bridge capabilities
- TV management and input restrictions for home entertainment control
- Button and remote action handling for streamlined automations
- Ford vehicle companion features such as remote start, door control, alerts, and climate-related automation
- Irrigation monitoring and runtime tracking for Rain Bird systems

## Technology focus

The work is primarily built in Python and targets the Home Assistant ecosystem, often with support for HomeKit, HACS, and other smart-home tooling. The emphasis is on creating polished integrations that people can actually use in everyday home setups.

## Mission

BisMan Home Automations exists to solve gaps in smart-home experiences by building custom automations and integrations that help homes feel more connected, responsive, and personalized. The goal is to turn fragmented devices and services into a more cohesive and useful living environment.

## Repository style

Projects under this organization are typically:

- Open source and community-focused
- Designed for Home Assistant users
- Built around practical automation use cases
- Intended to improve comfort, efficiency, and insight inside the home

## Integrations

Every integration installs through [HACS](https://hacs.xyz/) as a custom repository and is set up from **Settings → Devices & services**.

| Integration | What it does | Home Assistant |
| --- | --- | --- |
| [Appliance Live Activity](https://github.com/bisman-automations/ha-appliance-live-activity) | Live Activities (iOS) and Live Updates (Android) for washers, dryers, dishwashers, ovens and other appliances. | 2026.7+ |
| [Button Actions](https://github.com/bisman-automations/ha-button-actions) | Short, double and long presses on Lutron Pico and other button remotes, mapped to any action in the UI. | 2025.11+ |
| [Daily Routine](https://github.com/bisman-automations/ha-daily-routine) | Room-by-room, safety-aware daily routines from a sidebar panel. | 2026.9+ |
| [Ford Assistant](https://github.com/bisman-automations/ha-ford-assistant) | Ready-to-use features (remote start, doors, alerts, climate) on top of the Ford integration. | 2026.2+ |
| [Holiday Lighting](https://github.com/bisman-automations/ha-holiday-lighting) | Holiday color themes rotated across your existing lights. | 2026.2+ |
| [HomeKit Extended](https://github.com/bisman-automations/ha-homekit-extended) | HomeKit accessories beyond what the built-in HomeKit Bridge offers. | 2025.3+ |
| [Matter Bridge](https://github.com/bisman-automations/ha-matter-bridge) | Home Assistant Matter Hub as an integration, with a device for each bridge. | 2025.3+ |
| [Montana-Dakota Utilities](https://github.com/bisman-automations/ha-mdu) | Monthly electric and gas usage and billing from MDU. | 2025.11+ |
| [Media Mgmt](https://github.com/bisman-automations/ha-media-mgmt) | Parental controls and listening analytics for speakers. | 2026.3+ |
| [Rain Bird Extended](https://github.com/bisman-automations/ha-rainbird-extended) | Irrigation monitoring and runtime tracking on top of the built-in Rain Bird integration. | 2026.9+ |
| [TCL Android TV Remote](https://github.com/bisman-automations/ha-tcl-android-tv-remote) | Control for TCL Google TV and Android TV sets. | 2025.8+ |
| [TV Mgmt](https://github.com/bisman-automations/ha-tv-mgmt) | Parental controls for smart TVs: one input, daily screen time and bedtime. | 2026.3+ |

How the repositories are built, tested and released is written down in [bisman-automations/.github](https://github.com/bisman-automations/.github).

## Learn more

Visit the organization page here:

- https://github.com/bisman-automations

Explore the public repositories to see the current set of integrations and automation projects in action.

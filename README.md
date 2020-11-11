# SNOOZ Fan Entity
[![License][license-shield]](LICENSE)
[![Home Assistant Component Store][hacsbadge]][hacs]
[![Gift a coffee][giftacoffeebadge]][giftacoffee]

Component to integrate with the [SNOOZ][snooz] white noise sound machine as a fan entity on Home Assistant.

![SNOOZ logo][snoozlogo]

![Image of a SNOOZ device][snoozdevice]

## Installation
### Requirements
[Home Assistant][homeassistant] host that supports Bluetooth Low Energy
  - Tested on Raspberry Pi 4 w/ Home Assistant **0.117**
  
### HACS
1. Copy `custom_components/snooz/*` to your `custom_components` folder in Home Assistant
2. Add a fan to your `configuration.yaml` with the platform `snooz` and MAC address of your SNOOZ device
2. Restart Home Assistant

New to HACS? [Learn more][hacsinstall]

## Configuration

### Example configuration.yaml
```yaml
fan:
  - platform: snooz
    address: AA:BB:CC:DD:EE:FF
    name: My Snooz
```

### Options
key | description
:--- | :---
**address (Required)** | Bluetooth MAC address of the SNOOZ device
**name (Optional)** | Custom name for the fan entity. Defaults to `Snooz {id}` where `id` is the last 2 bytes in the `address` option

[![Gift a coffee][giftacoffeebadgeblue]][giftacoffee]

![Screenshot of home assistant showing a power toggle and fan speed dropdown][screenshot]

[snooz]: https://getsnooz.com/
[snoozlogo]: snooz.png
[snoozdevice]: device.jpg
[homeassistant]: https://www.home-assistant.io/
[screenshot]: screenshot.png
[giftacoffee]: https://www.buymeacoffee.com/abrunkhorst
[giftacoffeebadge]: https://img.shields.io/badge/Gift%20a%20coffee-green.svg?style=flat
[giftacoffeebadgeblue]: https://img.shields.io/badge/Gift%20a%20coffee-blue.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/AustinBrunkhorst/snooz.svg?style=flat
[commits]: https://github.com/custom-components/blueprint/commits/master
[hacs]: https://github.com/custom-components/hacs
[hacsinstall]: https://hacs.xyz/docs/installation/manual
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=flat
[hacsfolder]: https://github.com/AustinBrunkhorst/snooz/tree/master/custom_components/snooz
[license-shield]: https://img.shields.io/github/license/AustinBrunkhorst/snooz.svg?style=flat

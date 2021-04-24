# ![SNOOZ logo][snoozlogo] for Home Assistant
[![License][license-shield]](LICENSE)
[![Home Assistant Component Store][hacsbadge]][hacs]
[![Gift a coffee][giftacoffeebadge]][giftacoffee]

Component to integrate with the [SNOOZ][snooz] white noise sound machine as a fan entity on Home Assistant.

![Image of a SNOOZ device][snoozdevice]

## Installation
### Requirements
[Home Assistant][homeassistant] host that supports Bluetooth Low Energy
  - Tested on Raspberry Pi 4 w/ Home Assistant **2021.4.6**
  
### HACS
1. Add `https://github.com/AustinBrunkhorst/snooz` as a [custom repository][hacsrepository]
   - Alternatively copy `custom_components/snooz/*` to `custom_components/snooz` in your Home Assistant configuration directory
3. Add a `fan` entry to your `configuration.yaml` with the platform `snooz` and MAC address of your SNOOZ device
4. Restart Home Assistant

New to HACS? [Learn more][hacsinstall]

### Snooz MAC Address
SNOOZ broadcasts on bluetooth with the name `Snooz-FFFF` where `FFFF` is the last 2 bytes in its MAC address. 

- You should be able to inspect the full address once you connect to it on Android or iOS (via the Bluetooth Devices system menu).
- If you are adventurous, the linux command [bluetoothctl][bluetoothctl] can be used to find a deviced similar to `Snooz-FFFF`.

***Note**: Two devices are broadcasted under a name like `Snooz-FFFF`. One of them does not work properly, so you may need to try both.*

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

## Screenshots
![Screenshot of home assistant showing a power toggle and fan speed dropdown][screenshot]

## Feature roadmap
- [ ] UI based integration configuration
- [ ] Device discovery

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
[hacsrepository]: https://hacs.xyz/docs/faq/custom_repositories/
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=flat
[hacsfolder]: https://github.com/AustinBrunkhorst/snooz/tree/master/custom_components/snooz
[license-shield]: https://img.shields.io/github/license/AustinBrunkhorst/snooz.svg?style=flat
[bluetoothctl]: https://www.linux-magazine.com/Issues/2017/197/Command-Line-bluetoothctl

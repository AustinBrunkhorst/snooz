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
1. Add `https://github.com/AustinBrunkhorst/snooz` as a [custom repository][hacsrepository].
   - Alternatively copy `custom_components/snooz/*` to `custom_components/snooz` in your Home Assistant configuration directory.
2. Put your SNOOZ device in pairing mode.
3. Add the "SNOOZ Noise Maker" integration. Your device should be discovered automatically.

New to HACS? [Learn more][hacsinstall]

[![Gift a coffee][giftacoffeebadgeblue]][giftacoffee]

## Screenshots
![Screenshot of home assistant showing a power toggle and fan speed dropdown][screenshot]

## Frequently asked questions
> How do I enter pairing mode?
1. Unplug SNOOZ and let sit for 5 seconds.
2. Plug SNOOZ back in.
3. Confirm no other phones are trying to connect to the device.
4. With one finger, press and hold the power button on SNOOZ. Release when the lights start blinking (approximately 5 seconds).

> My device isn't discovered on the integration setup

Make sure the SNOOZ device is in pairing mode and within Bluetooth range of the host device running Home Assistant.

> Can I use the SNOOZ mobile app when the device is connected to Home Assistant?

No. This is a limitation with the SNOOZ device supporting only 1 simultaneous connection.

## ⚠ Disclaimer ⚠
This integration is in no way affiliated with SNOOZ. SNOOZ does not offer support for this integration, as it was built by reverse engineering communication with SNOOZ's mobile app.

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

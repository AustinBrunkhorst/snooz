> **Note**
> Snooz is now available as a [core integration](https://www.home-assistant.io/integrations/snooz/) in Home Assistant 2022.11+. This custom component will no longer be maintained.

<p align="center">
  <img src="header.svg" alt="Home Assistant + SNOOZ" />
</p>

Custom Home Assistant component for [SNOOZ][snooz] white noise sound machine.

## Installation
### Requirements
- [Home Assistant][homeassistant] **2022.8+**
- [Bluetooth Component][bluetooth_component]
  
### HACS
1. Add `https://github.com/AustinBrunkhorst/snooz` as a [custom repository][hacsrepository].
   - Alternatively copy `custom_components/snooz/*` to `custom_components/snooz` in your Home Assistant configuration directory.
2. Ensure your SNOOZ device is within range of your Home Assistant host hardware.
3. Add the **SNOOZ** integration in *Settings > Devices & Services*
4. Select a device to setup
5. Enter the device in pairing mode to complete the setup

New to HACS? [Learn more][hacsinstall]

[![Gift a coffee][giftacoffeebadgeblue]][giftacoffee]

## Fan
SNOOZ devices are exposed as fan entities and support the following services:
- `fan.turn_on`
- `fan.turn_off`
- `fan.set_percentage`

## Sensor
### `sensor.connection_status`
The bluetooth connection status of the device.
- connected
- disconnected
- connecting

### `sensor.signal_strength`
The bluetooth RSSI signal strength of the device.

## Services
### `snooz.turn_on`
Power on the device. Optionally transition the volume over time.
|          |          |                                                     |
|----------|----------|-----------------------------------------------------|
| volume   | optional | Volume to set before turning on                     |    
| duration | optional | Duration in seconds to transition to the new volume |

### `snooz.turn_off`
Power off the device. Optionally transition the volume over time.
|          |          |                                                     |
|----------|----------|-----------------------------------------------------|
| duration | optional | Duration in seconds to transition to the new volume |

### `snooz.disconnect`
Terminate any connections to this device.

## Troubleshooting
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
[bluetooth_component]: https://www.home-assistant.io/components/bluetooth/

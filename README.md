# SNOOZ Fan Entity
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

Component to integrate with the [SNOOZ][snooz] white noise sound machine as a fan entity on Home Assistant.

![SNOOZ logo][snoozlogo]

![SNOOZ device][snoozdevice]

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
**name (Optional)** | Custom name for the fan entity. Defaults to `Snooz`

![Home Assistant screenshot][screenshot]

[snooz]: https://getsnooz.com/
[snoozlogo]: snooz.png
[snoozdevice]: device.jpg
[screenshot]: screenshot.png
[buymecoffee]: https://www.buymeacoffee.com/abrunkhorst
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-blue.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/AustinBrunkhorst/snooz.svg?style=for-the-badge
[commits]: https://github.com/custom-components/blueprint/commits/master
[hacs]: https://github.com/custom-components/hacs
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/AustinBrunkhorst/snooz.svg?style=for-the-badge

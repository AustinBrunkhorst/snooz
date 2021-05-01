from bluepy.btle import Scanner, DefaultDelegate, ScanEntry


class DiscoveredSnooz:
    name = None
    token = None
    device = None


class SnoozDiscoverer(DefaultDelegate):
    devices = []

    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, device, isNew, isData):
        if not isNew:
            return

        device_name = device.getValueText(ScanEntry.COMPLETE_LOCAL_NAME)

        if not isinstance(device_name, str) or not device_name.startswith("Snooz"):
            return

        advertisement = device.getValue(ScanEntry.MANUFACTURER)

        # unexpected data
        if len(advertisement) < 3:
            return

        if advertisement[:3] == b"\xFF\xFF\x08":
            print("{} is not in discovery mode.".format(device_name))
            return

        token = advertisement[3:]

        snooz_device = DiscoveredSnooz(device_name, token, device)

        self.devices.append(snooz_device)


def discover():
    discoverer = SnoozDiscoverer()

    scanner = Scanner().withDelegate(discoverer)
    scanner.scan(5.0)

    return discoverer.devices
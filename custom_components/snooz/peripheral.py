from bluepy.btle import (
    ADDR_TYPE_PUBLIC,
    ADDR_TYPE_RANDOM,
    ScanEntry,
    BTLEDisconnectError,
    Peripheral,
)


class PeripheralWithTimeout(Peripheral):
    def _connect(self, addr, addrType=ADDR_TYPE_PUBLIC, iface=None, timeout=None):
        if len(addr.split(":")) != 6:
            raise ValueError("Expected MAC address, got %s" % repr(addr))
        if addrType not in (ADDR_TYPE_PUBLIC, ADDR_TYPE_RANDOM):
            raise ValueError(
                "Expected address type public or random, got {}".format(addrType)
            )
        self._startHelper(iface)
        self.addr = addr
        self.addrType = addrType
        self.iface = iface
        if iface is not None:
            self._writeCmd("conn %s %s %s\n" % (addr, addrType, "hci" + str(iface)))
        else:
            self._writeCmd("conn %s %s\n" % (addr, addrType))
        rsp = self._getResp("stat", timeout)
        if rsp is None:
            raise BTLEDisconnectError(
                "Timed out while trying to connect to peripheral %s, addr type: %s"
                % (addr, addrType),
                rsp,
            )
        while rsp["state"][0] == "tryconn":
            rsp = self._getResp("stat", timeout)
        if rsp["state"][0] != "conn":
            self._stopHelper()
            raise BTLEDisconnectError(
                "Failed to connect to peripheral %s, addr type: %s" % (addr, addrType),
                rsp,
            )

    def connect(self, addr, addrType=ADDR_TYPE_PUBLIC, iface=None, timeout=None):
        if isinstance(addr, ScanEntry):
            self._connect(addr.addr, addr.addrType, addr.iface, timeout)
        elif addr is not None:
            self._connect(addr, addrType, iface, timeout)
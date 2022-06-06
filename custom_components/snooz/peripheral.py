import logging
import pprint
from bluepy.btle import (
    ADDR_TYPE_PUBLIC,
    ADDR_TYPE_RANDOM,
    ScanEntry,
    BTLEDisconnectError,
    Peripheral,
)

_LOGGER = logging.getLogger(__name__)

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
        response = self._getResp("stat", timeout)
        if response is None:
            raise BTLEDisconnectError(
                "Timed out while trying to connect to peripheral %s, addr type: %s"
                % (addr, addrType),
                response,
            )

        while self.get_state_from_response(response) == "tryconn":
            response = self._getResp("stat", timeout)
        
        if self.get_state_from_response(response) != "conn":
            self._stopHelper()
            raise BTLEDisconnectError(
                "Failed to connect to peripheral %s, addr type: %s" % (addr, addrType),
                response,
            )

    def connect(self, addr, addrType=ADDR_TYPE_PUBLIC, iface=None, timeout=None):
        if isinstance(addr, ScanEntry):
            self._connect(addr.addr, addr.addrType, addr.iface, timeout)
        elif addr is not None:
            self._connect(addr, addrType, iface, timeout)

    def get_state_from_response(self, response):
        if response is None or response["state"] is None or response["state"][0] is None:
            _LOGGER.error(
                f"Missing 'state' in stat response during connection: {pprint.pformat(response)}"
            )
            return None
        return response["state"][0]

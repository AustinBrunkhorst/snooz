DOMAIN = "snooz"

# bluetooth MAC address of the snooz
CONF_ADDRESS = "address"

# uuid of the service that controls snooz
SNOOZ_SERVICE_UUID = "729f0608496a47fea1243a62aaa3fbc0"

# uuid of the characteristic that reads snooz state
READ_STATE_UUID = "80c37f00-cc16-11e4-8830-0800200c9a66"

# uuid of the characteristic that writes snooz state
WRITE_STATE_UUID = "90759319-1668-44da-9ef3-492d593bd1e5"

# sequence of bytes to write when connected to the device
CONNECTION_SEQUENCE = [
    [0x07],
    [0x06, 0xae, 0xf6, 0x74, 0x5a, 0x01, 0x18, 0x02, 0x24],
    [0x07],
    [0x0b, 0x31, 0xd2, 0x08, 0x00],
    [0x0c],
    [0x10],
]

# length in bytes of the read characteristic
STATE_UPDATE_LENGTH = 20

# bytes that turn on the snooz
COMMAND_TURN_ON = [0x02, 0x01]

# bytes that turn off the snooz
COMMAND_TURN_OFF = [0x02, 0x00]

# interval to retry connecting
CONNECTION_RETRY_INTERVAL = 5

# timeout for waiting on notifications
NOTIFICATION_TIMEOUT = 15

# maximum age for a state update job
MAX_QUEUED_STATE_AGE = 10

# maximum number of queued items
MAX_QUEUED_STATE_COUNT = 2

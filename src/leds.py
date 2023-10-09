import uasyncio as asyncio
import time
import common
import common_pins
from driver_r4d3b8 import R4D3B16

relays = []
relay_board = None
leds = []

relay_pins = [
    common_pins.RELAY_1,
    common_pins.RELAY_2,
    common_pins.RELAY_3,
    common_pins.RELAY_4,
    common_pins.RELAY_5,
    common_pins.RELAY_6,
    common_pins.RELAY_7,
    common_pins.RELAY_8,
]
led_pins = [
    common_pins.ONBOARD_LED,
    common_pins.B_LED1,
    common_pins.B_LED2
]


class Led:
    def __init__(self, id, name, active_high=False):
        self.output = common.create_output(id)
        self.active_high = active_high
        self.state = None
        self.set_state(0)
        self.name = name

    def set_state(self, state):
        if self.active_high:
            if state:
                self.output.off()
            else:
                self.output.on()
        else:
            if state:
                self.output.on()
            else:
                self.output.off()
        self.state = state

class Relay:
    def __init__(self, id, name, relay_board, active_high=False):
        self.id = id
        self.name = name
        self.relay_board = relay_board
        self.active_high = active_high
        self.state = None
        self.set_state(0)

    def set_state(self, state):
        if self.active_high:
            if state:
                self.relay_board.set_relay_off(self.id)
            else:
                self.relay_board.set_relay_on(self.id)
        else:
            if state:
                self.relay_board.set_relay_on(self.id)
            else:
                self.relay_board.set_relay_off(self.id)
        self.state = state


def set_state_by_name(name, state):
    print("[LEDS]: set_state_by_name(%s, %s)" % (name, state))
    for relay in relays:
        if relay.name == name:
            relay.set_state(state)
    for led in leds:
        if led.name == name:
            led.set_state(state)


def get_state_by_name(name):
    for relay in relays:
        if relay.name == name:
            return relay.state
    for led in leds:
        if led.name == name:
            return led.state
    return None


def on_relay_direct(thing):
    state = int(thing.data) if thing.data in ("0", "1", 0, 1) else None
    if state is not None:
        set_state_by_name(thing.alias, state)
    if thing.data == "request":
        state = get_state_by_name(thing.alias)
        print(thing.alias, thing.data)
        if state is not None:
            thing.data = state
            thing.dirty_out = True


def test_relays():
    global relays
    relays = []
    init_relays()
    for relay in relays:
        print("[LEDS]: testing %s" % (relay.name))
        relay.set_state(1)
        time.sleep_ms(1000)
        relay.set_state(0)
        time.sleep_ms(1000)


def test_leds():
    global leds
    leds = []
    init_leds()
    for led in leds:
        print("[LEDS]: testing %s" % (led.name))
        led.set_state(1)
        time.sleep_ms(1000)
        led.set_state(0)
        time.sleep_ms(1000)


def init_relays():
    global relay_board
    relay_board = R4D3B16(common_pins.UART0_INSTANCE.id, common_pins.UART0_TX.id, common_pins.UART0_RX.id)
    for pin in relay_pins:
        relays.append(Relay(pin.id, pin.name, relay_board))


def init_leds():
    for pin in led_pins:
        if "ONBOARD" in pin.name:
            leds.append(Led(pin.id, pin.name))
        else:
            leds.append(Led(pin.id, pin.name, active_high=True))


def init():
    print("[LEDS]: init")
    init_relays()
    init_leds()
    action()


def action():
    pass


def test():
    print("[LEDS]: test")
    init()
    while True:
        action()


def test_async():
    print("[LEDS]: test_async")
    init()
    asyncio.run(common.loop_async("LEDS", action))

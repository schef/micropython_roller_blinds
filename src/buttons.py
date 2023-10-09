import uasyncio as asyncio
import common
import common_pins

on_state_change_cb = None
buttons = []

button_pins = [common_pins.ONBOARD_BUTTON,
               common_pins.B1_SW1,
               common_pins.B1_SW2,
               common_pins.B2_SW1,
               common_pins.B2_SW2,
               common_pins.B3_SW1,
               common_pins.B3_SW2,
               common_pins.B4_SW1,
               common_pins.B4_SW2
               ]


class Button:
    def __init__(self, pin):
        self.input = common.create_input(pin.id)
        self.name = pin.name
        self.state = None

    def check(self):
        state = self.input.value()
        if state != self.state:
            self.state = state
            print("[BUTTONS]: %s -> %d" % (self.name, self.state))
            if on_state_change_cb:
                on_state_change_cb(self.name, self.state)


def register_on_state_change_callback(cb):
    print("[BUTTONS]: register on state change cb")
    global on_state_change_cb
    on_state_change_cb = cb


def init():
    print("[BUTTONS]: init")
    for pin in button_pins:
        buttons.append(Button(pin))


def action():
    for button in buttons:
        button.check()


def test():
    print("[BUTTONS]: test")
    init()
    while True:
        action()


def test_async():
    print("[BUTTONS]: test_async")
    init()
    asyncio.run(common.loop_async("BUTTONS", action))

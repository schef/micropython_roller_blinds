from typing import Optional
import uasyncio as asyncio
import common
import buttons

class RolloSingleDirection:
    def __init__(self, relay, button):
        self.relay = relay
        self.button = button
        self.active = False

class Rollo:
    def __init__(self, path, rollo_up, rollo_down):
        self.path = path
        self.up = rollo_up
        self.down = rollo_down
        self.timestamp = None
        self.max_timeout = 60000
        self.timeout = self.max_timeout
        self.current_position = None
        self.first_time_position = None

on_state_change_cb = None

rollos = {
    "rollo/1": Rollo("rollo/1", RolloSingleDirection("RELAY_1", "B_SW1"), RolloSingleDirection("RELAY_2", "B_SW2")),
    "rollo/2": Rollo("rollo/2", RolloSingleDirection("RELAY_3", "B_SW1"), RolloSingleDirection("RELAY_4", "B_SW2")),
    "rollo/3": Rollo("rollo/3", RolloSingleDirection("RELAY_5", "B_SW1"), RolloSingleDirection("RELAY_6", "B_SW2")),
    "rollo/4": Rollo("rollo/4", RolloSingleDirection("RELAY_7", "B_SW1"), RolloSingleDirection("RELAY_8", "B_SW2"))
}

def get_rollo_from_alias(alias) -> Optional[Rollo]:
    rollo = None
    for key in rollos:
        if alias == rollos[key].up.button or alias == rollos[key].down.button:
            rollo = rollos[key]
    return rollo

def check_rollos_for_button(alias, state):
    rollo = get_rollo_from_alias(alias)
    if rollo is not None:
        if not state:
            if rollo.up.active or rollo.down.active:
                set_rollos(rollo, "STOP")
            else:
                if rollo.up.button == alias:
                    set_rollos(rollo, "UP")
                elif rollo.down.button == alias:
                    set_rollos(rollo, "DOWN")


def on_button_state_change_callback(alias, data):
    check_rollos_for_button(alias, data)

def on_data_received(thing):
    rollo = rollos.get(thing.path)
    if rollo is not None:
        set_rollos(rollo, thing.data)
    for key in rollos:
        rollo = rollos[key]

def get_percent_from_data(data):
    if data == "UP":
        return 100
    elif data == "DOWN":
        return 0
    else:
        try:
            percent = int(data)
            if percent >= 0 and percent <= 100:
                return percent
        except Exception as e:
            print("[PHY]: ERROR: with error %s" % (e))
    return None

def set_rollos(rollo, data):
    print("[PHY]: set_rollos[%s], data[%s]" % (rollo.path, data))
    if data == "STOP":
        if rollo.up.active:
            if common.millis_passed(rollo.timestamp) >= rollo.max_timeout:
                rollo.current_position = 100
            else:
                if rollo.current_position is not None:
                    rollo.current_position = rollo.current_position + int(common.millis_passed(rollo.timestamp) / rollo.max_timeout * 100)
                    if rollo.current_position > 100:
                        rollo.current_position = 100
        elif rollo.down.active:
            if common.millis_passed(rollo.timestamp) >= rollo.max_timeout:
                rollo.current_position = 0
            else:
                if rollo.current_position is not None:
                    rollo.current_position = rollo.current_position - int(common.millis_passed(rollo.timestamp) / rollo.max_timeout * 100)
                    if rollo.current_position < 0:
                        rollo.current_position = 0
        print("[PHY]: rollo[%s], position[%s]" % (rollo.path, str(rollo.current_position)))
        if on_state_change_cb is not None:
            on_state_change_cb(rollo.path, str(rollo.current_position))
        rollo.up.active = False
        rollo.down.active = False
        rollo.timeout = None
        rollo.timestamp = None
    else:
        percent = get_percent_from_data(data)
        if percent is not None:
            direction_up = False
            direction_down = False
            timeout = None
            if percent == 100:
                direction_up = True
                timeout = rollo.max_timeout
            elif percent == 0:
                direction_down = True
                timeout = rollo.max_timeout
            else:
                if rollo.current_position is not None:
                    move_percent = percent - rollo.current_position
                    timeout = abs(int(move_percent / 100 * rollo.max_timeout))
                    if move_percent > 0:
                        direction_up = True
                    elif move_percent < 0:
                        direction_down = True
                else:
                    rollo.first_time_position = percent
                    direction_up = True
                    timeout = rollo.max_timeout
            if direction_up:
                if rollo.down.active:
                    rollo.down.active = False
                rollo.up.active = True
                rollo.timeout = timeout
                rollo.timestamp = common.get_millis()
            elif direction_down:
                if rollo.up.active:
                    rollo.up.active = False
                rollo.down.active = True
                rollo.timeout = timeout
                rollo.timestamp = common.get_millis()

def check_rollos_timeout():
    for key in rollos:
        rollo = rollos[key]
        if rollo.up.active or rollo.down.active:
            if common.millis_passed(rollo.timestamp) >= rollo.timeout:
                set_rollos(rollo, "STOP")
                if rollo.first_time_position is not None:
                    if rollo.current_position is None:
                        rollo.first_time_position = None
                    else:
                        set_rollos(rollo, rollo.first_time_position)
                        rollo.first_time_position = None

def register_on_state_change_callback(cb):
    global on_state_change_cb
    print("[PHY]: register on state change cb")
    on_state_change_cb = cb

def init():
    print("[PHY]: init")
    buttons.register_on_state_change_callback(on_button_state_change_callback)
    for key in rollos:
        set_rollos(rollos[key], "STOP")

async def action():
    while True:
        check_rollos_timeout()
        await asyncio.sleep(0.1)

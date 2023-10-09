import uasyncio as asyncio
import common
import buttons
import leds


class Light:
    def __init__(self, path, button, main_light, inverted_light, activity_light):
        self.path = path
        self.button = button
        self.main_light = main_light
        self.inverted_light = inverted_light
        self.activity_light = activity_light
        self.state = None


class RolloSingleDirection:
    def __init__(self, relay, button, idle_light, pressed_light):
        self.relay = relay
        self.button = button
        self.idle_light = idle_light
        self.pressed_light = pressed_light
        self.active = False


class Co2Alarm:
    def __init__(self, path):
        self.path = path
        self.active = False


class Rollo:
    def __init__(self, path, rollo_up, rollo_down, co2alarm):
        self.path = path
        self.up = rollo_up
        self.down = rollo_down
        self.alarm = co2alarm
        self.timestamp = None
        self.max_timeout = 60000
        self.timeout = self.max_timeout
        self.current_position = None
        self.first_time_position = None


on_state_change_cb = None

lights = {
    "lights/1/1": Light("lights/1/1", "B4_SW1", "RELAY_11", "B4_LED1_R", "B4_LED1_GB"),
    "lights/1/2": Light("lights/1/2", "B4_SW2", "RELAY_12", "B4_LED2_R", "B4_LED2_GB"),
    "lights/2/1": Light("lights/2/1", "B3_SW1", "RELAY_10", "B3_LED1_R", "B3_LED1_GB")
}

rollos = {
    "rollo/1": Rollo("rollo/1", RolloSingleDirection("RELAY_4", "B2_SW1", "B2_LED1_GB", "B2_LED1_R"), RolloSingleDirection("RELAY_3", "B2_SW2", "B2_LED2_GB", "B2_LED2_R"), Co2Alarm("co2_alarm/1")),
    "rollo/2": Rollo("rollo/2", RolloSingleDirection("RELAY_2", "B1_SW1", "B1_LED1_GB", "B1_LED1_R"), RolloSingleDirection("RELAY_1", "B1_SW2", "B1_LED2_GB", "B1_LED2_R"), Co2Alarm("co2_alarm/2"))
}


def get_light_from_alias(alias):
    light = None
    for key in lights:
        if lights[key].button == alias:
            light = lights[key]
    return light


def get_rollo_from_alias(alias) -> Rollo:
    rollo = None
    for key in rollos:
        if alias == rollos[key].up.button or alias == rollos[key].down.button:
            rollo = rollos[key]
    return rollo


def check_lights_for_button(alias, state):
    light = get_light_from_alias(alias)
    if light is not None:
        if state:
            leds.set_state_by_name(light.activity_light, 0)
            leds.set_state_by_name(light.inverted_light, 1)
        else:
            leds.set_state_by_name(light.inverted_light, 0)
            set_lights(light, int(not (light.state)))


def check_rollos_for_button(alias, state):
    rollo = get_rollo_from_alias(alias)
    if rollo is not None:
        if state:
            if rollo.alarm.active == False:
                if rollo.up.button == alias:
                    leds.set_state_by_name(rollo.up.idle_light, 0)
                    leds.set_state_by_name(rollo.up.pressed_light, 1)
                elif rollo.down.button == alias:
                    leds.set_state_by_name(rollo.down.idle_light, 0)
                    leds.set_state_by_name(rollo.down.pressed_light, 1)
        else:
            if rollo.up.active or rollo.down.active:
                set_rollos(rollo, "STOP")
            else:
                if rollo.up.button == alias:
                    set_rollos(rollo, "UP")
                elif rollo.down.button == alias:
                    set_rollos(rollo, "DOWN")


def on_button_state_change_callback(alias, data):
    check_lights_for_button(alias, data)
    check_rollos_for_button(alias, data)


def on_data_received(thing):
    light = lights.get(thing.path)
    if light is not None:
        set_lights(light, thing.data)
    rollo = rollos.get(thing.path)
    if rollo is not None:
        set_rollos(rollo, thing.data)
    for key in rollos:
        rollo = rollos[key]
        if rollo.alarm.path == thing.path:
            set_co2allarms(rollo, thing.data)


def set_lights(light, data):
    print("[PHY]: set_lights[%s], data[%s]" % (light.path, data))
    state = int(data) if data in ("0", "1", 0, 1) else None
    if state is not None:
        light.state = state
        leds.set_state_by_name(light.main_light, state)
        leds.set_state_by_name(light.activity_light, int(not (state)))
        if on_state_change_cb is not None:
            on_state_change_cb(light.path, light.state)


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
        if rollo.alarm.active == False:
            leds.set_state_by_name(rollo.up.pressed_light, 0)
            leds.set_state_by_name(rollo.up.idle_light, 1)
            leds.set_state_by_name(rollo.down.pressed_light, 0)
            leds.set_state_by_name(rollo.down.idle_light, 1)
        leds.set_state_by_name(rollo.up.relay, 0)
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
        leds.set_state_by_name(rollo.down.relay, 0)
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
                if rollo.alarm.active == False:
                    leds.set_state_by_name(rollo.up.pressed_light, 0)
                    leds.set_state_by_name(rollo.up.idle_light, 1)
                if rollo.down.active:
                    leds.set_state_by_name(rollo.down.relay, 0)
                    rollo.down.active = False
                leds.set_state_by_name(rollo.up.relay, 1)
                rollo.up.active = True
                rollo.timeout = timeout
                rollo.timestamp = common.get_millis()
            elif direction_down:
                if rollo.alarm.active == False:
                    leds.set_state_by_name(rollo.down.pressed_light, 0)
                    leds.set_state_by_name(rollo.down.idle_light, 1)
                if rollo.up.active:
                    leds.set_state_by_name(rollo.up.relay, 0)
                    rollo.up.active = False
                leds.set_state_by_name(rollo.down.relay, 1)
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


def set_co2allarms(rollo, data):
    print("[PHY]: set_co2allarms[%s], data[%s]" % (rollo.alarm.path, data))
    state = int(data) if data in ("0", "1", 0, 1) else None
    if state is not None:
        rollo.alarm.active = state
        if rollo.alarm.active:
            leds.set_state_by_name(rollo.up.pressed_light, 1)
            leds.set_state_by_name(rollo.up.idle_light, 0)
            leds.set_state_by_name(rollo.down.pressed_light, 1)
            leds.set_state_by_name(rollo.down.idle_light, 0)
        else:
            leds.set_state_by_name(rollo.up.pressed_light, 0)
            leds.set_state_by_name(rollo.up.idle_light, 1)
            leds.set_state_by_name(rollo.down.pressed_light, 0)
            leds.set_state_by_name(rollo.down.idle_light, 1)


def register_on_state_change_callback(cb):
    global on_state_change_cb
    print("[PHY]: register on state change cb")
    on_state_change_cb = cb


def init():
    print("[PHY]: init")
    buttons.register_on_state_change_callback(on_button_state_change_callback)
    for key in lights:
        set_lights(lights[key], 0)
    for key in rollos:
        set_rollos(rollos[key], "STOP")


async def action():
    while True:
        check_rollos_timeout()
        await asyncio.sleep(0.1)

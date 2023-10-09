import uasyncio as asyncio
import common
import leds
import mqtt

BOOT_LED = "ONBOARD_LED1"
ACTIVITY_LED = "ONBOARD_LED2"
MQTT_LED = "ONBOARD_LED3"
activity_timestamp = None
activity_timeout = 100


def set_signal_led_boot():
    leds.set_state_by_name(BOOT_LED, 1)


def check_signal_led_mqtt(state):
    if leds.get_state_by_name(MQTT_LED) != int(state):
        leds.set_state_by_name(MQTT_LED, int(state))


def set_activity():
    global activity_timestamp
    activity_timestamp = common.get_millis()
    leds.set_state_by_name(ACTIVITY_LED, 1)


def check_signal_led_activity():
    global activity_timestamp
    if activity_timestamp is not None and common.millis_passed(activity_timestamp) >= activity_timeout:
        activity_timestamp = None
        leds.set_state_by_name(ACTIVITY_LED, 0)


async def action():
    set_signal_led_boot()
    while True:
        check_signal_led_mqtt(mqtt.is_connected())
        check_signal_led_activity()
        await asyncio.sleep(0.1)

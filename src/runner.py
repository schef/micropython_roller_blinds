import uasyncio as asyncio
import things
import common
import buttons
import leds
import mqtt
import cli
import signal_leds
import phy_interface
import heartbeat


async def process_time_measure(timeout=20):
    print("[RUNNER]: start process_time_measure")
    timestamp = common.get_millis()
    bigest = 0
    while True:
        await asyncio.sleep(0)
        timepassed = common.millis_passed(timestamp)
        if timepassed >= timeout:
            if timepassed > bigest:
                bigest = timepassed
            print("[RUNNER]: timeout warning %d ms with bigest %d" % (timepassed, bigest))
        timestamp = common.get_millis()


def init():
    print("[RUNNER]: init")
    buttons.init()
    buttons.action()
    leds.init()
    phy_interface.init()
    mqtt.init()
    cli.init()
    things.init()


async def add_tasks():
    print("[RUNNER]: add_tasks")
    tasks = []
    tasks.append(asyncio.create_task(things.loop_async()))
    tasks.append(asyncio.create_task(common.loop_async("BUTTONS", buttons.action)))
    tasks.append(asyncio.create_task(common.loop_async("LEDS", leds.action)))
    tasks.append(asyncio.create_task(mqtt.loop_async()))
    tasks.append(asyncio.create_task(common.loop_async("CLI", cli.action)))
    tasks.append(asyncio.create_task(signal_leds.action()))
    tasks.append(asyncio.create_task(phy_interface.action()))
    tasks.append(asyncio.create_task(process_time_measure()))
    tasks.append(asyncio.create_task(heartbeat.action()))
    for task in tasks:
        await task
    print("[RUNNER]: Error: loop task finished!")


def start():
    print("[RUNNER]: start")
    init()
    asyncio.run(add_tasks())

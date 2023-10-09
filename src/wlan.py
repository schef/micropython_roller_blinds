from micropython import const
import network
import uasyncio as asyncio
import credentials

# https://docs.openmv.io/library/network.LAN.html
# https://github.com/EchoDel/hardware_projects/blob/main/micropython/micropython-async-master/v2/sock_nonblock.py
# https://github.com/peterhinch/micropython-mqtt/blob/master/mqtt_as/mqtt_as.py
# https://github.com/microhomie/microhomie/blob/master/lib/mqtt_as.py
# https://github.com/micropython/micropython-lib/blob/master/micropython/umqtt.simple/umqtt/simple.py
# https://github.com/fizista/micropython-umqtt.simple2/blob/master/src/umqtt/simple2.py

_CONNECT_TIMEOUT_SLEEP_MS = const(30 * 60 * 1000)

mac = ""
wlan = None


async def check_link():
    status = wlan.status()
    if status == 0:
        print("[WLAN]: Link Down")
    if status == 1:
        print("[WLAN]: Link Join")
        try:
            wlan.active(True)
        except Exception as e:
            print("[WLAN]: ERROR %s" % (e))
    elif status == 2:
        print("[WLAN]: Link No-IP")
        connect_error = False
        try:
            wlan.connect(credentials.ssid, credentials.password)
            while wlan.isconnected() == False:
                print('[WLAN] Waiting for connection...')
                asyncio.sleep_ms(1000)
            print(f"[WLAN]: {wlan.ifconfig()}")
        except Exception as e:
            print("[WLAN]: ERROR %s" % (e))
            connect_error = True
        if connect_error:
            print("[WLAN]: Waiting %d until nekt try" % (_CONNECT_TIMEOUT_SLEEP_MS))
            await asyncio.sleep_ms(_CONNECT_TIMEOUT_SLEEP_MS)
    elif status == 3:
        print("[WLAN]: Link Up")
        return True
    return False


def init():
    print("[WLAN]: init")
    global wlan, mac
    wlan = network.WLAN(network.STA_IF)
    mac = "".join(['{:02X}'.format(x) for x in wlan.config('mac')])


def print_mac():
    print("[WLAN]: mac %s" % (mac))

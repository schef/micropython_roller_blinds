from micropython import const
import network
import uasyncio as asyncio

# https://docs.openmv.io/library/network.LAN.html
# https://github.com/EchoDel/hardware_projects/blob/main/micropython/micropython-async-master/v2/sock_nonblock.py
# https://github.com/peterhinch/micropython-mqtt/blob/master/mqtt_as/mqtt_as.py
# https://github.com/microhomie/microhomie/blob/master/lib/mqtt_as.py
# https://github.com/micropython/micropython-lib/blob/master/micropython/umqtt.simple/umqtt/simple.py
# https://github.com/fizista/micropython-umqtt.simple2/blob/master/src/umqtt/simple2.py

_DHCP_TIMEOUT_SLEEP_MS = const(30 * 60 * 1000)

mac = ""
eth = None


async def check_link():
    status = eth.status()
    if status == 0:
        print("[LAN]: Link Down")
    if status == 1:
        print("[LAN]: Link Join")
        try:
            eth.active(True)
        except Exception as e:
            print("[LAN]: ERROR %s" % (e))
    elif status == 2:
        print("[LAN]: Link No-IP")
        dhcp_error = False
        try:
            eth.ifconfig('dhcp')
        except Exception as e:
            print("[LAN]: ERROR %s" % (e))
            dhcp_error = True
        if dhcp_error:
            print("[LAN]: Waiting %d until nekt try" % (_DHCP_TIMEOUT_SLEEP_MS))
            await asyncio.sleep_ms(_DHCP_TIMEOUT_SLEEP_MS)
    elif status == 3:
        print("[LAN]: Link Up")
        return True
    return False


def init():
    print("[LAN]: init")
    global eth, mac
    eth = network.LAN()
    mac = "".join(['{:02X}'.format(x) for x in eth.config('mac')])


def print_mac():
    print("[LAN]: mac %s" % (mac))

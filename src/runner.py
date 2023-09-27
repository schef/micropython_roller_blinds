import time
from r4d3b8 import R4D3B16

rb = None

def get_millis():
    return time.ticks_ms()

def millis_passed(timestamp):
    return time.ticks_diff(time.ticks_ms(), timestamp)

def init():
    global rb
    rb = R4D3B16()
    print("init")

def run():
    pass

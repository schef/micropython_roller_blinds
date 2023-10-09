import time

def get_millis():
    return time.ticks_ms()

def millis_passed(timestamp):
    return time.ticks_diff(time.ticks_ms(), timestamp)


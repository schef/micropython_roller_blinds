class Pin:
    def __init__(self, id, name):
        self.id = id
        self.name = name

UART0_INSTANCE = Pin(0, "UART0_INSTANCE")
UART0_TX = Pin(0, "UART0_TX")
UART0_RX = Pin(1, "UART0_RX")
RELAY_1 = Pin(0, "RELAY_1")
RELAY_2 = Pin(1, "RELAY_2")
RELAY_3 = Pin(2, "RELAY_3")
RELAY_4 = Pin(3, "RELAY_4")
RELAY_5 = Pin(4, "RELAY_5")
RELAY_6 = Pin(5, "RELAY_6")
RELAY_7 = Pin(6, "RELAY_7")
RELAY_8 = Pin(7, "RELAY_8")
B_SW1 = Pin(2, "B_SW1")
B_SW2 = Pin(4, "B_SW2")
B_LED1 = Pin(3, "B_LED1")
B_LED2 = Pin(5, "B_LED2")
ONBOARD_LED = Pin(0, "ONBOARD_LED")

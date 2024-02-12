#!/bin/python3
import vgamepad as vg
import time
from os import environ
import socket
import sys

ADDR=("evwheel", 6769)

MAX_WHEEL_ANGLE=540

CMD_CALIB=1
CMD_FOLLOW_ON=2
CMD_FOLLOW_OFF=3
CMD_FFB_ON=4
CMD_FFB_OFF=5


def connect():
    s=None
    print("Connecting to ", ADDR)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(2)
    s.connect(ADDR)
    return s

def update_buttons_state(buttons):
    global gamepad

    if (val >> 0) & True:
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_B)
    else:
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_B)

    if (val >> 1) & True:
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
    else:
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_X)

    if (val >> 2) & True:
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
    else:
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)

def update():
    send_data=bytearray()
    send_data.append(0) # command
    socket.send(send_data)

    data = None
    addr = None
    try:
        data, addr = socket.recvfrom(8)
    except:
        print("failed to recv packet data")
        time.sleep(1)
        return
    angle=float(int.from_bytes(data[0:4], "big", signed= True))
    angle=-((angle-MAX_WHEEL_ANGLE)/MAX_WHEEL_ANGLE)

    buttons=data[4]
    update_buttons_state(buttons)

    trot=(float(data[5])/255)
    brea=(float(data[6])/255)
    clu=(float(data[7])/127.5)-1

    gamepad.right_trigger_float(trot)
    gamepad.left_trigger_float(brea)
    gamepad.right_joystick_float(clu, 0)

    #print(angle)
    gamepad.left_joystick_float(angle, 0)

disable_wheel=False
disable_pedals=False

args = sys.argv
if "--help" in args or "-h" in args:
    print("""Usage: driver.py [OPTIONS]
    OPTIONS:
    -h, --help    show this message
""")
    exit(0)


gamepad = vg.VX360Gamepad()
gamepad.reset()

socket=connect()

target=0
quit_data=b'0xff'

try:
    while True:
        update()
        gamepad.update()

except KeyboardInterrupt:
    print("disconnecting...")
    socket.send(quit_data)
    time.sleep(0.1)
    raise


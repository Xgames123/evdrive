#!/bin/python3
import vgamepad as vg
import time
from os import environ
import socket
import sys

ADDR=("evwheel", 6769)
PEDALS_ADDR=("evpedals", 6969)

MAX_WHEEL_ANGLE=540

CMD_CALIB=1
CMD_FOLLOW_ON=2
CMD_FOLLOW_OFF=3
CMD_FFB_ON=4
CMD_FFB_OFF=5


def connect(addr):
    s=None
    info = socket.getaddrinfo(addr[0], addr[1], proto=socket.IPPROTO_UDP)
    ipv6_addr=info[0][4]
    print("Connecting to ", ipv6_addr)
    s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    s.settimeout(3)
    s.connect(ipv6_addr)
    return s

def update_buttons_state(val):
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
    global s
    global ps
    send_data=bytearray()
    send_data.append(0) # command
    send_count = s.send(send_data)
    if send_count == 0:
        print("no data send to wheel")
        return
    if ps:
        send_count = ps.send(send_data)
    if send_count == 0:
        print("no data send to pedals")
        return

    data = None
    data = None
    try:
        if ps:
            data, addr = s.recvfrom(5)
        else:
            data, addr = s.recvfrom(8)
    except Exception as e:
        print("recv wheel fail:",e)
        return

    angle=float(int.from_bytes(data[0:4], "big", signed= True))
    angle=-((angle-MAX_WHEEL_ANGLE)/MAX_WHEEL_ANGLE)

    buttons=data[4]
    update_buttons_state(buttons)

    gamepad.left_joystick_float(angle, 0)
    gamepad.update()

    pedlas_addr = None
    pedals_addr = None
    if ps:
        try:
            pedals_data, pedals_addr = ps.recvfrom(3)
        except Exception as e:
            print("recv pedals fail:",e)
            return

    if ps:
        data = pedals_data
    else:
        data = data[4:]

    trot=(float(data[0])/255)
    brea=(float(data[1])/255)
    clu=(float(data[2])/127.5)-1

    gamepad.right_trigger_float(trot)
    gamepad.left_trigger_float(brea)
    gamepad.right_joystick_float(clu, 0)
    gamepad.update()

    #print(angle)

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

s=connect(ADDR)
ps = None
if PEDALS_ADDR:
    ps=connect(PEDALS_ADDR)

target=0
quit_data=b'0xff'

try:
    while True:
        update()

except KeyboardInterrupt:
    print("disconnecting...")
    s.send(quit_data)
    time.sleep(0.1)
    raise


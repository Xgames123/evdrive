#!/bin/python3
import vgamepad as vg
import time
from os import environ
import socket
import sys

MAX_WHEEL_ANGLE=360

CMD_CALIB=1
CMD_FOLLOW_ON=2
CMD_FOLLOW_OFF=3
CMD_FFB_ON=4
CMD_FFB_OFF=5


def connect(env_name, default_ip, name):
    addr=None
    s=None
    addr=(default_ip, 6769)
    if env_name in environ:
        addr=(environ[env_name], 6769)
    print("Connecting to", name, addr)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(2)
    s.connect(addr)
    return addr, s

def connect_pedals():
    return connect("PEDALS_IP","192.168.137.4", "pedals")
def connect_wheel():
    addr, s = connect("WHEEL_IP", "192.168.137.3", "wheel")
    wheel_send_packet(s, 0, CMD_FFB_OFF)
    return addr, s


def wheel_send_packet(socket, wheel, target, cmd=0):
    if disable_wheel:
        return
    send_data=bytearray(target.to_bytes(4, "big"))
    send_data.append(cmd)
    socket.sendall(send_data)


def do_pedals():
    global pedals_s
    global disable_pedals
    pedals_data=b'0x00'
    if pedals_s.send(pedals_data) == 0:
        print("failed to send pedal data")
        raise
        return

    addr = None
    data = None
    try:
        data, addr=pedals_s.recvfrom(3)
    except:
        print("failed to recv pedal data")
        time.sleep(1)
        return

    trot=(float(data[0])/255)
    brea=(float(data[1])/255)
    clu=(float(data[2])/127.5)-1

    gamepad.right_trigger_float(trot)
    gamepad.left_trigger_float(brea)
    gamepad.right_joystick_float(clu, 0)

def do_steering_wheel():
    send_data=bytearray(target.to_bytes(4, "big"))
    send_data.append(0)
    wheel_s.send(send_data)

    data = None
    addr = None
    try:
        data, addr = wheel_s.recvfrom(7)
    except:
        print("failed to recv steering data")
        time.sleep(1)
        return
    angle=float(int.from_bytes(data[0:4], "big", signed= True))
    angle=(angle-MAX_WHEEL_ANGLE)/MAX_WHEEL_ANGLE
    if data[4] == 1:
        #print("start button")
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_B)
    else:
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_B)
    if data[5] == 1:
        #print("gear l button")
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
    else:
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
    if data[6] == 1:
        #print("gear r button")
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
    else:
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)

    #print(angle)
    gamepad.left_joystick_float(angle, 0)

disable_wheel=False
disable_pedals=False

args = sys.argv
if "-dp" in args:
    disable_pedals=True
elif "-dw" in args:
    disable_wheel=True
elif "--help" in args or "-h" in args:
    print(
"""A program for connecting to pedals.py and wheel.py and creating a virutal joystick from the input
driver.py [OPTIONS]
    OPTIONS:
    -dp           disable pedals
    -dw           disable wheel
    -h, --help    show this message
""")

    exit(0)

if disable_wheel and disable_pedals:
    print("ERR: steering and pedals can not be disabled at the same time")
    exit(1)

gamepad = vg.VX360Gamepad()
gamepad.reset()

wheels_addr = None
wheel_s = None
if not disable_wheel:
    wheel_addr, wheel_s = connect_wheel()
else:
    print("wheel disabled")

pedals_addr = None
pedals_s = None
if not disable_pedals:
    pedals_addr, pedals_s = connect_pedals()
else:
    print("pedals disabled")


target=0
quit_data=b'0xff'

try:
    while True:
        if not disable_pedals:
            do_pedals()
        if not disable_wheel:
            do_steering_wheel()
        gamepad.update()


except KeyboardInterrupt:
    print("disconecting")
    pedals_s.send(quit_data)
    wheel_s.send(quit_data)
    time.sleep(1)
    raise


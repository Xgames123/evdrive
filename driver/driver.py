#!/bin/python3
import vgamepad as vg
import time
import socket
import sys

WHEEL_IP="169.254.211.203"
WHEEL_PORT=6769

PEDALS_IP="169.254.2.151"
PEDALS_PORT=6767

DISABLE_STEERING=False
DISABLE_PEDALS=False

# TODO: send stop calib packet to pedals after some time
# TODO: auto detect ips ?

CMD_CALIB=1
CMD_FOLLOW_ON=2
CMD_FOLLOW_OFF=3
CMD_FFB_ON=4
CMD_FFB_OFF=5

def wheel_send_packet(target, cmd=0):
    global wheel_s
    if DISABLE_STEERING:
        return
    send_data=bytearray(target.to_bytes(4, "big"))
    send_data.append(cmd)
    wheel_s.sendall(send_data)


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
    except socket.timeout:
        print("failed to recv pedal data")
        return

    trot=float(data[0])/255
    brea=float(data[1])/255
    clu=float(data[2])/255

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
    except socket.timeout:
        print("failed to recv steering data")
        return
    angle=float(int.from_bytes(data[0:4], "big", signed= True))
    angle=(angle-360)/360
    angle=angle
    if data[4] == 1:
        print("start button")
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_B)
    else:
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_B)
    if data[5] == 1:
        print("gear l button")
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
    else:
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
    if data[6] == 1:
        print("gear r button")
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
    else:
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)

    #print(angle)
    gamepad.left_joystick_float(angle, 0)

args = sys.argv
if "-dp" in args:
    DISABLE_PEDALS=True
elif "-ds" in args:
    DISABLE_STEERING=True

gamepad = vg.VX360Gamepad()
gamepad.reset()

wheel_s=None
if not DISABLE_STEERING:
    print("Connecting to wheel")
    wheel_s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    wheel_s.settimeout(2)
    wheel_s.connect((WHEEL_IP, WHEEL_PORT))

pedals_s=None
if not DISABLE_PEDALS:
    print("Connecting to pedals")
    pedals_s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    pedals_s.settimeout(2)
    pedals_s.connect((PEDALS_IP, PEDALS_PORT))

if "-f" in args:
    wheel_send_packet(0, CMD_FOLLOW_ON)
elif "-c" in args:
    wheel_send_packet(0, CMD_CALIB)

wheel_send_packet(0, CMD_FFB_OFF)


target=0
quit_data=b'0xff'
try:
    while True:
        if not DISABLE_PEDALS:
            do_pedals()
        if not DISABLE_STEERING:
            do_steering_wheel()
        gamepad.update()

        if DISABLE_STEERING and DISABLE_PEDALS:
            print("ERR: steering or pedals need to be enabled")
            break

except KeyboardInterrupt:
    print("disconecting")
    pedals_s.send(quit_data)
    wheel_s.send(quit_data)
    time.sleep(1)
    raise


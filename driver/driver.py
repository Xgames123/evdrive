#!/bin/python3
import vgamepad as vg
import time


import socket
import sys

WHEEL_IP="10.42.0.3"
WHEEL_PORT=6769

PEDALS_IP="ev3dev"
PEDALS_PORT=6767

CMD_CALIB=1
CMD_FOLLOW_ON=2
CMD_FOLLOW_OFF=3
CMD_FFB_ON=4
CMD_FFB_OFF=5

def wheel_send_packet(target, cmd=0):
    send_data=bytearray(target.to_bytes(4, "big"))
    send_data.append(cmd)
    wheel_s.sendall(send_data)


def do_steering_wheel():
    send_data=bytearray(target.to_bytes(4, "big"))
    send_data.append(0)
    wheel_s.sendall(send_data)

    data = wheel_s.recv(5)
    angle=int.from_bytes(data[0:4], "big", signed= True)
    if data[4] == 1:
        print("start button")

    print(angle)
    #TODO: map this
    gamepad.left_joystick_float(x_value_float=angle)


gamepad = vg.VX360Gamepad()
gamepad.reset()

print("Connecting to wheel")
#wheel_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#wheel_s.connect((WHEEL_IP, WHEEL_PORT))

print("Connecting to pedals")
pedals_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
pedals_s.connect((PEDALS_IP, PEDALS_PORT))

print("PRESS EVERY PEDAL FULLY DOWN TO CALIBRATE")
time.sleep(2)

target=0
args = sys.argv
if "-f" in args:
    wheel_send_packet(0, CMD_FOLLOW_ON)
elif "-c" in args:
    wheel_send_packet(0, CMD_CALIB)


pedals_data=b'0x00'
try:
    while True:

        pedals_s.sendall(pedals_data)

        pedals_data=pedals_s.recv(3)

        trot=float(pedals_data[0])/255
        brea=float(pedals_data[1])/255
        clu=float(pedals_data[2])/255
        print(trot)

        gamepad.right_trigger_float(trot)
        gamepad.left_trigger_float(brea)
        gamepad.left_joystick_float(0, clu)
        #do_steering_wheel()
        gamepad.update()

except KeyboardInterupt:
    pedals_s.close()
    wheel_s.close()


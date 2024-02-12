#!/usr/bin/env python3
from time import sleep
import math
import socket

from ev3dev2.motor import LargeMotor, OUTPUT_D, SpeedPercent
from ev3dev2.sensor import INPUT_2, INPUT_1, INPUT_3, INPUT_4
from ev3dev2.sensor.lego import GyroSensor, TouchSensor
from ev3dev2.button import Button
from ev3dev2.sound import Sound
#from ev3dev2.display import Display
#import ev3dev2.fonts as fonts

ADDR=("0.0.0.0", 6769)
PEDALS_ADDR=("evpedals", 6969)

MAX_FORCE=230
MAX_ANGLE=540


def clamp01(n):
    return clamp(n, 0, 1)
def clamp(n, minv, maxv):
    return max(minv, min(n, maxv))

def to01(value, minb, maxb):
    if maxb-minb == 0:
        return 0
    return clamp01(float(value - minb) / float(maxb-minb))

def calibrate():
    print("calibrating...")
    global calibrated
    global sound
    m.reset()
    sound.beep()
    calibrated=True
    print("calib done")


print("setting up devices")

start_button=TouchSensor(INPUT_1)
gear_switch_l=TouchSensor(INPUT_3)
gear_switch_r=TouchSensor(INPUT_4)
m = LargeMotor(OUTPUT_D)
m.stop_action="coast"
buttons = Button()
sound = Sound()
#display = Display()
#title_font=fonts.load("courB24")
#text_font=fonts.load("courR14")


def manual_zeroing():
    print("Zero wheel: u/d")
    while True:
       cmd = input()
       if cmd == "u":
           m.on_for_degrees(SpeedPercent(50), 30)
       elif cmd == "U":
           m.on_for_degrees(SpeedPercent(50), 90)
       elif cmd == "d":
           m.on_for_degrees(SpeedPercent(50), -30)
       elif cmd == "D":
           m.on_for_degrees(SpeedPercent(50), -90)
       elif cmd == "":
           break

# def update_screen():
#     global display
#     global title_font
#     global text_font
#     display.text_grid("evdrive", x=(22/2)+(7/2), y=0, font=title_font, clear_screen=False)
#     display.text_grid("address:   {IP}:{PORT}", x=1, y=2, font=text_font,clear_screen=False)
#     display.text_grid( "max_angle: {MAX_ANGLE} deg",x=1, y=3, font=text_font, clear_screen=False)
#     display.update()

#update_screen()
print("zeroing wheel")
m.stop_action="brake"
m.on_to_position(SpeedPercent(10), 0)
m.stop_action="coast"
calibrate()
def run():
    global s
    global pedals_socket
    global calibrated
    global buttons
    global sound
    print("listening on", ADDR)

    target_pos=0
    angle=0
    while True:
        if buttons.enter:
            calibrate()

        data, addr = s.recvfrom(1)
        command=data[0]
        pedals_socket.send(command)
        if command == 255:
            print("quit")
            sound.beep()
            print("forwarding to pedals...")
            pedals_socket.send(command)
            sound.beep()
            return
        elif command == 1: # echo
            s.sendto(b'\x01', addr)
            continue
        elif command == 2:
            calibrate()

        angle = (m.position/m.count_per_rot)*360.0
        if angle > MAX_ANGLE :
            m.position_sp=m.count_per_rot*(MAX_ANGLE/360)
            m.speed_sp=m.max_speed*0.1
            m.run_to_abs_pos()
        elif angle < -MAX_ANGLE:
            m.position_sp=m.count_per_rot*(-MAX_ANGLE/360)
            m.speed_sp=m.max_speed*0.1
            m.run_to_abs_pos()

        send_data = bytearray(int((clamp(angle, -MAX_ANGLE, MAX_ANGLE)+MAX_ANGLE)).to_bytes(4, 'big', signed=True))

        buttons=(start_button.is_pressed) | (gear_switch_l.is_pressed << 1) | (gear_switch_r.is_pressed << 2)
        send_data.append(buttons)

        data = pedals_socket.recvfrom(4)
        pedals_status=data[0]
        send_data.append(data[1])
        send_data.append(data[2])
        send_data.append(data[3])

        try:
            s.sendto(send_data, addr)
        except:
            print("Failed to send data. closing connection")
            return


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(ADDR)

pedals_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
pedals_socket.settimeout(2)
print("connecting to", PEDALS_ADDR)
pedals_socket.connect(PEDALS_ADDR)
while True:
    try:
        run()
    except KeyboardInterrupt:
        pedals_socket.close()
        s.close()

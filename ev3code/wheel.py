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

IP="0.0.0.0"
PORT=6769

MAX_FORCE=230
MAX_ANGLE=360


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
display = Display()
title_font=fonts.load("courB24")
text_font=fonts.load("courR14")
sound = Sound()


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
    global socket
    global calibrated
    global buttons
    global sound
    print("listening on ", IP, ":", PORT)

    target_pos=0
    follow=False
    ffb=True
    angle=0
    while True:
        if buttons.enter:
            calibrate()

        data, addr = socket.recvfrom(5)
        if len(data) == 1:
            if data[0] == 255:
                print("quit")
                sound.beep()
                sound.beep()
                return
            elif data[0] == 1: # echo
                socket.sendto(b'\x01', addr)
                continue

        if len(data) != 5:
            print("Invalid data. closing connection")
            sound.beep()
            sound.beep()
            return
        target=int.from_bytes(data[0:4], "big", signed= True)
        if data[4] == 1:
            calibrate()
        elif data[4] == 2:
            follow=True
        elif data[4] == 3:
            follow = False
        #elif data[4] == 4:
        #    ffb = True
        #elif data[4] == 5:
        #    ffb = False

        angle = (m.position/m.count_per_rot)*360.0
        #if ffb:
            #delta=m.position-m.position_sp

            #print(abs(target-angle))
            #if target-angle > MAX_FORCE:
            #    target=angle+MAX_FORCE
            #elif target-angle < -MAX_FORCE:
            #    target=angle-MAX_FORCE
            #
            #if follow:
            #    target=angle
            #
            #target_pos = clamp(target, -MOTOR_LIMIT, MOTOR_LIMIT)


            #m.position_sp = target_pos
            #m.speed_sp = m.max_speed*clamp01(abs(delta)/FOLLOW_MARGIN)
            #m.run_to_abs_pos()
        if angle > MAX_ANGLE :
            m.position_sp=m.count_per_rot*(MAX_ANGLE/360)
            m.speed_sp=m.max_speed*0.1
            m.run_to_abs_pos()
        elif angle < -MAX_ANGLE:
            m.position_sp=m.count_per_rot*(-MAX_ANGLE/360)
            m.speed_sp=m.max_speed*0.1
            m.run_to_abs_pos()

        send_data = bytearray(int((clamp(angle, -MAX_ANGLE, MAX_ANGLE)+MAX_ANGLE)).to_bytes(4, 'big', signed=True))
        if start_button.is_pressed:
            send_data.append(1)
        else:
            send_data.append(0)

        if gear_switch_l.is_pressed:
            send_data.append(1)
        else:
            send_data.append(0)

        if gear_switch_r.is_pressed:
            send_data.append(1)
        else:
            send_data.append(0)

        try:
            socket.sendto(send_data, addr)
        except:
            print("Failed to send data. closing connection")
            return



socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket.bind((IP, PORT))
while True:
    try:
        run()
    except KeyboardInterrupt:
        #m.stop()
        socket.close()

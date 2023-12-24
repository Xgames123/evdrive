#!/bin/python3
from time import sleep
import math
import socket

from ev3dev2.motor import LargeMotor, OUTPUT_A, SpeedPercent
from ev3dev2.sensor import INPUT_2, INPUT_1
from ev3dev2.sensor.lego import GyroSensor, TouchSensor

IP="10.42.0.3"
PORT=6769

FOLLOW_MARGIN=50
CALIB_LEN=4
#CALIB_LEN=20
CALIB_JUMP=30
#CALIB_DELAY=1.5
CALIB_DELAY=1
MAX_FORCE=230

def clamp01(n):
    return clamp(n, 0, 1)
def clamp(n, minv, maxv):
    return max(minv, min(n, maxv))

def calib_segment(count, direct=1):
    offsets=[]
    for i in range(count):
        motor_rot=(CALIB_JUMP*(i+1))*direct
        m.on_to_position(SpeedPercent(50), motor_rot)
        sleep(1.5)
        angle=s.angle
        new_offset=(motor_rot/angle)
        print("offset="+str(new_offset))
        offsets.append(new_offset)
        print(str(i+1)+"/"+str(count))
    return offsets

def calibrate(count=CALIB_LEN):
    global calibrated
    calibrated = True
    print("calibrating...")
    m.on_to_position(SpeedPercent(100), 0)
    sleep(1.5)
    offsets=calib_segment(math.floor(count/2), 1)
    m.on_to_position(SpeedPercent(100), 0)
    sleep(1.5)
    offsets+=calib_segment(math.ceil(count/2), -1)
    m.on_to_position(SpeedPercent(100), 0)

    offsets.sort()
    global offset
    offset = offsets[len(offsets)//2]
    print(offset)
    print("calibrating done")
    print("offset="+str(offset))


print("searching for devices...")

start_button=TouchSensor(INPUT_1)
m = LargeMotor(OUTPUT_A)
s = GyroSensor(INPUT_2)


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

print("zeroing wheel based of of previous data")
m.on_to_position(SpeedPercent(100), 0)
manual_zeroing()

print("zeroing sensor")

m.reset()
s.calibrate()


offset=3
calibrated=False

calibrate()
def run():
    global socket
    global calibrated
    print("Waiting for connection")
    socket.listen(1)
    con, addr = socket.accept()
    print("Got connection from ", addr)
    if not calibrated:
        calibrate(CALIB_LEN)

    target_pos=0
    follow=False
    while True:
        data = con.recv(5)
        if len(data) != 5:
            print("Invalid data. closing connection")
            con.close()
            return
        target=int.from_bytes(data[0:4], "big", signed= True)
        if data[4] == 1:
            calibrate(CALIB_LEN)
        elif data[4] == 2:
            follow=True
        elif data[4] == 3:
            follow = False

        angle = s.angle*offset
        delta=m.position-m.position_sp

        print(abs(target-angle))
        if target-angle > MAX_FORCE:
            target=angle+MAX_FORCE
        elif target-angle < -MAX_FORCE:
            target=angle-MAX_FORCE

        if follow:
            target=angle

        target_pos = clamp(target, -1200, 1200)


        m.position_sp = target_pos
        m.speed_sp = m.max_speed*clamp01(abs(delta)/FOLLOW_MARGIN)
        m.run_to_abs_pos()
        send_data = bytearray(int(angle).to_bytes(4, 'big', signed=True))
        if start_button.is_pressed:
            send_data.append(1)
        else:
            send_data.append(0)
        
        try:
            con.send(send_data)
        except:
            print("Failed to send data. closing connection")
            con.close()
            return



m.position_sp = 0
m.speed_sp=m.max_speed
m.stop_action="coast"

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.bind((IP, PORT))
while True:
    try:
        run()
    except KeyboardInterrupt:
        m.stop()
        socket.close()

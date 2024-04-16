#!/usr/bin/env python3
from time import sleep
from ev3dev2.motor import LargeMotor, OUTPUT_D, OUTPUT_B, OUTPUT_C
from ev3dev2.sound import Sound
import math
import socket
import sys

ADDR=("::", 6969)

TROT_MIN=-34
TROT_MAX=1

BRAKE_MIN=-30
BRAKE_MAX=1

CLU_MIN=-43
CLU_MAX=-6

def clamp01(n):
    return clamp(n, 0, 1)

def clamp(n, minv, maxv):
    return max(minv, min(n, maxv))

def to01(value, minb, maxb):
    if maxb-minb == 0:
        return 0
    return clamp01(float(value - minb) / float(maxb-minb))

class Pedal:
    def __init__(self, addr, name, rot_min, rot_max):
        m=LargeMotor(addr)
        self.m=m
        self.min=rot_min
        self.max=rot_max
        self.calibrated=False
        self.name = name

    def calib(self):
        global sound
        val = self.m.position
        if val < self.min:
            self.min=val
        if not self.calibrated and self.min < self.max-5 and val > self.max-5:
            print(self.name, "calibrated")
            sound.beep()
            self.calibrated=True
        return self.calibrated

    def start_calib(self):
        self.min = 0
        self.max = self.m.position
        self.calibrated=False

    def get(self):
        val=self.m.position
        mapped_val= to01(val, self.max, self.min)
        return mapped_val

def calibrate():
    global trot
    global brea
    global clu
    print("Calibrating...")
    trot.start_calib()
    brea.start_calib()
    clu.start_calib()
    print("PRESS DOWN ALL PEDALS SLOWLY")

    while True:
        if trot.calib() & brea.calib() & clu.calib():
            sound.beep()
            print("calibration done")
            print("trot: ", trot.min, trot.max, ", brake:", brea.min, brea.max,", clu:", clu.min, clu.max)
            exit(0)



def run():
    global sound
    global s
    global trot
    global brea
    global clu
    while True:

        data, addr = s.recvfrom(1)
        if len(data) == 1:
            if data[0] == 255:
                print("quit")
            elif data[0] == 1: # echo
                s.sendto(b"\x01", addr)
                continue

        send_data = bytearray()
        send_data.append(int(trot.get()*255))
        send_data.append(int(brea.get()*255))
        send_data.append(int(clu.get()*255))

        try:
            s.sendto(send_data, addr)
        except:
            print("Failed to send data. closing connection")
            return

args = sys.argv
if "--help" in args or "-h" in args:
    print("""Usage: driver.py [OPTIONS]
    OPTIONS:
    -h, --help    show this message
    -c, --calib   calculate ROT_MIN and ROT_MAX
""")
    exit(0)


trot=Pedal(OUTPUT_D, "trot", TROT_MIN, TROT_MAX)
brea=Pedal(OUTPUT_C, "brake", BRAKE_MIN, BRAKE_MAX)
clu=Pedal(OUTPUT_B, "clutch", CLU_MIN, CLU_MAX)
sound = Sound()
sound.beep()

if "--calib" in args or "-c" in args:
    calibrate()

s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
info = socket.getaddrinfo(ADDR[0], ADDR[1], proto=socket.IPPROTO_UDP)
IPV6_ADDR=info[0][4]
s.bind(IPV6_ADDR)

print("listening on", IPV6_ADDR)
while True:
    try:
        run()
    except KeyboardInterrupt:
        s.close()

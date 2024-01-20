#!/bin/python3
from time import sleep
from ev3dev2.motor import LargeMotor, OUTPUT_D, OUTPUT_B, OUTPUT_C
from ev3dev2.sound import Sound
import math
import socket

IP="0.0.0.0"
PORT=6769

def clamp01(n):
    return clamp(n, 0, 1)

def clamp(n, minv, maxv):
    return max(minv, min(n, maxv))

def to01(value, minb, maxb):
    if maxb-minb == 0:
        return 0
    return clamp01(float(value - minb) / float(maxb-minb))

class Pedal:
    def __init__(self, addr, name):
        m=LargeMotor(addr)
        self.m=m
        self.zero=m.position
        self.min=self.zero
        self.calibrated=False
        self.name = name

    def calib(self):
        global sound
        val = self.m.position
        if val < self.min:
            self.min=val
        if not self.calibrated and self.min < self.zero-5 and val > self.zero-5:
            print(self.name, "calibrated")
            sound.beep()
            self.calibrated=True
        return self.calibrated

    def start_calib(self):
        self.calibrated=False

    def get(self):
        val=self.m.position
        mapped_val= to01(val, self.zero, self.min)
        return mapped_val


def run():
    global sound
    global socket
    global trot
    global brea
    global clu
    global calib
    if calib:
        print("Calibrating...")
        trot.start_calib()
        brea.start_calib()
        clu.start_calib()
        print("PRESS DOWN ALL PEDALS SLOWLY")
    else:
        print("listening on ", IP, ":", PORT)
    while True:
        if calib:
            if trot.calib() & brea.calib() & clu.calib():
                sound.beep()
                print("calibration done")
                print("listening on ", IP, ":", PORT)
                calib=False
            continue

        data, addr = socket.recvfrom(1)
        if data[0] == 255:
            print("quit")
        elif data[0] == 1: # echo
            socket.sendto(b"\x01", addr)
            continue

        send_data = bytearray()
        send_data.append(int(trot.get()*255))
        send_data.append(int(brea.get()*255))
        send_data.append(int(clu.get()*255))
        print(send_data)

        try:
            socket.sendto(send_data, addr)
        except:
            print("Failed to send data. closing connection")
            return


trot=Pedal(OUTPUT_D, "trot")
brea=Pedal(OUTPUT_C, "break")
clu=Pedal(OUTPUT_B, "cluch")
sound = Sound()
sound.beep()


socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket.bind((IP, PORT))
calib=True
while True:
    try:
        run()
    except KeyboardInterrupt:
        socket.close()

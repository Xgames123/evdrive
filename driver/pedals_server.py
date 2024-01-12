#!/bin/python3
from time import sleep
from ev3dev2.motor import LargeMotor, OUTPUT_D, OUTPUT_B, OUTPUT_C
import math
import socket

IP="0.0.0.0"
PORT=6767

def clamp01(n):
    return clamp(n, 0, 1)
def clamp(n, minv, maxv):
    return max(minv, min(n, maxv))
def to01(value, minb, maxb):
    if maxb-minb == 0:
        return 0
    return clamp01(float(value - minb) / float(maxb-minb))

class Pedal:
    def __init__(self, addr):
        m=LargeMotor(addr)
        self.m=m
        self.zero=m.position
        self.min=self.zero

    def get(self):
        val=self.m.position
        if calib and val < self.min:
            self.min=val
        mapped_val= to01(val, self.zero, self.min)
        return mapped_val


def run():
    global socket
    global trot
    global brea
    global clu
    global calib
    print("listening on ", IP, ":", PORT)
    calib=True
    while True:
        data, addr = socket.recvfrom(1)
        if data[0] == 255:
            print("quit")
            return
        elif data[0] == 1:
            print("stop calibration")
            calib=False
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


trot=Pedal(OUTPUT_D)
brea=Pedal(OUTPUT_C)
clu=Pedal(OUTPUT_B)



socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket.bind((IP, PORT))
calib=True
while True:
    try:
        run()
    except KeyboardInterrupt:
        socket.close()

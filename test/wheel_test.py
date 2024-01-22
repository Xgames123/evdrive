#!/bin/python3

import socket
import sys

IP="192.168.137.3"
PORT=6769

CMD_CALIB=1
CMD_FOLLOW_ON=2
CMD_FOLLOW_OFF=3

MAX_WHEEL_ANGLE=360

def send_packet(target, cmd=0):
    send_data=bytearray(target.to_bytes(4, "big"))
    send_data.append(cmd)
    s.sendall(send_data)


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.settimeout(2)
s.connect((IP, PORT))
print(f"connecting to ({IP}:{PORT})")
target=0

args = sys.argv
if "-f" in args:
    send_packet(0, CMD_FOLLOW_ON)
elif "-c" in args:
    send_packet(0, CMD_CALIB)

try:
    while True:
        send_data=bytearray(target.to_bytes(4, "big"))
        send_data.append(0)
        s.send(send_data)

        data = None
        addr = None
        try:
            data, addr = s.recvfrom(7)
        except:
            print("failed to recv steering data")
            continue
        angle=float(int.from_bytes(data[0:4], "big", signed= True))
        angle=(angle-MAX_WHEEL_ANGLE)/MAX_WHEEL_ANGLE

        if data[4] == 1:
            print("start button")
        if data[5] == 1:
            print("gear l button")
        if data[6] == 1:
            print("gear r button")

        print(angle)
except KeyboardInterrupt:
    exit(1)


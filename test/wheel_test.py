#!/bin/python3

import socket
import sys

IP="10.42.0.3"
PORT=6769

CMD_CALIB=1
CMD_FOLLOW_ON=2
CMD_FOLLOW_OFF=3

def send_packet(target, cmd=0):
    send_data=bytearray(target.to_bytes(4, "big"))
    send_data.append(cmd)
    s.sendall(send_data)


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((IP, PORT))
target=0

args = sys.argv
if "-f" in args:
    send_packet(0, CMD_FOLLOW_ON)
elif "-c" in args:
    send_packet(0, CMD_CALIB)

while True:
    send_data=bytearray(target.to_bytes(4, "big"))
    send_data.append(0)
    s.sendall(send_data)

    data = s.recv(5)
    angle=int.from_bytes(data[0:4], "big", signed= True)
    if data[4] == 1:
        print("button")
    print(angle)


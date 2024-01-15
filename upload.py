# Uploads the scripts to the ev3's
from os import environ, system, path
import platform

# Magic code to fix windows garbage
system32 = path.join(environ['SystemRoot'], 'SysNative' if
platform.architecture()[0] == '32bit' else 'System32')

SCP = path.join(system32, 'openSSH', 'scp.exe')

pedals_ip="192.168.137.4"
if "PEDALS_IP" in environ:
    pedals_ip=environ["PEDALS_IP"]

wheel_ip="192.168.137.3"
if "WHEEL_IP" in environ:
    wheel_ip=environ["WHEEL_IP"]

print("pedals", pedals_ip)
system(f"{SCP} ev3code/pedals_server.py robot@{pedals_ip}:pedals_server.py")


print("wheel", wheel_ip)
system(f"{SCP} ev3code/wheel_server.py robot@{wheel_ip}:wheel_server.py")



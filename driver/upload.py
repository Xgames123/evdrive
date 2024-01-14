# Uploads the scripts to the ev3's
from os import environ, system, path
import platform

# Magic code to fix windows garbage
system32 = path.join(environ['SystemRoot'], 'SysNative' if
platform.architecture()[0] == '32bit' else 'System32')

SCP = path.join(system32, 'openSSH', 'scp.exe')

if not "PEDALS_IP" in environ or not "WHEEL_IP" in environ:
    print("PEDALS_IP and WHEEL_IP environment variables are required")
    exit(1)

pedals_ip=environ["PEDALS_IP"]
wheel_ip=environ["WHEEL_IP"]

print("pedals")
system(f"{SCP} ./pedals_server.py robot@{pedals_ip}:pedals_server.py")


print("wheels")
system(f"{SCP} ./wheel_server.py robot@{wheel_ip}:wheel_server.py")



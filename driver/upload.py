# Uploads the scripts to the ev3's
from os import environ, system

if not "PEDALS_IP" in environ or not "WHEEL_IP" in environ:
    print("PEDALS_IP and WHEEL_IP environment variables are required")
    exit(1)

pedals_ip=environ["PEDALS_IP"]
wheel_ip=environ["WHEEL_IP"]

print("pedals")
system(f"scp ./pedals_server.py robot@{pedals_ip}:pedals_server.py")
system(f"ssh robot@{pedals_ip} python3 pedals_server.py")

print("wheels")
system(f"scp ./wheel_server.py robot@{wheel_ip}:wheel_server.py")
system(f"ssh robot@{wheel_ip} python3 wheel_server.py")

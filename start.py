from paramiko.client import SSHClient, SSHException
from os import environ, system
from sys import argv
import time

def env_var(name, default_value):
    value=default_value
    if name in environ:
        value=environ[name]
    return value

def setup(name, default_ip, default_username, default_passwd, upload=False, interactive=True):
    global ssh
    ip = env_var(name.upper()+"_IP", default_ip)
    username = env_var(name.upper()+"_USERNAME", default_username)
    passwd = env_var(name.upper()+"_PASSWD", default_passwd)

    print(f"Connecting to {name} ({username}@{ip})")
    ssh.connect(ip, username=username, password=passwd)

    if upload:
        print("creating sftp connection...")
        ftp = ssh.open_sftp()
        print("uploading files...")
        ftp.put(f"ev3code/{name}.py", f"{name}.py")
        return

    print("killing all python3's on ev3")
    ssh.exec_command("killall python3")
    time.sleep(1)
    print("starting new program on ev3")
    channel=ssh.get_transport().open_session()
    channel.exec_command(f"python3 {name}.py")
    return channel

def run_channel(channel, name):
    if channel != None:
        if channel.exit_status_ready():
            print(f"{name} stopped output:")
            file = channel.makefile()
            file_err = channel.makefile_stderr()
            for line in file.readlines():
                print(line)
            for line in file_err.readlines():
                print(line)
            file.close()
            file_err.close()
            channel=None
            return False

    return True

if "--help" in argv or "-h" in argv:
    print(
"""Setup and start evdrive
usage: start.py [OPTIONS]
    OPTIONS:
    -u, --upload  upload the python files to the ev3s
    -dp           disable pedals
    -dw           disable wheel
    -h, --help    show this message
""")

    exit(0)

upload=False
if "-u" in argv or "--upload" in argv:
    upload=True

ssh = SSHClient()
ssh.load_system_host_keys()
print("host keys loaded")

wheel_channel=None
pedals_channel=None
driver_args=""
if "-dw" in argv:
    driver_args+=" -dw"
else:
    wheel_channel = setup("wheel", "192.168.137.3", "robot", "maker", upload=upload)
if "-dp" in argv:
    driver_args+=" -dp"
else:
    pedals_channel = setup("pedals", "192.168.137.4", "robot", "maker", upload=upload)

if upload:
    print("upload done")
    exit(0)

print("starting driver...")
print(driver_args)
system("python driver.py "+driver_args)
try:
    while run_channel(pedals_channel, "pedals") & run_channel(wheel_channel, "wheel"):
        pass
    exit(0)
except:
    ssh.close()
    raise

from paramiko.client import SSHClient, SSHException
from os import environ
from sys import argv

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
        info = ftp.put(f"ev3code/{name}.py", f"{name}.py")
        print("mode", info.st_mode)
        if info.st_mode != 33261:
            print("changing mode")
            file = ftp.file(f"{name}.py")
            file.chmod(33261)
            file.close()

    return ssh.exec_command(f"python3 {name}.py")

upload=False
if "-u" in argv or "--upload" in argv:
    upload=True

ssh = SSHClient()
ssh.load_system_host_keys()
print("host keys loaded")

wheel_channel=None
pedals_channel=None
if not "-dw" in argv:
    wheel_channel = setup("wheel", "192.168.137.3", "robot", "maker", upload=upload)
if not "-dp" in argv:
    pedals_channel = setup("pedals", "192.168.137.4", "robot", "maker", upload=upload)

while True:
    if pedals_channel != None:
        stdin, stdout, stderr = pedals_channel
        print("pedals:", stdout)
        print("pedals_err:", stderr)
    if wheel_channel != None:
        stdin, stdout, stderr = wheel_channel
        print("wheel:", stdout)
        print("wheel_err:", stderr)

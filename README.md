# evdrive
Steering wheel + pedals made with the lego ev3

[![demo video](https://img.youtube.com/vi/g0dI3Tlzhqg/0.jpg)](https://www.youtube.com/watch?v=g0dI3Tlzhqg)

# build instructions
Here are some [images](images/) form different angles

# Software setup
1. Install [ev3dev](ev3dev.org) on your 2 ev3s
2. [connect the 2 ev3's to your pc](https://www.ev3dev.org/docs/networking)
3. Open 2 ssh sessions for your 2 ev3's
4. Change /etc/hostname to evwheel for your wheel and evpedals for your pedals.
5. Copy wheel.py to evwheel and pedals.py to evpedals
5. REBOOT THE 2 EV3'S
6. Run driver.py on the windows host and start wheel.py and pedals.py on the right ev3. By going to > filebrowser > wheel.py/pedals.py (The screen should go blank for 5seconds)
7. Done

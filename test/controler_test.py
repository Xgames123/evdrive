import vgamepad as vg

gamepad = vg.VX360Gamepad()
gamepad.reset()

direction=False
dec_streak=0
last_force=0

def my_callback(client, target, large_motor, small_motor, led_number, user_data):
    global direction
    global last_force
    global dec_streak
    force=large_motor+small_motor
    if force < last_force:
        dec_streak+=1
    else:
        dec_streak=0
    if dec_streak > 4:
        print("dir switch")
        direction = not direction
    dirforce=force
    if direction:
        dirforce = -force
    #print(f"{dirforce}")
    last_force=force

gamepad.register_notification(callback_function=my_callback)

while True:
    pass

from gpiozero import AngularServo
from time import sleep

servo = AngularServo(12, min_angle=-90, max_angle=90)
servo2 = AngularServo(25, min_angle=-90, max_angle=90)

while True:
    servo.angle = -90
    servo2.angle = -90
    sleep(2)
    servo.angle = 90
    servo2.angle = 90
    sleep(2)



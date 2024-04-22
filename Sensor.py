import RPi.GPIO as GPIO
import time
import cv2
import os
import numpy as np
import pytesseract
import glob
import shutil
import requests
import json
from fastapi import FastAPI
from gpiozero import AngularServo
from time import sleep

servo = AngularServo(25, min_angle=-90, max_angle=90)

GPIO.setmode(GPIO.BCM)
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
app = FastAPI()

TRIG1 = 23
ECHO1 = 24
TRIG2 = 21
ECHO2 = 20

GPIO.setup(TRIG1, GPIO.OUT)
GPIO.setup(ECHO1, GPIO.IN)
GPIO.setup(ECHO2, GPIO.IN)
GPIO.setup(TRIG2, GPIO.OUT)

GPIO.output(TRIG1, False)
print("Waiting For Sensor 1 To Settle")
time.sleep(2)
GPIO.output(TRIG2, False)
print("Waiting For Sensor 2 To Settle")
time.sleep(2)

registration_list = []

try:
    while True:

        # first sensor

        GPIO.output(TRIG1, True)
        time.sleep(0.1)
        GPIO.output(TRIG1, False)

        while GPIO.input(ECHO1) == 0:
            pulse_start = time.time()

        while GPIO.input(ECHO1) == 1:
            pulse_end = time.time()

        pulse_duration_first = pulse_end - pulse_start

        distance_first = pulse_duration_first * 17150
        distance_first_sensor = round(distance_first, 2)

        print("Distance sensor 1:", distance_first_sensor, "cm")

        # second sensor

        GPIO.output(TRIG2, True)
        time.sleep(0.1)
        GPIO.output(TRIG2, False)

        while GPIO.input(ECHO2) == 0:
            pulse_start = time.time()

        while GPIO.input(ECHO2) == 1:
            pulse_end = time.time()

        pulse_duration_second = pulse_end - pulse_start

        distance_second = pulse_duration_second * 17150
        distance_second_sensor = round(distance_second, 2)

        print("Distance sensor 2:", distance_second_sensor, "cm")

        # camera1

        if distance_first_sensor <= 8:
            save_dir = '/home/sgal/images/pics/'
            print("Distance is 8cm or less. Taking pictures...")


            def capture_images():
                print("Taking 10 pictures...")
                camera_1 = cv2.VideoCapture(0)
                time.sleep(2)

                os.makedirs(save_dir, exist_ok=True)

                for i in range(10):
                    ret, frame = camera_1.read()
                    if ret:
                        cv2.imwrite(os.path.join(save_dir, f'image_{i}.jpg'), frame)

                camera_1.release()

                return glob.glob(save_dir + '*.jpg')


            image_paths = capture_images()

            for image_path in image_paths:
                image = cv2.imread(image_path)
                success, image_jpg = cv2.imencode('.jpg', image)
                files = {'upload': image_jpg.tobytes()}

                # Delay for 1 second to avoid API throttling
                time.sleep(1)

                response = requests.post(
                    'https://api.platerecognizer.com/v1/plate-reader/',
                    headers={'Authorization': 'Token 397cefc199536f232215b12cc3a5651c5d8847f3'},
                    files=files
                )
                response_data = response.json()
                results = response_data.get('results', [])
                for result in results:
                    plate_number = result.get('plate')
                    print("License plate number:", plate_number)
                    registration_list.append(plate_number)

            print("reg list", registration_list)


            def most_common_registration(registration_list):
                return max(set(registration_list), key=registration_list.count)


            # Sending plate number to another endpoint
            response = requests.post(
                'http://172.16.1.38:8082/tickets',
                json={'registration': most_common_registration(registration_list)}
            )

        # ----------------------------------------------------------------------------------
        # camera2

        if distance_second_sensor <= 8:
            save_dir = '/home/sgal/images/pics/'
            print("Distance is 8cm or less. Taking pictures...")


            def capture_images():
                print("Taking 10 pictures...")
                camera_2 = cv2.VideoCapture(2)
                time.sleep(2)

                os.makedirs(save_dir, exist_ok=True)

                for i in range(10):
                    ret2, frame2 = camera_2.read()
                    if ret2:
                        cv2.imwrite(os.path.join(save_dir, f'image_{i}.jpg'), frame2)

                camera_2.release()

                return glob.glob(save_dir + '*.jpg')


            image_paths2 = capture_images()

            for image_path in image_paths2:
                image = cv2.imread(image_path)
                success, image_jpg = cv2.imencode('.jpg', image)
                files = {'upload': image_jpg.tobytes()}

                # Delay for 1 second to avoid API throttling
                time.sleep(1)

                response = requests.post(
                    'https://api.platerecognizer.com/v1/plate-reader/',
                    headers={'Authorization': 'Token 397cefc199536f232215b12cc3a5651c5d8847f3'},
                    files=files
                )
                response_data = response.json()
                results = response_data.get('results', [])
                for result in results:
                    plate_number = result.get('plate')
                    print("License plate number:", plate_number)
                    registration_list.append(plate_number)

            print("reg list", registration_list)


            def most_common_registration(registration_list):
                return max(set(registration_list), key=registration_list.count)


            most_common_reg = most_common_registration(registration_list)

            # Check if you can exit
            response2 = requests.get(
                f'http://172.16.1.38:8082/tickets/registration/{most_common_reg}/can-exit',
                json={'registration': most_common_registration(registration_list)}
            )
            response_data2 = response2.json()
            print("RD", response_data2)
            result2 = response_data2.get("canExit")
            print("result2", result2)
            if result2 != "False":
                servo.angle = 90
                sleep(2)

                response = requests.post(
                    f'http://172.16.1.38:8082/tickets/registration/{most_common_reg}/exit',
                    json={'canExit': '',
                          'timeOfExit': ''}
                )
        if distance_second_sensor >= 20:
            servo.angle = -90



except KeyboardInterrupt:
    print("Program terminated by user.")
    GPIO.cleanup()

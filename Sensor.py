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

GPIO.setmode(GPIO.BCM)
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
app = FastAPI()

TRIG = 23
ECHO = 24

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

GPIO.output(TRIG, False)
print("Waiting For Sensor To Settle")
time.sleep(2)

registration_list = []

try:
    while True:
        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)

        while GPIO.input(ECHO) == 0:
            pulse_start = time.time()

        while GPIO.input(ECHO) == 1:
            pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start

        distance = pulse_duration * 17150
        distance = round(distance, 2)

        print("Distance:", distance, "cm")

        if distance <= 8:
            save_dir = '/home/sgal/images/pics/'
            print("Distance is 8cm or less. Taking pictures...")


            def capture_images():
                print("Taking 10 pictures...")
                cap = cv2.VideoCapture(0)
                time.sleep(2)

                os.makedirs(save_dir, exist_ok=True)

                for i in range(10):
                    ret, frame = cap.read()
                    if ret:
                        cv2.imwrite(os.path.join(save_dir, f'image_{i}.jpg'), frame)

                cap.release()

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


            # Sending plate number
            response = requests.post(
                'http://172.16.1.38:8082/tickets',
                json={'registration': most_common_registration(registration_list)}
            )


except KeyboardInterrupt:
    print("Program terminated by user.")
    GPIO.cleanup()


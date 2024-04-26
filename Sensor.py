import RPi.GPIO as GPIO
import time
import cv2
import os
import glob
import requests
from gpiozero import AngularServo
from time import sleep
import json

servo1 = AngularServo(12, min_angle=-90, max_angle=90)
servo2 = AngularServo(25, min_angle=-90, max_angle=90)
GPIO.setmode(GPIO.BCM)
TRIG1, ECHO1, TRIG2, ECHO2 = 23, 24, 21, 20
GPIO.setup([TRIG1, TRIG2], GPIO.OUT)
GPIO.setup([ECHO1, ECHO2], GPIO.IN)

GPIO.output(TRIG1, False)
print("Waiting For Sensor 1 To Settle")
time.sleep(2)
GPIO.output(TRIG2, False)
print("Waiting For Sensor 2 To Settle")
time.sleep(2)

registration_list = []


def get_distance(TRIG, ECHO):
    GPIO.output(TRIG, True)
    time.sleep(0.1)
    GPIO.output(TRIG, False)
    pulse_start, pulse_end = 0, 0

    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    return round(pulse_duration * 17150, 2)


def capture_images(camera):
    print("Taking 10 pictures...")
    save_dir = '/home/sgal/images/pics/'
    os.makedirs(save_dir, exist_ok=True)

    for i in range(10):
        ret, frame = camera.read()
        if ret:
            cv2.imwrite(os.path.join(save_dir, f'image_{i}.jpg'), frame)
    return glob.glob(save_dir + '*.jpg')


def process_image(image_paths):
    for image_path in image_paths:
        image = cv2.imread(image_path)
        success, image_jpg = cv2.imencode('.jpg', image)
        files = {'upload': image_jpg.tobytes()}
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


def main_process(distance_sensor, camera):
    image_paths = capture_images(camera)
    process_image(image_paths)


try:
    while True:
        # First sensor
        distance_first_sensor = get_distance(TRIG1, ECHO1)
        print("Distance sensor 1:", distance_first_sensor, "cm")

        # Second sensor
        distance_second_sensor = get_distance(TRIG2, ECHO2)
        print("Distance sensor 2:", distance_second_sensor, "cm")

        # Camera 1
        if distance_first_sensor <= 8:
            main_process(distance_first_sensor, cv2.VideoCapture(0))
            print("Registration list:", registration_list)

            most_common_reg = max(set(registration_list), key=registration_list.count)

            response_get = requests.get(
                f'http://172.16.1.38:8082/tickets/registration/{most_common_reg}'
            )
            if (response_get.status_code != 200):
                print("Registration not found. Proceeding to create new ticket.")

                # Create new ticket
                response_create = requests.post(
                    'http://172.16.1.38:8082/tickets',
                    json={'registration': most_common_reg}
                )
                print("Created new ticket:", response_create.status_code)
                servo1.angle = 90
                sleep(2)

            else:
                ticket_data = response_get.json()
                ticket_id = ticket_data.get('ticketId')
                print("Found ticket ID:", ticket_id)

                # Delete transaction

                response_transactions = requests.get(
                    f'http://172.16.1.38:8082/transactions'
                )

                transactions = response_transactions.json()
                for transaction in transactions:
                    if transaction['ticket']['ticketId'] == ticket_id:
                        transaction_id = transaction['transactionId']
                        response_delete_transaction = requests.delete(
                            f'http://172.16.1.38:8082/transactions/{transaction_id}'
                        )
                        print("Deleted transaction:", response_delete_transaction.status_code)

                # Delete old ticket if registration exists
                response_delete = requests.delete(
                    f'http://172.16.1.38:8082/tickets/{ticket_id}'
                )
                print("Deleted old ticket:", response_delete.status_code)

                response_create = requests.post(
                    'http://172.16.1.38:8082/tickets',
                    json={'registration': most_common_reg}
                )
                print("Created new ticket:", response_create.status_code)
                servo1.angle = 90
                sleep(2)

        if distance_first_sensor >= 20:
            servo1.angle = -90

        # Camera 2
        if distance_second_sensor <= 8:
            main_process(distance_second_sensor, cv2.VideoCapture(2))
            print("Registration list:", registration_list)

            most_common_reg = max(set(registration_list), key=registration_list.count)

            # Check if you can exit
            response2 = requests.get(
                f'http://172.16.1.38:8082/tickets/registration/{most_common_reg}/can-exit',
                json={'registration': most_common_reg}
            )
            response_data2 = response2.json()
            result2 = response_data2.get("canExit")
            print("Result 2:", result2)
            if result2 == True:
                servo2.angle = 90
                sleep(2)

                response = requests.post(
                    f'http://172.16.1.38:8082/tickets/registration/{most_common_reg}/exit',
                    json={'canExit': '', 'timeOfExit': ''}
                )
        if distance_second_sensor >= 20:
            servo2.angle = -90


except KeyboardInterrupt:
    print("Program terminated by user.")
    GPIO.cleanup()

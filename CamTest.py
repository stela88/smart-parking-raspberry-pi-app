import cv2
import os
import time
import pytesseract
import numpy as np
import glob
import shutil
import requests
import json
from fastapi import FastAPI

pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
app = FastAPI()

save_dir = '/home/sgal/images/pics/'
def capture_images():
    print("Taking 10 pictures...")
    cap = cv2.VideoCapture(0)
    time.sleep(2)


    os.makedirs(save_dir, exist_ok=True)

    # Capture 10 images
    for i in range(10):
        ret, frame = cap.read()
        if ret:
            cv2.imwrite(os.path.join(save_dir, f'image_{i}.jpg'), frame)

    cap.release()

    # Return the list of image paths
    return glob.glob(save_dir + '*.jpg')

# Get a list of image paths
image_paths = glob.glob(save_dir + '*.jpg')

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


    @app.get("/")
    def read_root():
        return {plate_number}

#senzor
metersToTheCamera = [5, 5, 5, 4, 3, 2, 2, 1, 1, 0.5]
prev_element = None
count = 1

for meters in metersToTheCamera:
    if 0.5 <= meters <= 1.5:
        count += 1
        if count == 3:
            capture_images()
            break
    else:
        count = 0


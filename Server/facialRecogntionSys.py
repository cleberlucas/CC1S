import cv2
import pickle
import json
import requests
from pyzbar.pyzbar import decode
import time
import base64
import numpy as np

face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

with open('config.json') as f:
    config = json.load(f)

video_url = ""
facialDataAccessLayerURL =  "http://127.0.0.1:5000/"

esp_32_url_info = "http://"
response = requests.get(facialDataAccessLayerURL + "esp/url/32")
if response.status_code == 200:
    esp_32_url_info = esp_32_url_info + response.json()['url']
    print("esp-32-url: " + esp_32_url_info)
    video_url = esp_32_url_info + ":81/stream"
else:
    print("error-esp-32-url: ", response.json()['message'])
    exit()

esp_8266_url_info = "http://"
response = requests.get(facialDataAccessLayerURL + "esp/url/8266")
if response.status_code == 200:
    esp_8266_url_info = esp_8266_url_info + response.json()['url']
    print("esp-8266-url: " + esp_8266_url_info)
else:
    print("error-esp-8266-url: ", response.json()['message'])
    exit()


def main():
    global automatic_registration 
    global esp_last_state_leds
    global esp_last_state_face_detection
    global esp_last_state_face_recognized
    global esp_last_state_door

    automatic_registration = True
    esp_last_state_leds = False
    esp_last_state_face_detection = False
    esp_last_state_face_recognized = False
    esp_last_state_door = False

    if video_url:
        print ("video-url: "+video_url)
        video_capture = cv2.VideoCapture(video_url)
    else:
        print("ESP32-CAM camera URL not found in the configuration file.")
        exit()

    while True:
        time.sleep(0.1)

        ret, frame = video_capture.read()
        if ret:
            qr(frame)
            faces(frame)


def qr(frame):
    decoded_objects = decode(frame)
    for obj in decoded_objects:
        if obj.type == 'QRCODE':
            recognized = False
            qr_data = obj.data.decode('utf-8')
            print("qr-data: ", qr_data)
            try:
                qr_object = json.loads(qr_data)
                send_request_to_server("/qr/recognized")
                print("qr-recognized", qr_object)
                recognized = True
            except json.JSONDecodeError:
                print("error-qr-decoding")
            if not recognized: 
                send_request_to_server("/qr/unrecognized")
                print("qr-unrecognized", qr_object)

def faces(frame):
    global automatic_registration

    global esp_last_state_face_recognized
    global esp_last_state_face_detection
    global esp_last_state_door
    global esp_last_state_leds

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_classifier.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces) == 0:
        print('face-undetected')
        if esp_last_state_face_detection:
            send_request_to_server("/face/undetected")
            esp_last_state_face_detection = False

    registered = False
    esp_last_state_door = False
    for (x, y, w, h) in faces:
        print('face-detected')
        if not esp_last_state_face_detection:
            send_request_to_server("/face/detected")

            esp_last_state_face_detection = True
            
        current_face = gray_frame[y:y+h, x:x+w]

        try:
            response = requests.get(facialDataAccessLayerURL + "faces")
            if response.status_code == 200:
                face_data = response.json().get('faces', [])
                for face in face_data:
                    name = face.get('name')
                    user_id = face.get('user_id')
                    face_img = face.get('face_img')
                    if face_img is not None:
                        registered_face = np.array(face_img, dtype=np.uint8)
                        res = cv2.matchTemplate(current_face, registered_face, cv2.TM_CCOEFF_NORMED)
                        _, max_val, _, _ = cv2.minMaxLoc(res)
                        if max_val > 0.7:
                            registered = True
                            print('face-recognized: ' + name)
                            if not esp_last_state_face_recognized and not esp_last_state_door:
                                send_request_to_server("/face/recognized")             
                                send_request_to_server("/door/open")
                                time.sleep(5)
                                send_request_to_server("/leds/off")
                                main()

                if not registered and automatic_registration:
                    register_face(1,frame, x, y, w, h)
                    registered = True
                    print('face-registered')
                else:
                    if esp_last_state_face_recognized:
                        send_request_to_server("/face/unrecognized")
                        esp_last_state_face_recognized = False
                        esp_last_state_leds = True
                    print('face-unrecognized')
        except Exception as e:
            print("An error occurred:", str(e))

            

def register_face(id, frame, x, y, w, h):
    try:
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        registered_face = gray_frame[y:y+h, x:x+w]
        serialized_face = pickle.dumps(registered_face)

        serialized_face_base64 = base64.b64encode(serialized_face).decode('utf-8')

        data = {
            'id': id,
            'serialized_face': serialized_face_base64
        }

        response = requests.post(facialDataAccessLayerURL + "register-face", json=data)

        if response.status_code == 200:
            print("Face registered successfully")
        else:
            print("Failed to register face:", response.json())

    except Exception as e:
        print("An error occurred:", str(e))


def send_request_to_server(route):
    url = esp_8266_url_info + route
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("Request sent successfully to:", route)
        else:
            print("Error sending request to:", route, response.status_code)
    except requests.RequestException as e:
        print("Error sending request to:", route, e)

if __name__ == "__main__":
    main()

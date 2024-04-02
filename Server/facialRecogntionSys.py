import cv2
import pickle
import requests
from pyzbar.pyzbar import decode
import time
import base64
import numpy as np
import threading

face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

local = None
video_url = ""
facialDataAccessLayerURL =  "http://127.0.0.1:5000/"

esp_32_url_info = "http://"
esp_32_id_info=int(input("set ESP32 to init:<id> "))
response = requests.get(facialDataAccessLayerURL + f"esp?id={esp_32_id_info}")
if response.status_code == 200:
    esp_32_url_info = esp_32_url_info + response.json()['url']
    video_url = esp_32_url_info + ":81/stream"
    local = response.json()['local']

    print("esp-32-url: " + esp_32_url_info)
    if not local: 
        print("local: " + str(local))
else:
    print("Failed to get ESP32 url:  ", response.json()['message'])
    exit()

esp_8266_url_info = "http://"
esp8266_id_info=int(input("set ESP8266 to init:<id> "))
response = requests.get(facialDataAccessLayerURL + f"esp?id={esp8266_id_info}")
if response.status_code == 200:
    esp_8266_url_info = esp_8266_url_info + response.json()['url']
    
    print("esp-8266-url: " + esp_8266_url_info)
    if not local: 
        local = response.json()['local']
        print("local: " + str(local))

else:
    print("Failed to get ESP8266 url: ", response.json()['message'])
    exit()

def faceDetection():
    global esp_last_state_face_detection
    global esp_last_state_face_unrecognized
    global esp_last_state_door

    esp_last_state_face_detection = False
    esp_last_state_face_unrecognized = False
    esp_last_state_door = False

    if video_url:
        print ("video-url: "+ video_url)
        
    else:
        print("ESP32-CAM camera URL not found in the configuration file.")
        exit()
    
    send_request_to_server("/leds/off")

    while True:
        time.sleep(0.01)
        video_capture = cv2.VideoCapture(video_url)
        ret, frame = video_capture.read()
        if ret:
            if face(frame):
                send_request_to_server("/leds/off")          
                send_request_to_server("/led/blue/on")
                time.sleep(5)
        video_capture.release()

def face(frame):
    global local
    global esp_last_state_face_unrecognized
    global esp_last_state_face_detection

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_classifier.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces) == 0:
        print('face-undetected')
        if esp_last_state_face_detection:
            send_request_to_server("/led/yellow/off")
            esp_last_state_face_detection = False

    for (x, y, w, h) in faces:
        registered = False

        print('face-detected')

        if not esp_last_state_face_detection:
            send_request_to_server("/led/yellow/on")
            esp_last_state_face_detection = True
            
        current_face = gray_frame[y:y+h, x:x+w]

        try:
            response = requests.get(facialDataAccessLayerURL + f"faces?local={local}")
            if response.status_code == 200:
                face_data = response.json().get('faces', [])
                for face in face_data:
                    name = face.get('name')
                    face_img = face.get('face_img')
                    if face_img is not None:
                        registered_face = np.array(face_img, dtype=np.uint8)
                        res = cv2.matchTemplate(current_face, registered_face, cv2.TM_CCOEFF_NORMED)
                        _, max_val, _, _ = cv2.minMaxLoc(res)
                        if max_val > 0.7:           
                            if registration_mode:
                                esp_last_state_face_unrecognized = False
                                register_face(current_user_id,frame, x, y, w, h)

                                print('face-registered')

                                send_request_to_server("/led/green/on")
                                #time.sleep(0.5)
                                send_request_to_server("/led/green/off")

                                registered = True
                                break
                            else:
                                print('face-recognized: ' + name)
                                send_request_to_server("/led/green/on")
                                return True

            if not esp_last_state_face_unrecognized:
                send_request_to_server("/led/red/on")
                esp_last_state_face_unrecognized = True
                print('face-unrecognized')

            current_user_id = 1 #check after
            if registration_mode and not registered:
                esp_last_state_face_unrecognized = False
                register_face(current_user_id,frame, x, y, w, h)

                print('face-registered')

                send_request_to_server("/led/green/on")
                #time.sleep(0.5)
                send_request_to_server("/led/green/off")

        except Exception as e:
            print("An error occurred:", str(e))
    return False

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

def get_esp_register_mode(esp_id):
    try:
        response = requests.get(f"{facialDataAccessLayerURL}esp/register-mode?id={esp_id}")
        if response.status_code == 200:
            data = response.json()
            register_mode = data.get('register_mode')
            return register_mode
        else:
            print(f"Failed to check esp register mode. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

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


def check_user_exists(user_id):
    try:
        response = requests.get(f"{facialDataAccessLayerURL}user/exists?id={user_id}")
        if response.status_code == 200:
            data = response.json()
            exists = data.get('exists')
            return exists
        else:
            print(f"Failed to check user existence. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
def syncData():
    global registration_mode 
    registration_mode = get_esp_register_mode(8266)
    
def run_syncData_repeatedly():
    timeout = 5
    while True:
        try:
            syncData()
        except Exception as e:
            print("An error occurred:", str(e))
            timeout += 1
        time.sleep(timeout)

def run_faceDetection_repeatedly():
    timeout = 5
    while True:
        try:
            faceDetection()
        except Exception as e:
            print("An error occurred:", str(e))
            timeout += 1
        time.sleep(timeout)
  
def main():
    syncData()

    sync_thread = threading.Thread(target=run_syncData_repeatedly)
    sync_thread.daemon = True
    sync_thread.start()

    face_thread = threading.Thread(target=run_faceDetection_repeatedly)
    face_thread.daemon = True
    face_thread.start()

    while True:
        pass

if __name__ == "__main__":
    main()
    


import cv2
import pickle
import json
import requests
from pyzbar.pyzbar import decode
import time
import base64
import numpy as np
import threading

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



def faceDetection():
    global esp_last_state_face_detection
    global esp_last_state_face_unrecognized
    global esp_last_state_qr_detection
    global esp_last_state_qr_recognized
    global esp_last_state_door
    global current_user_id
    global video_capture

    esp_last_state_face_detection = False
    esp_last_state_face_unrecognized = False
    esp_last_state_qr_recognized = False
    esp_last_state_qr_detection = False
    esp_last_state_door = False
    current_user_id = 0
    video_capture = None

    if video_url:
        print ("video-url: "+video_url)
        
    else:
        print("ESP32-CAM camera URL not found in the configuration file.")
        exit()
    
    send_request_to_server("/leds/off")

    while True:
        time.sleep(0.01)
        video_capture = cv2.VideoCapture(video_url)
        ret, frame = video_capture.read()
        if ret:
            qr(frame)
            if current_user_id != 0:    
                if face(frame):
                    send_request_to_server("/leds/off")          
                    send_request_to_server("/door/open")
                    time.sleep(5)
                    faceDetection()
        video_capture.release()

def qr(frame):
    global esp_last_state_qr_recognized
    global esp_last_state_qr_detection
    global current_user_id
    user_id = 0

    detected = False
    decoded_objects = decode(frame)
    for obj in decoded_objects:
        detected = True
        if obj.type == 'QRCODE':

            qr_data = obj.data.decode('utf-8')

            print('qr-detected')
            if not esp_last_state_qr_detection:
                send_request_to_server("/qr/detected")
                esp_last_state_qr_detection = True
           
            try:
                qr_object = json.loads(qr_data)
                user_id = int(qr_object.get("id"))

                if user_id is not None and check_user_exists(user_id):
                    print('qr-recognized: ' + str(user_id))
                    
                    if current_user_id != user_id and not esp_last_state_qr_recognized:               
                        send_request_to_server("/qr/recognized")
                        time.sleep(5)
                        esp_last_state_qr_recognized = True
                        send_request_to_server("/leds/off")
                        send_request_to_server("/qr/detected")

                    current_user_id = user_id    
                else:
                    send_request_to_server("/qr/unrecognized")
                    current_user_id = 0
                
                
            except json.JSONDecodeError:
                print("error-qr-decoding")

            if current_user_id != user_id and esp_last_state_qr_recognized:
                print("qr-unrecognized")
                send_request_to_server("/qr/unrecognized")
                esp_last_state_qr_recognized = False
                
    if current_user_id == 0 and not detected:
        print('qr-undetected')        
        if esp_last_state_qr_detection:
            send_request_to_server("/qr/undetected")
            esp_last_state_qr_detection = False


def face(frame):
    global video_capture
    global current_user_id
    global automatic_registration

    global esp_last_state_face_unrecognized
    global esp_last_state_face_detection
    global esp_last_state_door

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_classifier.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces) == 0:
        print('face-undetected')
        if esp_last_state_face_detection:
            send_request_to_server("/face/undetected")
            esp_last_state_face_detection = False

    esp_last_state_door = False
    for (x, y, w, h) in faces:
        print('face-detected')
        if not esp_last_state_face_detection:
            send_request_to_server("/face/detected")
            esp_last_state_face_detection = True
            
        current_face = gray_frame[y:y+h, x:x+w]

        if current_user_id == 0 : return False

        if automatic_registration:
            register_face(current_user_id,frame, x, y, w, h)
            print('face-registered')
            frame = video_capture.read()

        try:
            response = requests.get(facialDataAccessLayerURL + f"faces?id={current_user_id}")
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
                            print('face-recognized: ' + name)
                            send_request_to_server("/face/recognized")
                            return not automatic_registration

            if not esp_last_state_face_unrecognized:
                send_request_to_server("/face/unrecognized")
                esp_last_state_face_unrecognized = True
                print('face-unrecognized')
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
    global automatic_registration 
    automatic_registration = get_esp_register_mode(8266)
    
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
    


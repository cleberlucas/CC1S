import cv2
import tkinter as tk
from PIL import Image, ImageTk
import mysql.connector
import pickle
import json
import cv2
from pyzbar.pyzbar import decode

automatic_registration = False

face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

current_frame = None

with open('config.json') as f:
    config = json.load(f)

esp32cam_config = config.pop("esp32cam", {})
video_url = esp32cam_config.get("url")
if video_url:
    video_capture = cv2.VideoCapture(video_url)
else:
    print("ESP32-CAM camera URL not found in the configuration file.")
    exit()

db_config = config.get("db", {})
db_connection = mysql.connector.connect(
    host=db_config.get("host", "localhost"),
    user=db_config.get("user", "root"),
    password=db_config.get("password", ""),
    database=db_config.get("database", "")
)
cursor = db_connection.cursor()

def update_camera():
    global current_frame
    ret, frame = video_capture.read()
    if ret:
        frame = cv2.flip(frame, 1)
        current_frame = frame

        read_qr_code(frame)
        detect_and_draw_faces(frame)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = Image.fromarray(frame)

        #frame = frame.resize((320, 240), Image.ANTIALIAS)

        #photo = ImageTk.PhotoImage(image=frame)
        #camera_label.config(image=photo)
        #camera_label.image = photo

    window.after(1, update_camera)

def read_qr_code(frame):
    decoded_objects = decode(frame)
    for obj in decoded_objects:
        if obj.type == 'QRCODE':
            qr_data = obj.data.decode('utf-8')
            print("QR Code Data:", qr_data)
            try:
                qr_object = json.loads(qr_data)
                print("JSON Object:", qr_object)
            except json.JSONDecodeError:
                print("Error decoding JSON")

def detect_and_draw_faces(frame):
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_classifier.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    for (x, y, w, h) in faces:
        current_face = gray_frame[y:y+h, x:x+w]

        registered = False

        cursor.execute("SELECT `name`, face_img FROM facial_recognition f INNER JOIN users u ON f.user_rgm = u.rgm")
        records = cursor.fetchall()

        for name, serialized_face in records:
            registered_face = pickle.loads(serialized_face)
            res = cv2.matchTemplate(current_face, registered_face, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(res)

            if max_val > 0.7:
                registered = True
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, str(name), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                print(name)   
                break
               
        if  not registered and automatic_registration:  
            register_face(frame, x, y, w, h)
            registered = True
            print('Registered')   
        else:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(frame, "Unknown", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            print('Unknown')

def register_face(frame, x, y, w, h):
    user_rgm = rgm_entry.get() if rgm_entry.get() else "123456"
    name = name_entry.get() if name_entry.get() else "Cleber-Automatic"

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    registered_face = gray_frame[y:y+h, x:x+w]
    serialized_face = pickle.dumps(registered_face)    

    cursor.execute("REPLACE INTO users (rgm,name) VALUES (%s, %s)", (user_rgm, name,))
    cursor.execute("INSERT INTO facial_recognition (user_rgm, face_img) VALUES (%s, %s)", (user_rgm, serialized_face))
    db_connection.commit()

    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.putText(frame, "Registered", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    print('Registered')            
           

def register_face_manually():
    ret, frame = video_capture.read()
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_classifier.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    user_rgm = rgm_entry.get()
    name = name_entry.get()

    if user_rgm.isnumeric():
        if user_rgm and len(faces) > 0:
            for (x, y, w, h) in faces:
                registered_face = gray_frame[y:y+h, x:x+w]
                serialized_face = pickle.dumps(registered_face)    
                cursor.execute("REPLACE INTO users (rgm,name) VALUES (%s, %s)", (user_rgm, name,))
                cursor.execute("INSERT INTO facial_recognition (user_rgm, face_img) VALUES (%s, %s)", (user_rgm, serialized_face))
                db_connection.commit()

            cursor.fetchall()
            
            cursor.execute("SELECT count(*) total FROM facial_recognition f INNER JOIN users u ON f.user_rgm = u.rgm")
            total = cursor.fetchone()[0]
            result_label.config(text=f"Face registered for user: {user_rgm} photos: {total}")
        elif not user_rgm:
            result_label.config(text="Please enter the user RGM")
        else:
            result_label.config(text="No face detected for registration")
    else:
        result_label.config(text="Please enter a valid RGM!")

def toggle_automatic_registration():
    global automatic_registration  # Define automatic_registration as global
    automatic_registration = not automatic_registration

window = tk.Tk()
window.title("Face Recognition")
'''

camera_label = tk.Label(window)
camera_label.pack()

'''

id_label = tk.Label(window, text="Enter your RGM:")
id_label.pack()

rgm_entry = tk.Entry(window)
rgm_entry.pack()

name_label = tk.Label(window, text="Enter your name:")
name_label.pack()

name_entry = tk.Entry(window)
name_entry.pack()

register_button = tk.Button(window, text="Register Face", command=register_face_manually)
register_button.pack()

register_auto_button = tk.Button(window, text="Automatic Registration", command=toggle_automatic_registration)
register_auto_button.pack()

result_label = tk.Label(window, text="")
result_label.pack()

update_camera()

window.mainloop()

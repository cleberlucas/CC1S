import cv2
import tkinter as tk
from PIL import Image, ImageTk
import mysql.connector
import serial
import pickle
import json
import requests
import time;

#arduino = serial.Serial('COM4', 9600)
video_capture = cv2.VideoCapture(0)



classificador_rosto = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

frame_atual = None

with open('config.json') as f:
    config = json.load(f)

conexao_bd = mysql.connector.connect(**config)
cursor = conexao_bd.cursor()
video_url = "http://192.168.15.100:81/stream" 
cap = cv2.VideoCapture(video_url)

def atualizar_camera():
    global frame_atual
    ret, frame = cap.read()
    if ret:
        frame = cv2.flip(frame, 1)
        frame_atual = frame

        detectar_e_desenhar_rostos(frame)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = Image.fromarray(frame)
        photo = ImageTk.PhotoImage(image=frame)
        camera_label.config(image=photo)
        camera_label.image = photo

    janela.after(10, atualizar_camera)

def detectar_e_desenhar_rostos(frame):
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rostos = classificador_rosto.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    for (x, y, w, h) in rostos:
        rosto_atual = gray_frame[y:y+h, x:x+w]

        cadastrado = False

        cursor.execute("SELECT `name`, face_img FROM facial_recognition f INNER JOIN users u ON f.user_rgm = u.rgm")
        registros = cursor.fetchall()

        for name, rosto_serializado in registros:
            rosto_cadastrado = pickle.loads(rosto_serializado)
            res = cv2.matchTemplate(rosto_atual, rosto_cadastrado, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(res)

            if max_val > 0.7:
                cadastrado = True
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, str(name), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                break

        if not cadastrado:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(frame, "Desconhecido", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            #arduino.write(b'1')
            print('Desconhecido')

        time.sleep(1000)

def cadastrar_rosto():
    ret, frame = video_capture.read()
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rostos = classificador_rosto.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    user_rgm = rgm_entry.get()
    name = name_entry.get()

    if user_rgm.isnumeric() :
        if user_rgm and len(rostos) > 0:
            for (x, y, w, h) in rostos:
                rosto_cadastrado = gray_frame[y:y+h, x:x+w]
                rosto_serializado = pickle.dumps(rosto_cadastrado)    
                cursor.execute("REPLACE INTO users (rgm,name) VALUES (%s, %s)", (user_rgm,name,))
                cursor.execute("INSERT INTO facial_recognition (user_rgm, face_img) VALUES (%s, %s)", (user_rgm, rosto_serializado))
                conexao_bd.commit()
                
            resultado_label.config(text=f"Rosto cadastrado para o usuário: {user_rgm} fotos:{len(rostos)}")
        elif not user_rgm:
            resultado_label.config(text="Por favor, insira o RGM do usuário")
        else:
            resultado_label.config(text="Nenhum rosto detectado para cadastro")
    else:
        resultado_label.config(text="Por favor, digite um RGM válido!")

janela = tk.Tk()
janela.title("Verificação de Rosto")

camera_label = tk.Label(janela)
camera_label.pack()

id_label = tk.Label(janela, text="Dígite seu rgm:")
id_label.pack()

rgm_entry = tk.Entry(janela)
rgm_entry.pack()

name_label = tk.Label(janela, text="Dígite seu nome:")
name_label.pack()

name_entry = tk.Entry(janela)
name_entry.pack()

cadastrar_botao = tk.Button(janela, text="Cadastrar Rosto", command=cadastrar_rosto)
cadastrar_botao.pack()

resultado_label = tk.Label(janela, text="")
resultado_label.pack()

atualizar_camera()

janela.mainloop()

import cv2
import tkinter as tk
from PIL import Image, ImageTk
import mysql.connector
import serial
import pickle
import json

import time
import threading

arduino_id = 123
#arduino = serial.Serial('COM4', 9600)
#video_capture = cv2.VideoCapture(0)
video_url = "http://192.168.15.100:81/stream" 
video_capture = cv2.VideoCapture(video_url)

classificador_rosto = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

frame_atual = None

with open('config.json') as f:
    config = json.load(f)

conexao_bd = mysql.connector.connect(**config)
cursor = conexao_bd.cursor()

def atualizar_camera():
    global frame_atual
    ret, frame = video_capture.read()
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

        global cadastrado

        cadastrado = False
        
        cursor.execute("SELECT `name` user_id, face_img FROM facial_recognition f INNER JOIN users u ON f.user_rgm = u.rgm")
        registros = cursor.fetchall()

        for user_id, rosto_serializado in registros:
            rosto_cadastrado = pickle.loads(rosto_serializado)
            res = cv2.matchTemplate(rosto_atual, rosto_cadastrado, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(res)

            if max_val > 0.7:
                cadastrado = True
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, str(user_id), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                break

        if not cadastrado:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(frame, "Desconhecido", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            #arduino.write(b'1')
            print('Desconhecido')

def destravar():
    if cadastrado:
        resultado_label.config(text="Bem vindo!!")
        cursor.execute("REPLACE INTO arduino (id, `unlock`) VALUES (%s, TRUE)", (arduino_id,))
        conexao_bd.commit()
        threading.Thread(target=reset_unlock).start()
    else:
        resultado_label.config(text="Você não está cadastrado no sistema")

def travar():
    cursor.execute("REPLACE INTO arduino (id, `unlock`) VALUES (%s, FALSE)", (arduino_id,))
    conexao_bd.commit()

def reset_unlock():
    with mysql.connector.connect(**config) as conexao_bd_temp:
        with conexao_bd_temp.cursor() as temp_cursor:
            time.sleep(2)
            temp_cursor.execute("REPLACE INTO arduino (id, `unlock`) VALUES (%s, FALSE)", (arduino_id,))
            conexao_bd_temp.commit()

janela = tk.Tk()
janela.title("Verificação de Rosto")

camera_label = tk.Label(janela)
camera_label.pack()

cadastrar_botao = tk.Button(janela, text="Destravar", command=destravar)
cadastrar_botao.pack()

cadastrar_botao = tk.Button(janela, text="Travar", command=travar)
cadastrar_botao.pack()

resultado_label = tk.Label(janela, text="")
resultado_label.pack()

atualizar_camera()

janela.mainloop()

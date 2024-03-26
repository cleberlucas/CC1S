import cv2
import tkinter as tk
from PIL import Image, ImageTk
import mysql.connector
import serial
import pickle
import json

arduino = serial.Serial('COM4', 9600)
video_capture = cv2.VideoCapture(0)

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

    cursor.execute("SELECT nome, rosto FROM rostos")
    registros = cursor.fetchall()

    for (x, y, w, h) in rostos:
        rosto_atual = gray_frame[y:y+h, x:x+w]

        cadastrado = False

        for nome, rosto_serializado in registros:
            rosto_cadastrado = pickle.loads(rosto_serializado)
            res = cv2.matchTemplate(rosto_atual, rosto_cadastrado, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(res)

            if max_val > 0.7:
                cadastrado = True
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, nome, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                break
        if not cadastrado:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(frame, "Desconhecido", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            arduino.write(b'1')
            print('Desconhecido')

def cadastrar_rosto():
    ret, frame = video_capture.read()
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rostos = classificador_rosto.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    nome = nome_entry.get()

    if nome and len(rostos) > 0:
        for (x, y, w, h) in rostos:
            rosto_cadastrado = gray_frame[y:y+h, x:x+w]
            
            # Serializar o array numpy em bytes
            rosto_serializado = pickle.dumps(rosto_cadastrado)
            
            # Inserir os dados no banco de dados MySQL
            cursor.execute("INSERT INTO rostos (nome, rosto) VALUES (%s, %s)", (nome, rosto_serializado))
            conexao_bd.commit()
            
        resultado_label.config(text=f"Rosto cadastrado: {nome} fotos:{len(rostos)}")
    elif not nome:
        resultado_label.config(text="Por favor, insira o nome da pessoa")
    else:
        resultado_label.config(text="Nenhum rosto detectado para cadastro")

janela = tk.Tk()
janela.title("Verificação de Rosto")

camera_label = tk.Label(janela)
camera_label.pack()

nome_label = tk.Label(janela, text="Nome:")
nome_label.pack()

nome_entry = tk.Entry(janela)
nome_entry.pack()

cadastrar_botao = tk.Button(janela, text="Cadastrar Rosto", command=cadastrar_rosto)
cadastrar_botao.pack()

resultado_label = tk.Label(janela, text="")
resultado_label.pack()

atualizar_camera()

janela.mainloop()

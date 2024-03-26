import cv2
import tkinter as tk
from PIL import Image, ImageTk
import serial

arduino = serial.Serial('COM4', 9600)
video_capture = cv2.VideoCapture(0)

classificador_rosto = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

frame_atual = None

rostos_cadastrados = {}

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
    global rostos_cadastrados
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rostos = classificador_rosto.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    for (x, y, w, h) in rostos:
        rosto_atual = gray_frame[y:y+h, x:x+w]

        cadastrado = False

        for nome, lista_rostos in rostos_cadastrados.items():
            for rosto_cadastrado in lista_rostos:
                res = cv2.matchTemplate(rosto_atual, rosto_cadastrado, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, _ = cv2.minMaxLoc(res)

                if max_val > 0.7:  # Ajustando o threshold de similaridade
                    cadastrado = True
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame, nome, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    break
            if cadastrado:
                break

        if not cadastrado:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(frame, "Desconhecido", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            arduino.write(b'1')
            print('Desconhecido')

def cadastrar_rosto():
    global rostos_cadastrados
    ret, frame = video_capture.read()
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rostos = classificador_rosto.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    nome = nome_entry.get()

    if nome and len(rostos) > 0:
        if nome not in rostos_cadastrados:
            rostos_cadastrados[nome] = []

        for (x, y, w, h) in rostos:
            rosto_cadastrado = gray_frame[y:y+h, x:x+w]
            rostos_cadastrados[nome].append(rosto_cadastrado)
            resultado_label.config(text=f"Rosto cadastrado: {nome} fotos:{len(rostos_cadastrados[nome])}")
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

import cv2
import tkinter as tk
from PIL import Image, ImageTk
import mysql.connector
import pickle
import json
import cv2
from pyzbar.pyzbar import decode

#arduino = serial.Serial('COM4', 9600)
video_capture = cv2.VideoCapture(0)

cadastro_automatico = False

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

        ler_qr_code(frame)
        detectar_e_desenhar_rostos(frame)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = Image.fromarray(frame)

        #frame = frame.resize((320, 240), Image.ANTIALIAS)

        photo = ImageTk.PhotoImage(image=frame)
        camera_label.config(image=photo)
        camera_label.image = photo

    janela.after(10, atualizar_camera)

def ler_qr_code(frame):
    decoded_objects = decode(frame)
    for obj in decoded_objects:
        if obj.type == 'QRCODE':
            qr_data = obj.data.decode('utf-8')
            print("QR Code Data:", qr_data)
            try:
                qr_objeto = json.loads(qr_data)
                print("JSON Object:", qr_objeto)
                # Faça o que você precisa com o objeto JSON aqui
            except json.JSONDecodeError:
                print("Erro ao decodificar JSON")

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
               
        if cadastro_automatico:  
            cadastrar_rosto_parameter(frame,x, y, w, h)
            cadastrado = True        
        elif not cadastrado:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(frame, "Desconhecido", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            print('Desconhecido')

def cadastrar_rosto_parameter(frame,x, y, w, h):
    user_rgm = rgm_entry.get() if rgm_entry.get() else "123456"
    name = name_entry.get() if name_entry.get() else "Cleber-Automatica"

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rosto_cadastrado = gray_frame[y:y+h, x:x+w]
    rosto_serializado = pickle.dumps(rosto_cadastrado)    

    cursor.execute("REPLACE INTO users (rgm,name) VALUES (%s, %s)", (user_rgm, name,))
    cursor.execute("INSERT INTO facial_recognition (user_rgm, face_img) VALUES (%s, %s)", (user_rgm, rosto_serializado))
    conexao_bd.commit()

    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.putText(frame, "Cadastrado", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    print('Cadastrado')            
           

def cadastrar_rosto():
    ret, frame = video_capture.read()
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rostos = classificador_rosto.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    user_rgm = rgm_entry.get()
    name = name_entry.get()

    if user_rgm.isnumeric():
        if user_rgm and len(rostos) > 0:
            for (x, y, w, h) in rostos:
                rosto_cadastrado = gray_frame[y:y+h, x:x+w]
                rosto_serializado = pickle.dumps(rosto_cadastrado)    
                cursor.execute("REPLACE INTO users (rgm,name) VALUES (%s, %s)", (user_rgm, name,))
                cursor.execute("INSERT INTO facial_recognition (user_rgm, face_img) VALUES (%s, %s)", (user_rgm, rosto_serializado))
                conexao_bd.commit()

            cursor.fetchall()
            
            cursor.execute("SELECT count(*) total FROM facial_recognition f INNER JOIN users u ON f.user_rgm = u.rgm")
            total = cursor.fetchone()[0]
            resultado_label.config(text=f"Rosto cadastrado para o usuário: {user_rgm} fotos: {total}")
        elif not user_rgm:
            resultado_label.config(text="Por favor, insira o RGM do usuário")
        else:
            resultado_label.config(text="Nenhum rosto detectado para cadastro")
    else:
        resultado_label.config(text="Por favor, digite um RGM válido!")

def cadastrar_automatico():
    cadastro_automatico = not cadastro_automatico

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

cadastrar_a_botao = tk.Button(janela, text="Cadastrar Automatico", command=cadastrar_automatico)
cadastrar_a_botao.pack()

resultado_label = tk.Label(janela, text="")
resultado_label.pack()

atualizar_camera()

janela.mainloop()

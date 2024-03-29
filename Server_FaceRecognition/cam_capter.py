import serial
import numpy as np
import cv2

ser = serial.Serial('COM4', 115200)

largura = 320
altura = 240

cv2.namedWindow('Camera OV7670', cv2.WINDOW_NORMAL)

while True:
    raw_data = ser.read(largura * altura * 2)

    img_array = np.frombuffer(raw_data, dtype=np.uint8)
    img_array = img_array.reshape((altura, largura, 2))
    img = cv2.cvtColor(img_array, cv2.COLOR_BGR5652BGR)

    cv2.imshow('Camera OV7670', img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

ser.close()
cv2.destroyAllWindows()

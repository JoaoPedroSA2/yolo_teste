import cv2
from ultralytics import YOLO
import winsound
import pyttsx3
import time

model = YOLO("yolov8n.pt")

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 540)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 680)

engine = pyttsx3.init()

frequencia = 1000
duracao = 100

area_alerta = 40000

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)

    if len(results[0].boxes) > 0:
        boxes = results[0].boxes.xyxy
        confs = results[0].boxes.conf
        classes = results[0].boxes.cls

        index = int(confs.argmax())
        obj = model.names[int(classes[index])]
        x1,y1,x2,y2 = boxes[index]
        comprimento = x2 - x1
        altura = y2 - y1

        area = comprimento * altura

        calculo_proximidade = 0.7 * altura + 0.3 * (area ** 0.5)

        if calculo_proximidade > 300:
            engine.say(f"Alerta! {obj} muito próximo!")
            engine.runAndWait()
            
    frame_anotado = results[0].plot()

    cv2.imshow("YOLO Webcam", frame_anotado)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()

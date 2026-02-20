import cv2
from ultralytics import YOLO
import winsound
import time
from funcoes import *

model = YOLO("yolov8n.pt")

#-----configurações da webcam------
cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 540)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 680)
#---------------------

area_alerta = 40000

#sistema alerta e cooldown
ultimo_alerta = 0
cooldown_alerta = 5
ultimo_nivel = -1
#--------

#Configurações para direcao
largura_frame = 540
centro_tela = largura_frame / 2
#-----------------

# Loop principal
while True:
    ret, frame = cap.read() #Lê um frame da webcam
    if not ret:
        break

    results = model(frame) #Realiza detecção no frame

    if len(results[0].boxes) > 0:  #Verifica se há objetos detectados
        boxes = results[0].boxes.xyxy
        confs = results[0].boxes.conf
        classes = results[0].boxes.cls
        
        prioritario = objeto_prioritario(boxes, classes, model, centro_tela, largura_frame) #Encontra o objeto prioritário

        if prioritario:
            tempo_atual = time.time()  #Obtém o tempo atual

            if prioritario["nivel"] == 1 and tempo_atual - ultimo_alerta > cooldown_alerta:
                falar(f"Alerta: {prioritario['obj']} muito próximo {prioritario['direcao']}", nivel=2)  #Fala o alerta para objetos muito próximos
                ultimo_alerta = tempo_atual  #Atualiza o tempo do último alerta
            elif prioritario["nivel"] == 0 and tempo_atual - ultimo_alerta > cooldown_alerta:
                falar(f"Cuidado: {prioritario['obj']} perto {prioritario['direcao']}", nivel=1)  #Fala o alerta para objetos próximos
                ultimo_alerta = tempo_atual  #Atualiza o tempo do último alerta

    frame_anotado = results[0].plot() #Desenha as caixas delimitadoras e rótulos no frame

    cv2.imshow("YOLO Webcam", frame_anotado)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()

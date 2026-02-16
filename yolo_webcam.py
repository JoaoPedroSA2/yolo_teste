import cv2
from ultralytics import YOLO
import winsound
import time
import os
import threading

model = YOLO("yolov8n.pt")

#-----configurações da webcam------
cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 540)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 680)
#---------------------

area_alerta = 40000

#sistema alerta e cooldown
ultimo_alerta = 0
cooldown_alerta = 3 
#--------

def falar(texto):
    def run(): #Função para rodar a fala em uma thread separada
        comando = f'powershell -Command "Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'{texto}\');"'
        os.system(comando)

    threading.Thread(target=run,daemon=True).start() #Inicia a thread para falar o texto

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
        
        index = int(confs.argmax()) #Encontra o índice da caixa com a maior confiança
        obj = model.names[int(classes[index])]
        x1,y1,x2,y2 = boxes[index]
        comprimento = x2 - x1
        altura = y2 - y1

        area = comprimento * altura

        calculo_proximidade = 0.7 * altura + 0.3 * (area ** 0.5) #Cálculo de proximidade baseado na altura e área da caixa delimitadora

        tempo_atual = time.time()

        if calculo_proximidade > 300 and tempo_atual - ultimo_alerta > cooldown_alerta:  #Verifica se o objeto está próximo e se o cooldown do alerta passou
            falar(f"Alerta: {obj} detectado próximo!")  #Fala o alerta  
            ultimo_alerta = tempo_atual  #Atualiza o tempo do último alerta

    frame_anotado = results[0].plot() #Desenha as caixas delimitadoras e rótulos no frame

    cv2.imshow("YOLO Webcam", frame_anotado)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()

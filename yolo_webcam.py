import cv2
from ultralytics import YOLO
import winsound
import time
from funcoes import *

model = YOLO("yolov8n.pt")

#-----configurações da webcam------
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 540)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 680)
#---------------------

area_alerta = 40000

#sistema alerta e cooldown
ultimo_alerta = 0
cooldown_alerta = 5
#--------

#Configurações para direcao
largura_frame = 540
centro_tela = largura_frame / 2
#-----------------

#Variáveis auliares
ultimo_obj = None
ultimo_direcao = None
ultimo_nivel = None
lendo_texto = False

# Loop principal
while True:
    ret, frame = cap.read() #Lê um frame da webcam
    if not ret:
        break

    if not lendo_texto: 
        results = model(frame) #Realiza detecção no frame

        if len(results[0].boxes) > 0:  #Verifica se há objetos detectados
            boxes = results[0].boxes.xyxy
            confs = results[0].boxes.conf
            classes = results[0].boxes.cls
            
            prioritario = objeto_prioritario(boxes, classes, model, centro_tela, largura_frame) #Encontra o objeto prioritário

            if prioritario: 
                tempo_atual = time.time()  #Obtém o tempo atual

                #Armazena as informações do último objeto detectado para evitar alertas repetitivos
                atual_obj = prioritario['obj']
                atual_direcao = prioritario['direcao']
                atual_nivel = prioritario['nivel'] 

                mudou = (atual_obj != ultimo_obj or atual_direcao != ultimo_direcao or atual_nivel != ultimo_nivel) #Verifica se houve mudança no objeto, direção ou nível

                if mudou and tempo_atual - ultimo_alerta > cooldown_alerta:
                    if atual_nivel == 1:
                        falar(f"Alerta: {prioritario['obj']} muito próximo {prioritario['direcao']}")  #Fala o alerta para objetos muito próximos
                        ultimo_alerta = tempo_atual  #Atualiza o tempo do último alerta
                    elif atual_nivel == 0:
                        falar(f"Cuidado: {prioritario['obj']} perto {prioritario['direcao']}")  #Fala o alerta para objetos próximos
                        ultimo_alerta = tempo_atual  #Atualiza o tempo do último alerta
                
                    ultimo_obj = atual_obj
                    ultimo_direcao = atual_direcao
                    ultimo_nivel = atual_nivel
        
    if cv2.waitKey(1) & 0xff == ord('l'): #Ativa a leitura de texto quando a tecla 'l' for pressionada
        lendo_texto = True

        speaker.Speak("",3)  #Limpa a fila de fala para evitar sobreposição de mensagens

        falar("iniciando")  #Fala uma mensagem indicando que a leitura está sendo iniciada
        print("Iniciando leitura")
        texto_extraido = extrair_texto_imagem(frame)  #Extrai o texto do frame usando a função definida anteriormente
        
        if texto_extraido.strip():  #Verifica se o texto extraído não está vazio
            print(f"Texto encontrado: {texto_extraido}")
            falar(f"Texto encontrado {texto_extraido}")  #Fala o texto extraído da imagem
        else:
            print("Nenhum texto encontrado")  
            falar("Erro ao ler texto")  #Fala uma mensagem de erro caso não seja possível extrair o texto
        
        lendo_texto = False  #Desativa a leitura de texto após a conclusão
        ultimo_alerta = time.time() #Atualiza o tempo do último alerta para evitar alertas repetitivos após a leitura de texto

    if not lendo_texto:
        frame_anotado = results[0].plot() #Desenha as caixas delimitadoras e rótulos no frame

    cv2.imshow("YOLO Webcam", frame_anotado)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()


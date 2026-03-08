import threading
import os
import pytesseract
import cv2
import win32com.client 
import numpy as np
import torch


speaker = win32com.client.Dispatch("SAPI.SpVoice") #Configura o mecanismo de fala do Windows
lock_fala = threading.Lock() #Cria um lock para controlar o acesso à fala, evitando sobreposição de falas

caminho_pytesseract = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe" #Caminho para o executável do Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = caminho_pytesseract

def nivel_distancia(valor):
    if valor > 400:
        return 1 #muito perto
    elif valor > 320:
        return 0 # perto
    
def falar(texto):
    def run(): #Função para rodar a fala em uma thread separada
        with lock_fala: #Adquire o lock para garantir que apenas uma fala ocorra por vez
            speaker.Speak(texto) #Fala o texto usando o mecanismo de fala do Windows

    threading.Thread(target=run,daemon=True).start() #Inicia a thread para falar o texto

def direcao_objeto(centro_obj, centro_tela, largura_frame):
    margem = largura_frame * 0.15  # Define uma margem de 15% da largura do frame para considerar o centro
    
    if centro_obj < centro_tela - margem: 
        return "à esquerda"
    elif centro_obj > centro_tela + margem: 
        return "à direita"
    else:
        return "no centro"

def objeto_prioritario(boxes, classes, model, centro_tela, largura_frame, mapa_profundidade):
    objeto_detectado = [] #Lista para armazenar os objetos detectados com suas informações

    for i in range(len(boxes)): #Itera sobre os objetos detectados
        x1, y1, x2, y2 = boxes[i]
        obj = model.names[int(classes[i])]

        #informações de tamanho e profundidade
        comprimento = x2 - x1
        altura = y2 - y1
        area = comprimento * altura

        regiao = mapa_profundidade[int((y1+y2)/2), int((x1+x2)/2)] #Obtém a profundidade do centro do objeto a partir do mapa de profundidade
        profundidade = regiao.mean() #Calcula a média da profundidade na região do objeto para obter uma estimativa mais precisa

        #---------------------------------

        nivel = nivel_distancia(profundidade) #Determina o nível de proximidade com base na função definida anteriormente

        centro_obj = (x1 + x2) / 2 #Calcula o centro do objeto para determinar a direção

        direcao = direcao_objeto(centro_obj, centro_tela, largura_frame) #Determina a direção do objeto com base na função definida anteriormente

        objeto_detectado.append({ 
            "obj": obj,
            "nivel":nivel,
            "direcao": direcao,
            "profundidade": profundidade
        }) #Adiciona as informações do objeto detectado à lista

    if not objeto_detectado:
        return None
        
    mais_perto = min(objeto_detectado, key=lambda x: x["profundidade"]) #Encontra o objeto mais próximo com base na profundidade calculada
    return mais_perto #Retorna o objeto mais próximo com base na profundidade calculada

def extrair_texto_imagem(frame):
   
   imagem = frame

   cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY) #Converte a imagem para escala de cinza para melhorar a precisão do OCR
   cinza = cv2.convertScaleAbs(cinza, alpha=1, beta=8) #Ajusta o contraste e brilho da imagem para melhorar a legibilidade do texto
   cinza = cv2.GaussianBlur(cinza, (3, 3), 0) #Aplica um desfoque gaussiano para reduzir o ruído na imagem
   
   _, thresh = cv2.threshold(cinza, 150,255,cv2.THRESH_BINARY) #Aplica uma limiarização para destacar o texto na imagem
   
   texto = pytesseract.image_to_string(thresh, config='--psm 6') #Extrai o texto da imagem usando o Tesseract
   
   cv2.imshow("Imagem Original", imagem) #Exibe a imagem original para referência
   cv2.imshow("Texto Extraído", thresh) #Exibe a imagem processada para verificar o resultado do OCR

   return texto.strip() #Retorna o texto extraído, removendo espaços em branco extras

    

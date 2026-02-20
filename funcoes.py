import threading
import os


def nivel_distancia(valor):
    if valor > 400:
        return 1 #muito perto
    elif valor > 320:
        return 0 # perto
    
def falar(texto):
    def run(): #Função para rodar a fala em uma thread separada
        comando = f'powershell -Command "Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'{texto}\');"'
        os.system(comando)

    threading.Thread(target=run,daemon=True).start() #Inicia a thread para falar o texto

def direcao_objeto(centro_obj, centro_tela, largura_frame):
    margem = largura_frame * 0.15  # Define uma margem de 15% da largura do frame para considerar o centro
    
    if centro_obj < centro_tela - margem: 
        return "à esquerda"
    elif centro_obj > centro_tela + margem: 
        return "à direita"
    else:
        return "no centro"

def objeto_prioritario(boxes, classes, model, centro_tela, largura_frame):
    objeto_detectado = [] #Lista para armazenar os objetos detectados com suas informações

    for i in range(len(boxes)): #Itera sobre os objetos detectados
        x1, y1, x2, y2 = boxes[i]
        obj = model.names[int(classes[i])]

        #informações de tamanho e proximidade
        comprimento = x2 - x1
        altura = y2 - y1
        area = comprimento * altura

        proximidade = 0.7 * altura + 0.3 * (area ** 0.5) 
        #---------------------------------

        nivel = nivel_distancia(proximidade) #Determina o nível de proximidade com base na função definida anteriormente

        centro_obj = (x1 + x2) / 2 #Calcula o centro do objeto para determinar a direção

        direcao = direcao_objeto(centro_obj, centro_tela, largura_frame) #Determina a direção do objeto com base na função definida anteriormente

        objeto_detectado.append({ 
            "obj": obj,
            "nivel":nivel,
            "direcao": direcao,
            "proximidade": proximidade
        }) #Adiciona as informações do objeto detectado à lista

    if not objeto_detectado:
        return None
        
    mais_perto = max(objeto_detectado, key=lambda x: x["proximidade"])
    return mais_perto #Retorna o objeto mais próximo com base na proximidade calculada


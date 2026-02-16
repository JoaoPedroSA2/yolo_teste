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
    objeto_detectado = []

    for i in range(len(boxes)): 
        x1, y1, x2, y2 = boxes[i]
        obj = model.names[int(classes[i])]

        comprimento = x2 - x1
        altura = y2 - y1
        area = comprimento * altura

        proximidade = 0.7 * altura + 0.3 * (area ** 0.5)

        nivel = nivel_distancia(proximidade)

        centro_obj = (x1 + x2) / 2

        direcao = direcao_objeto(centro_obj, centro_tela, largura_frame)

        objeto_detectado.append({
            "obj": obj,
            "nivel":nivel,
            "direcao": direcao,
            "proximidade": proximidade
        })

        if not objeto_detectado:
            return None
        
        mais_perto = max(objeto_detectado, key=lambda x: x["proximidade"])
        return mais_perto


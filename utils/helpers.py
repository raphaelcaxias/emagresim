# utils/helpers.py
from datetime import datetime
from utils.constants import MENSAGENS_AVATAR

def mensagem_bom_dia():
    hora = datetime.now().hour
    if hora < 12:
        return "🌅 Bom dia! Hoje é um novo começo."
    elif hora < 18:
        return "🌤️ Boa tarde! Continue firme."
    return "🌙 Boa noite! Amanhã é outro dia."

def calcular_imc(peso, altura):
    if altura <= 0:
        return 0
    return peso / (altura ** 2)

def calcular_avatar(percentual):
    for limite in [100, 75, 50, 25, 0]:
        if percentual >= limite:
            return MENSAGENS_AVATAR[limite]
    return MENSAGENS_AVATAR[0]

def formatar_data(data):
    return data.strftime("%d/%m/%Y")

def normalizar_altura(valor):
    try:
        altura = float(str(valor).replace(",", "."))
        if altura > 3:
            altura = altura / 100
        return round(altura, 2)
    except:
        return 1.75

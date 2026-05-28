# utils/helpers.py
from datetime import datetime
import locale

def calcular_imc(peso: float, altura: float) -> float:
    if altura <= 0:
        return 0
    return peso / (altura ** 2)

def calcular_avatar(percentual: float):
    if percentual >= 100:
        return "🏆", "Conquista! Você atingiu sua meta mensal!"
    elif percentual >= 75:
        return "⚡", "Quase lá! Continue firme."
    elif percentual >= 50:
        return "🌱", "Metade do caminho. Você está evoluindo."
    elif percentual >= 25:
        return "🔥", "Primeiros resultados! Continue assim."
    else:
        return "🌅", "Todo recomeço é uma semente. Confie no processo."

def mensagem_bom_dia():
    hora = datetime.now().hour
    if hora < 12:
        return "🌅 Bom dia! Hoje é um novo começo."
    elif hora < 18:
        return "🌤️ Boa tarde! Continue firme."
    return "🌙 Boa noite! Amanhã é outro dia."

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

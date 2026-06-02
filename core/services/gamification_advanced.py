import random
from datetime import datetime

class GamificationAdvanced:
    @staticmethod
    def calcular_nivel(xp_total: int) -> dict:
        nivel = int((xp_total / 100) ** 0.5) + 1
        xp_atual = (nivel - 1) ** 2 * 100
        xp_proximo = nivel ** 2 * 100
        progresso = ((xp_total - xp_atual) / (xp_proximo - xp_atual)) * 100 if xp_proximo > xp_atual else 0
        
        return {
            "nivel": nivel,
            "xp_total": xp_total,
            "progresso": min(100, progresso)
        }
    
    @staticmethod
    def gerar_desafio_semanal():
        desafios = [
            {"titulo": "7 Dias de Registro", "xp": 100},
            {"titulo": "Zero Calorias Noturnas", "xp": 80},
            {"titulo": "Proteína em Alta", "xp": 70},
        ]
        semana = datetime.now().isocalendar()[1]
        random.seed(semana)
        return random.choice(desafios)

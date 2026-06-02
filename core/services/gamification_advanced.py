import random
from datetime import datetime

class GamificationAdvanced:
    DESAFIOS_SEMANAIS = [
        {"id": "d1", "titulo": "7 Dias de Registro", "xp": 100, "desc": "Registre todas as refeições por 7 dias"},
        {"id": "d2", "titulo": "Zero Calorias Noturnas", "xp": 80, "desc": "Não coma após 20h por 3 dias"},
        {"id": "d3", "titulo": "Proteína em Alta", "xp": 70, "desc": "Consuma proteína em todas as refeições"},
        {"id": "d4", "titulo": "Hidratação Total", "xp": 50, "desc": "Beba 2L de água por dia"},
        {"id": "d5", "titulo": "Meta Atingida", "xp": 150, "desc": "Fique dentro da meta calórica por 5 dias"},
    ]
    
    CONQUISTAS_EXPANDIDAS = [
        {"name": "first_login", "title": "🎉 Primeiro Acesso", "xp": 10},
        {"name": "first_meal", "title": "🍽️ Primeira Refeição", "xp": 20},
        {"name": "week_streak", "title": "📅 7 Dias Seguidos", "xp": 100},
        {"name": "month_streak", "title": " 30 Dias Seguidos", "xp": 500},
        {"name": "hundred_meals", "title": " 100 Refeições", "xp": 200},
        {"name": "weight_tracked", "title": "⚖️ 10 Pesagens", "xp": 75},
        {"name": "goal_reached", "title": "🎯 Meta Atingida", "xp": 1000},
    ]
    
    @staticmethod
    def calcular_nivel(xp_total: int) -> dict:
        """Calcula nível baseado em XP (fórmula progressiva)"""
        nivel = int((xp_total / 100) ** 0.5) + 1
        xp_atual_nivel = (nivel - 1) ** 2 * 100
        xp_proximo_nivel = nivel ** 2 * 100
        progresso = ((xp_total - xp_atual_nivel) / (xp_proximo_nivel - xp_atual_nivel)) * 100
        
        titulos = {
            1: "Iniciante", 3: "Determinado", 5: "Disciplinado",
            8: "Atleta", 12: "Elite", 20: "Lenda"
        }
        titulo = "Iniciante"
        for lvl, t in sorted(titulos.items()):
            if nivel >= lvl:
                titulo = t
        
        return {
            "nivel": nivel,
            "titulo": titulo,
            "xp_total": xp_total,
            "xp_atual": xp_total - xp_atual_nivel,
            "xp_proximo": xp_proximo_nivel - xp_atual_nivel,
            "progresso": min(100, progresso)
        }
    
    @staticmethod
    def gerar_desafio_semanal() -> dict:
        """Retorna um desafio aleatório da semana"""
        semana_atual = datetime.now().isocalendar()[1]
        random.seed(semana_atual)
        return random.choice(GamificationAdvanced.DESAFIOS_SEMANAIS)
    
    @staticmethod
    def xp_por_refeicao(tipo: str) -> int:
        """XP baseado no tipo de ação"""
        xps = {
            "refeicao": 10,
            "combo": 15,
            "pesagem": 8,
            "perfil_atualizado": 5,
            "conquista": 50
        }
        return xps.get(tipo, 5)
